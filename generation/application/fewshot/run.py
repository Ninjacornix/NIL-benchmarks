"""Preregistered exposure adapter. Reuse frozen transport, repairs, budget and oracle."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
APP = HERE.parent
sys.path.insert(0, str(APP))
spec = importlib.util.spec_from_file_location('frozen_application', APP / 'run.py')
frozen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frozen)
SUITE = frozen.core.SUITE
CORPUS = SUITE / 'corpora/application-v5'
DEFINITION = HERE / 'experiment.json'


def examples():
    """Check the committed selection and hashes; never adapt selection to a task."""
    import re
    plan = json.loads(DEFINITION.read_text())
    tasks = json.loads((CORPUS / 'tasks.json').read_text())['tasks']
    selected = []
    rule = plan['selection']
    for category in rule['categories']:
        eligible = [t for t in tasks if t['category'] == category
                    and t['nil_status'] == 'supported' and not t['adaptation_overlap']
                    and t['id'] not in rule['excluded']
                    and set(re.findall(r'!([a-z0-9]+)', (CORPUS / 'programs' / (t['id'] + '.nil')).read_text())) <= set(rule['allowed_intrinsics'])]
        selected.append(min(eligible, key=lambda t: t['id']))
    assert [t['id'] for t in selected] == [x['task'] for x in plan['examples']]
    evaluated = json.loads((APP / 'experiment.json').read_text())['task_ids']
    assert not set(evaluated) & {t['id'] for t in selected}
    result = []
    for task, entry in zip(selected, plan['examples']):
        path = SUITE / entry['source']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256']
        result.append((task, path.read_text()))
    assert len(result) == rule['count']
    return result


def prompt(language, task):
    assert language == 'expr-v5'
    # Keep the control intact, including reference, generic copy and final contract.
    addition = '\nAdditional verified worked examples (independent tasks; do not copy their answers for the evaluated task):\n'
    for example, source in examples():
        addition += '\nExample task: ' + example['prompt'] + '\nComplete NIL source:\n' + source
    control = frozen.prompt(language, task)
    prefix, suffix = control.split('\nTask: ', 1)
    return prefix + addition + '\nTask: ' + suffix


def selected_preflight(output):
    """Same reference/native oracle, corpus's own unchanged expected bytes."""
    import tempfile
    sys.path.insert(0, str(CORPUS))
    from oracles import expected
    goldens = json.loads((CORPUS / 'goldens.json').read_text())
    rows = []
    original = frozen.oracle.expected
    frozen.oracle.expected = expected
    try:
        with tempfile.TemporaryDirectory(prefix='nil-fewshot-preflight-') as directory:
            for task, source in examples():
                golden = goldens[task['id']]
                assert expected(task['id'], bytes.fromhex(golden['input'])) == bytes.fromhex(golden['output'])
                task = task | {'inputs': task['inputs'] + [golden['input']]}
                folder = Path(directory) / task['id']; folder.mkdir()
                verdict = frozen.oracle.evaluate(source, 'expr-v5', task, folder)
                if not verdict['semantic_ok']:
                    raise RuntimeError('Selected example failed preflight: ' + task['id'] + str(verdict))
                rows.append(dict(task=task['id'], **verdict))
    finally:
        frozen.oracle.expected = original
    (output / 'examples-preflight.json').write_text(json.dumps(rows, indent=2) + '\n')
    print('Selected examples verified:', len(rows), 'reference checks', sum(x['tests_passed'] for x in rows), 'native O0/O2 checks', sum(x['native_tests_passed'] for x in rows), flush=True)


def run(output, endpoint, mock=False):
    output = output.expanduser().resolve()
    if output.exists():
        raise ValueError('Choose a fresh output directory')
    if any(output == p or p in output.parents for p in [frozen.core.ROOT, SUITE]):
        raise ValueError('Output must be outside both repositories')
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError('Use pinned Python 3.12')
    plan = json.loads(DEFINITION.read_text())
    definition = json.loads((APP / 'experiment.json').read_text())
    examples()
    # Check every model first. No partial matrix caused by a missing second model.
    if not mock:
        tags = {m['name']: m['digest'] for m in frozen.core.post(endpoint, '/api/tags')['models']}
        for name, digest in definition['models'].items():
            if tags.get(name) != digest:
                raise ValueError('Frozen model missing or digest mismatch: ' + name)
    frozen.oracle.prepare()
    output.mkdir(parents=True)
    (output / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
    selected_preflight(output)
    extra = [Path(__file__), DEFINITION, CORPUS / 'tasks.json', CORPUS / 'goldens.json', CORPUS / 'oracles.py']
    extra += [SUITE / x['source'] for x in plan['examples']]
    # Preserve the original language rotation within the control. Fixed model order.
    for index, (model, digest) in enumerate(definition['models'].items()):
        for condition in plan['conditions']:
            config = definition | dict(models={model: digest}, condition=condition,
                                       exposure_definition=str(DEFINITION.relative_to(SUITE)))
            if condition == 'fewshot':
                config['languages'] = ['expr-v5']
            factory = frozen.prompt if condition == 'control' else prompt
            frozen.run(output / f'{index}-{condition}', endpoint, mock,
                       definition=config, prompt_factory=factory, extra_sources=extra)
    report(output)


def modes(attempts):
    return dict(attempts=len(attempts),
                parse_pass=sum(r.get('parse_ok') is True for r in attempts),
                typecheck_pass=sum(r.get('typecheck_ok') is True for r in attempts),
                compile_pass=sum(r.get('compile_ok') is True for r in attempts),
                parse_unknown=sum(r.get('parse_ok') is None for r in attempts),
                typecheck_unknown=sum(r.get('typecheck_ok') is None for r in attempts),
                compile_unknown=sum(r.get('compile_ok') is None for r in attempts),
                outcomes=dict(Counter('correct' if r['semantic_ok'] else r.get('failure_reason', 'unknown') for r in attempts)))


def report(root):
    trials = []; attempts = []; configs = []
    for folder in sorted(root.glob('[01]-*')):
        config, ts, ats = frozen.audit(folder)
        configs.append(config)
        condition = config['condition']
        for t in ts:
            trials.append(t | dict(condition=condition))
        for a in ats:
            a = a | dict(condition=condition, artifact=str(folder.name + '/' + a['trial_id']))
            # Reconstruct the exact committed first prompt, not just its stored hash.
            if a['attempt'] == 0:
                task = next(t for t in json.loads((APP / 'tasks.json').read_text())['tasks'] if t['id'] == a['task'])
                request = json.loads((folder / a['trial_id'] / 'request-0.json').read_text())
                factory = frozen.prompt if condition == 'control' else prompt
                assert request['messages'] == [{'role': 'user', 'content': factory(a['profile'], task)}]
            attempts.append(a)
    assert len(configs) == 4, 'Incomplete condition/model matrix'
    assert len({c['condition'] for c in configs}) == 2
    mock = all(c['mock'] for c in configs)
    assert all(c['mock'] == mock for c in configs)
    assert len(trials) == 72
    aggregates = []; per_task = []; repeats = []; intervals = []
    for condition in ['control', 'fewshot']:
        rows = [r for r in trials if r['condition'] == condition]
        for group in frozen.core.summary(rows):
            matches = [a for a in attempts if a['condition'] == condition and a['model'] == group['model'] and a['profile'] == group['profile']]
            aggregates.append(group | dict(condition=condition, validity=modes(matches), final_outcomes=modes([a for a in matches if a['attempt'] == max(x['attempt'] for x in matches if x['trial_id'] == a['trial_id'])])))
        for task in configs[0]['task_ids']:
            for group in frozen.core.summary([r for r in rows if r['task'] == task]):
                matches = [a for a in attempts if a['condition'] == condition and a['model'] == group['model'] and a['profile'] == group['profile'] and a['task'] == task]
                per_task.append(group | dict(condition=condition, task=task, validity=modes(matches)))
        for seed in configs[0]['seeds']:
            repeats += [r | dict(condition=condition, seed=seed) for r in frozen.core.summary([t for t in rows if t['seed'] == seed])]
    for model in {r['model'] for r in trials}:
        paired = [r | dict(profile=r['condition']) for r in trials if r['model'] == model and r['profile'] == 'expr-v5']
        out = frozen.core.paired_interval(paired, model, 'control', 'fewshot')
        combined = [r | dict(output_tokens=r['output_tokens'] + r['input_tokens'] if r['output_tokens'] is not None and r['input_tokens'] is not None else None) for r in paired]
        intervals.append(dict(model=model, output=out, total=frozen.core.paired_interval(combined, model, 'control', 'fewshot')))
    result = dict(mock=mock, trials=len(trials), attempts=len(attempts), aggregate=aggregates,
                  per_task=per_task, per_seed=repeats, paired_intervals=intervals,
                  frozen_models=json.loads((APP / 'experiment.json').read_text())['models'],
                  source_hashes=configs[0]['source_hashes'])
    (root / 'analysis.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Exposure audit passed:', len(trials), 'trials;', len(attempts), 'attempts;', 'STUB ONLY' if mock else 'REAL MODEL USAGE', flush=True)
    for row in aggregates:
        print(json.dumps(row), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--endpoint', default='http://127.0.0.1:11434')
    parser.add_argument('--mock', action='store_true')
    parser.add_argument('--report-only', action='store_true')
    args = parser.parse_args()
    if args.report_only:
        report(args.output)
    else:
        run(args.output, args.endpoint, args.mock)
