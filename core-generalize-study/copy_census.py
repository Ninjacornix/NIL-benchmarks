"""Part A1 physical-copy census, classified against reference-semantic observations.

Every counted event carries a monotonic source version and a ledger group. An
unknown kind aborts the census rather than defaulting to AVOIDABLE. The
instrumented and ordinary paths must agree on exit code, stdout, output bytes and
preserved input before any program's events are accepted.

Two metrics are published for the PAYLOAD_COPY group:

``strict``       REQUIRED if the source version has any later observation.
``payload_only`` REQUIRED only if a later observation reads element payload.

AVOIDABLE is "no later observation under this metric", not a proof that the copy
can be removed; scheduling can also remove copies inside the REQUIRED set.
"""
import argparse, csv, hashlib, json, os, subprocess, sys, tempfile, time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUITE = HERE.parent
ROOT = SUITE.parent
sys.path.insert(0, str(HERE))
import copy_ledger
sys.path.insert(0, str(SUITE))
from resource_outcomes import native_code

NEETCODE = SUITE / 'corpora/neetcode150'
APPLICATION = SUITE / 'corpora/application-v5'


def fuzz_environment(row):
    """Only fixture state: never inherit ambient host variables or entropy."""
    env = {'NIL_COPY_FUZZ': '1', 'NIL_CENSUS_SEED': row['seed'],
           'NIL_RANDOM_SEED': '01' if row['invalid_seed'] == 'true' else row['seed'],
           'NIL_FUZZ_PRESENT': 'abc 12', 'NIL_FUZZ_EMPTY': '',
           'NIL_FUZZ_RAW': bytes([255, 128, 120]), 'NIL_FUZZ_LARGE': 'x' * 1024}
    if row['denied'] == 'true':
        env['NIL_DENY_HOST_IO'] = '1'
    if row['invalid_seed'] == 'true':
        env['NIL_CENSUS_INVALID_SEED'] = '1'
    return env


def prepare_fuzz_directories(work):
    for suffix, count in (('.entries', 16), ('.large', 1024), ('.empty', 0)):
        folder = work / ('input.bin' + suffix)
        if not folder.exists():
            folder.mkdir()
            for i in reversed(range(count)):
                (folder / f'entry-{i:04}-é').write_bytes(b'')
            if count == 16:
                (folder / 'subdirectory').mkdir()
    # The unreadable fixture is genuinely unreadable for this unprivileged run.
    folder = work / 'input.bin.unreadable'
    if not folder.exists():
        folder.mkdir()
        folder.chmod(0)


def read_trace(path):
    if not path.exists():
        return []
    with path.open() as handle:
        return list(csv.DictReader(handle, delimiter='\t'))


def blank(group_names):
    return {g: {'events': 0, 'bytes': 0,
                'strict': {'REQUIRED': 0, 'AVOIDABLE': 0},
                'strict_bytes': {'REQUIRED': 0, 'AVOIDABLE': 0},
                'payload_only': {'REQUIRED': 0, 'AVOIDABLE': 0},
                'payload_only_bytes': {'REQUIRED': 0, 'AVOIDABLE': 0}}
            for g in group_names}


def accumulate(into, events, kinds):
    for event in events:
        kind = event['kind']
        group = copy_ledger.group(kind)          # raises on UNCLASSIFIED
        assert int(event['version']) > 0, ('event without a source version', event)
        size = int(event['bytes'])
        slot = into[group]
        slot['events'] += 1
        slot['bytes'] += size
        for metric, column in (('strict', 'any_observation'), ('payload_only', 'payload_observation')):
            slot[metric][event[column]] += 1
            slot[metric + '_bytes'][event[column]] += size
        kinds[kind] += 1


def run_pair(ordinary, instrumented, source, work, data, trace, manifests=(), environment=None,
             fuzz=False):
    """Run both helpers on one fixture and require identical observable behaviour."""
    results = {}
    for label, helper in (('ordinary', ordinary), ('instrumented', instrumented)):
        for name in ('output.bin', 'stdout.bin'):
            (work / name).unlink(missing_ok=True)
        (work / 'input.bin').write_bytes(data)
        env = {'PATH': os.environ['PATH'], 'HOME': str(work), 'TMPDIR': str(work),
               'PYTHONDONTWRITEBYTECODE': '1', **(environment or {})}
        if label == 'instrumented':
            env['NIL_COPY_TRACE_FILE'] = str(trace)
            trace.unlink(missing_ok=True)
        done = subprocess.run([str(helper), str(source), 'input.bin', 'output.bin', 'stdout.bin',
                               *map(str, manifests)],
                              cwd=work, env=env, capture_output=True, timeout=300)
        results[label] = (done.returncode, done.stdout, done.stderr.split(b'NIL_REFERENCE_PROFILE')[0],
                          (work / 'output.bin').read_bytes() if (work / 'output.bin').exists() else None,
                          (work / 'stdout.bin').read_bytes() if (work / 'stdout.bin').exists() else None,
                          (work / 'input.bin').read_bytes())
    assert results['ordinary'] == results['instrumented'], ('instrumented divergence', source.name,
                                                            results['ordinary'][:3], results['instrumented'][:3])
    if fuzz:
        code = results['ordinary'][1].decode().strip().split('\t')
        assert len(code) == 2 and code[0] == 'RESULT', ('missing execution result', results)
        assert code[1] != 'E006', 'fuzz census entry still has wrong arity/types'
        return read_trace(trace), code[1], results['ordinary']
    return read_trace(trace)


def native_census(helpers, source, work, data, trace, reference_trace, max_events, manifests=(),
                  environment=None, expected=None):
    """Native O0 mechanism census joined to reference versions. Fail-closed.

    O0 keeps every runtime copy call the emitter decided to make, which is the
    decision this census measures. It deliberately does not claim which copies
    survive LLVM's O2 pipeline.
    """
    env = {'PATH': os.environ['PATH'], 'HOME': str(work), 'TMPDIR': str(work),
           'NIL_CLANG': str(HERE / 'copy_clang.py'),
           'NIL_NATIVE_COPY_TRACE_FILE': str(trace)}
    env.update(environment or {})
    binary = work / 'native-instrumented'
    trace.unlink(missing_ok=True)
    built = subprocess.run([str(helpers / 'native-copy-build'), str(source), str(binary),
                            'bounded' if expected is not None else 'unbounded', *map(str, manifests)],
                           cwd=work, env=env, capture_output=True, timeout=600)
    if built.stdout.strip() != b'BUILD\tOK':
        return None, 'instrumented build failed: ' + built.stdout.decode(errors='replace')[:160]
    (work / 'input.bin').write_bytes(data)
    if expected is not None:
        (work / 'output.bin').unlink(missing_ok=True)
    arguments = ['[3,-2,9]', 'abc 12', 'input.bin', 'output.bin'] if expected is not None else ['input.bin', 'output.bin']
    run = subprocess.run([str(binary), *arguments], cwd=work, env=env,
                         capture_output=True, timeout=600)
    if expected is not None:
        code = native_code(run)
        reference_code = expected[1].decode().strip().split('\t')[1]
        if code in ('E008', 'E013') or reference_code in ('E008', 'E013'):
            return None, f'resource-inconclusive reference={reference_code} native={code}'
        assert code == reference_code, ('native diagnostic divergence', source, code, expected[:3])
        assert run.stdout == expected[4], ('native stdout divergence', source)
        assert ((work / 'output.bin').read_bytes() if (work / 'output.bin').exists() else None) == expected[3], ('native output divergence', source)
        assert (work / 'input.bin').read_bytes() == expected[5], ('native input changed', source)
    if expected is None:
        code = native_code(run)
        if code in ('E008', 'E013'):
            return None, f'resource-inconclusive native={code}'
        assert code == 'OK', ('native census failed', source, run.stderr)
    events = read_trace(trace)
    if not events:
        return [], 'native exit %d, no instrumented copy reached' % run.returncode
    if len(events) > max_events:
        return None, f'native trace {len(events)} events exceeds --native-max-events {max_events}'
    # The native trace is small, so stream the large reference site file once and
    # keep only the rows this trace needs. Bounded memory, no event cap on the
    # reference side, so the largest qualification fixtures stay in the census.
    needed = {(int(r['site']), int(r['occurrence'])) for r in events}
    sites = {}
    sites_path = reference_trace.with_suffix('.sites.tsv')
    if not sites_path.exists():
        return None, 'reference site trace missing'
    with sites_path.open() as handle:
        for row in csv.DictReader(handle, delimiter='\t'):
            key = (int(row['site']), int(row['occurrence']))
            if key in needed:
                sites[key] = (int(row['clock']), [int(v) for v in row['versions'].split(',')])
    versions = {int(r['version']): (int(r['last_payload']), int(r['last_metadata']))
                for r in read_trace(reference_trace.with_suffix('.versions.tsv'))}
    joined = []
    for row in events:
        key = (int(row['site']), int(row['occurrence']))
        if key not in sites:
            return None, f'unjoinable native site {key}'
        clock, roles = sites[key]
        role = int(row['role'])
        if not 1 <= role <= len(roles):
            return None, f'unknown operand role {role} at site {key}'
        version = roles[role - 1]
        if version not in versions:
            return None, f'unknown source version {version} at site {key}'
        payload, metadata = versions[version]
        joined.append({'kind': row['kind'], 'bytes': row['bytes'], 'version': str(version),
                       'any_observation': 'REQUIRED' if max(payload, metadata) > clock else 'AVOIDABLE',
                       'payload_observation': 'REQUIRED' if payload > clock else 'AVOIDABLE'})
    return joined, ('native exit %d' % run.returncode)


def neetcode_programs(which):
    sys.path.insert(0, str(NEETCODE))
    import fixtures, verify as harness
    folder = (HERE / 'natural') if which == 'natural' else (NEETCODE / 'programs')
    for task in harness.tasks():
        path = folder / (task['id'] + '.nil')
        if path.exists():
            yield task['id'], path, list(fixtures.cases(task))


def application_programs():
    sys.path.insert(0, str(APPLICATION))
    sys.path.insert(0, str(SUITE / 'generation/application'))
    from external_suite import load_tasks, load_goldens
    goldens = load_goldens()
    for frozen in load_tasks('all'):
        if frozen['nil_status'] == 'unsupported':
            continue
        path = APPLICATION / 'programs' / (frozen['id'] + '.nil')
        golden = goldens[frozen['id']]
        inputs = [bytes.fromhex(v) for v in frozen['inputs']] + [bytes.fromhex(golden['input'])]
        environments = frozen.get('environments', [{}] * len(frozen['inputs'])) + [golden.get('environment', {})]
        yield frozen['id'], path, list(zip([f'fixture-{i}' for i in range(len(inputs))], inputs, environments))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--overlay', type=Path, required=True)
    parser.add_argument('--scope', required=True,
                        help='application | neetcode-natural | neetcode-tuned | fuzz:<seed>')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--limit', type=int, default=0, help='development subset only')
    parser.add_argument('--program', action='append', default=[],
                        help='explicit program subset for instrumented reruns; repeatable')
    parser.add_argument('--native-max-events', type=int, default=5000000,
                        help='skip the native join when the native trace itself is larger')
    parser.add_argument('--native', action='store_true',
                        help='also run the native O0 mechanism census and join it to reference versions')
    args = parser.parse_args()
    out = args.output.expanduser().resolve()
    if out.is_relative_to(ROOT):
        parser.error('raw census output belongs outside the checkout')
    helpers = args.overlay / 'helper/target/release'
    ordinary_core = ROOT / 'target/release/examples/core_check'
    ordinary_app = ROOT / 'target/release/examples/application_check'

    groups = copy_ledger.groups()
    totals = blank(groups)
    kinds = defaultdict(int)
    native_totals = blank(groups)
    native_kinds = defaultdict(int)
    per_program, skipped = [], []
    outcomes = defaultdict(int)
    scope = args.scope
    started = time.time()

    with tempfile.TemporaryDirectory(prefix='nil-copy-census-') as directory:
        base = Path(directory)
        trace = base / 'trace.tsv'
        if scope == 'application':
            jobs = [(name, path, cases, ordinary_app, helpers / 'reference-application')
                    for name, path, cases in application_programs()]
        elif scope in ('neetcode-natural', 'neetcode-tuned'):
            jobs = [(name, path, [(f, d, {}) for f, d in cases], ordinary_core, helpers / 'reference-profile')
                    for name, path, cases in neetcode_programs(scope.split('-')[1])]
        elif scope.startswith('fuzz:'):
            seed = scope.split(':', 1)[1]
            folder = base / 'fuzz'
            subprocess.run([str(helpers / 'fuzz-sources'), seed, str(folder)], check=True,
                           capture_output=True)
            # One deterministic census fixture, recorded as the census's own input
            # rather than the fuzz oracle's randomized host.
            fixture = bytes(range(256)) * 4
            metadata = list(csv.DictReader((folder / 'fixtures.tsv').open(), delimiter='\t'))
            jobs = []
            for row in metadata:
                env = fuzz_environment(row)
                path = folder / f"family-{int(row['index']):04}.nil"
                jobs.append((path.stem, path, [('census-fixture', fixture, env)],
                             args.overlay / 'ordinary-fuzz/target/release/ordinary-fuzz', helpers / 'reference-fuzz'))
        else:
            parser.error('unknown scope')
        if args.program:
            wanted = set(args.program)
            missing = wanted - {job[0] for job in jobs}
            if missing:
                parser.error('unknown selected programs: ' + ', '.join(sorted(missing)))
            jobs = [job for job in jobs if job[0] in wanted]
        if args.limit:
            jobs = jobs[:args.limit]

        for name, path, cases, ordinary, instrumented in jobs:
            program = blank(groups)
            program_kinds = defaultdict(int)
            native_program = blank(groups)
            native_program_kinds = defaultdict(int)
            native_notes = []
            fixtures_done = 0
            work = base / 'work'
            work.mkdir(exist_ok=True)
            if scope.startswith('fuzz:'):
                prepare_fuzz_directories(work)
            try:
                for label, data, environment in cases:
                    events = run_pair(ordinary, instrumented, path.resolve(), work, data, trace,
                                      environment=environment, fuzz=scope.startswith('fuzz:'))
                    expected = None
                    if scope.startswith('fuzz:'):
                        events, code, expected = events
                        outcomes[code] += 1
                    accumulate(program, events, program_kinds)
                    accumulate(totals, events, kinds)
                    fixtures_done += 1
                    if args.native and (not environment or scope.startswith('fuzz:')):
                        joined, note = native_census(helpers, path.resolve(), work, data,
                                                     base / 'native.tsv', trace,
                                                     args.native_max_events, environment=environment,
                                                     expected=expected)
                        if joined is None:
                            native_notes.append({'fixture': label, 'reason': note})
                        else:
                            accumulate(native_program, joined, native_program_kinds)
                            accumulate(native_totals, joined, native_kinds)
            except subprocess.TimeoutExpired:
                skipped.append({'program': name, 'reason': 'reference timeout at 300 s',
                                'fixtures_completed': fixtures_done})
                print(f'{name} TIMEOUT after {fixtures_done} fixtures', flush=True)
                continue
            payload = program[copy_ledger.PAYLOAD_COPY]
            per_program.append({
                'program': name,
                'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'fixtures': fixtures_done,
                'groups': program,
                'kinds': dict(program_kinds),
                'native': ({'groups': native_program, 'kinds': dict(native_program_kinds),
                            'unjoinable': native_notes} if args.native else None),
            })
            extra = ''
            if args.native:
                extra = (f" native_payload={native_program[copy_ledger.PAYLOAD_COPY]['events']:7d}"
                         f" unjoinable={len(native_notes)}")
            print(f"{name:52} fixtures={fixtures_done:3d} payload_events={payload['events']:9d} "
                  f"payload_bytes={payload['bytes']:12d} "
                  f"strict_avoidable={payload['strict']['AVOIDABLE']:8d}" + extra, flush=True)

    def worst(metric, key):
        rows = sorted(per_program,
                      key=lambda r: -r['groups'][copy_ledger.PAYLOAD_COPY][metric][key])
        return [{'program': r['program'],
                 'avoidable_bytes': r['groups'][copy_ledger.PAYLOAD_COPY][metric][key],
                 'payload_bytes': r['groups'][copy_ledger.PAYLOAD_COPY]['bytes']}
                for r in rows[:10] if r['groups'][copy_ledger.PAYLOAD_COPY][metric][key]]

    report = {
        'schema': 1,
        'scope': scope,
        'selected_programs': sorted(set(args.program)),
        'path': 'reference',
        'programs': len(per_program),
        'skipped': skipped,
        'elapsed_s': round(time.time() - started, 1),
        'ledger': copy_ledger.receipt(),
        'overlay_manifest_sha256': hashlib.sha256((args.overlay / 'MANIFEST.json').read_bytes()).hexdigest(),
        'totals': totals,
        'kinds': dict(kinds),
        'executed_codes': dict(outcomes),
        'inconclusive_native_fixtures': [{'program': r['program'], **n}
            for r in per_program if r['native'] for n in r['native']['unjoinable']
            if n['reason'].startswith('resource-inconclusive')],
        'fixture_contract': ({'parameters': ['v:[3,-2,9]', 's:abc 12', 's:input.bin', 's:output.bin'],
                              'input_sha256': hashlib.sha256(bytes(range(256)) * 4).hexdigest(),
                              'steps': 100000, 'call_depth': 256, 'memory_bytes': 67108864,
                              'resource_policy': 'clean E008/E013 inconclusive; excluded from native joins',
                              'host': 'fixed census fixture, not randomized campaign Host',
                              'native_observables_compared': ['diagnostic code', 'stdout', 'output file', 'preserved input']}
                             if scope.startswith('fuzz:') else None),
        'native': ({'path': 'native O0 ' + ('bounded' if scope.startswith('fuzz:') else 'unbounded') + ', mechanism census joined to reference versions',
                    'caveat': 'O0 preserves the emitter\'s copy decisions. It does not claim which '
                              'copies survive the O2 pipeline.',
                    'totals': native_totals, 'kinds': dict(native_kinds)} if args.native else None),
        'worst_strict_avoidable_bytes': worst('strict_bytes', 'AVOIDABLE'),
        'worst_payload_only_avoidable_bytes': worst('payload_only_bytes', 'AVOIDABLE'),
        'per_program': per_program,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + '\n')
    payload = totals[copy_ledger.PAYLOAD_COPY]
    print('CENSUS ' + json.dumps({
        'scope': scope, 'programs': len(per_program), 'skipped': len(skipped),
        'executed_codes': dict(outcomes),
        'inconclusive_native_fixtures': [{'program': r['program'], **n}
            for r in per_program if r['native'] for n in r['native']['unjoinable']
            if n['reason'].startswith('resource-inconclusive')],
        'payload_events': payload['events'], 'payload_bytes': payload['bytes'],
        'strict': payload['strict'], 'payload_only': payload['payload_only'],
        'other_groups': {g: totals[g]['events'] for g in groups if g != copy_ledger.PAYLOAD_COPY},
        'native_payload': (native_totals[copy_ledger.PAYLOAD_COPY] if args.native else None),
    }))


if __name__ == '__main__':
    main()
