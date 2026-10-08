"""Verify authored references, using the existing generation evaluator/native harness."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
SUITE = HERE.parents[1]
sys.path.insert(0, str(SUITE / 'generation' / 'application'))
import oracle as application
from oracles import expected as original_expected
from external_suite import load_tasks, load_goldens, external_expected

def expected(task, data, environment=None):
    return external_expected(task, data) if task.startswith("ex_") else original_expected(task, data, environment)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint():
    paths = [HERE / 'tasks.json', HERE / 'oracles.py', HERE / 'verify.py', HERE / 'driver.cpp', HERE / 'goldens.json']
    paths += sorted((HERE / 'programs').glob('*'))
    paths += [HERE / 'SUPPORT.json', HERE / 'external_suite.py', HERE / 'external/build_manifest.py'] + sorted((HERE / 'external').glob('*.json'))
    paths += [SUITE / 'generation/application' / name for name in ['oracle.py', 'python_driver.py']]
    paths += [SUITE / 'helpers/application_check.rs'] + sorted((HERE / 'algorithms').glob('*'))
    paths = [p for p in paths if p.is_file()]
    return {str(p.relative_to(SUITE)): digest(p) for p in paths}


def baseline(task, path, folder, language):
    if language == 'cpp':
        binary = folder / 'baseline-cpp'
        built = subprocess.run(['clang++', '-std=c++17', '-O2', str(path), str(HERE / 'driver.cpp'), '-o', str(binary)], capture_output=True, text=True)
        if built.returncode:
            return {'semantic_ok': False, 'feedback': built.stderr, 'tests_passed': 0}
        command = [str(binary)]
    else:
        command = [sys.executable, '-I', str(SUITE / 'generation/application/python_driver.py'), str(path)]
    passed = 0
    for index, value in enumerate(task['inputs']):
        with tempfile.TemporaryDirectory(dir=folder) as directory:
            work = Path(directory)
            data = bytes.fromhex(value)
            (work / 'input.bin').write_bytes(data)
            environment = task.get('environments', [{}] * len(task['inputs']))[index]
            answer = expected(task['id'], data, environment)
            # References are authored, trusted code; no inference or generated-code execution here.
            env = {'PATH': os.environ['PATH'], 'HOME': str(work), 'PYTHONDONTWRITEBYTECODE': '1', **environment}
            result = subprocess.run(command, cwd=work, env=env, capture_output=True, timeout=5)
            output = work / 'output.bin'
            good = result.returncode == 0 and result.stdout == f'{len(answer)}\n'.encode() and result.stderr == b'' and output.exists() and output.read_bytes() == answer and (work / 'input.bin').read_bytes() == data
            passed += int(good)
            if not good:
                print(f"FAIL {task['id']}/{language} fixture {index}: {result.stderr!r}, stdout={result.stdout!r}", flush=True)
    return {'semantic_ok': passed == len(task['inputs']), 'tests_passed': passed}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--task', action='append', help='Optional task IDs for development checks')
    parser.add_argument('--group', choices=['all', 'original', 'external'], default='all')
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    if output.is_relative_to(SUITE) or output.is_relative_to(application.ROOT):
        parser.error('Results must be outside source checkouts.')
    application.prepare()
    application.expected = expected
    tasks = load_tasks(args.group)
    if args.task:
        tasks = [t for t in tasks if t['id'] in args.task]
        if {t['id'] for t in tasks} != set(args.task):
            parser.error('Unknown task ID')
    results = []
    goldens = load_goldens()
    with tempfile.TemporaryDirectory(prefix='nil-corpus-') as directory:
        for frozen in tasks:
            golden = goldens[frozen['id']]
            task = frozen | {'inputs': frozen['inputs'] + [golden['input']]}
            if 'environments' in frozen:
                task['environments'] = frozen['environments'] + [golden['environment']]
            assert expected(task['id'], bytes.fromhex(golden['input']), golden['environment']) == bytes.fromhex(golden['output'])
            folder = Path(directory) / task['id']
            folder.mkdir()
            for language, extension in [('expr-v5', 'nil'), ('python', 'py'), ('cpp', 'cpp')]:
                if (language == 'expr-v5' and task['nil_status'] == 'unsupported') or (language != 'expr-v5' and task.get('baseline_status') == 'unsupported'):
                    results.append({'task': task['id'], 'language': language, 'status': 'unsupported', 'reason': task['unsupported_reason']})
                    continue
                path = HERE / 'programs' / f"{task['id']}.{extension}"
                verdict = application.evaluate(path.read_text(), language, task, folder) if language == 'expr-v5' else baseline(task, path, folder, language)
                results.append({'task': task['id'], 'language': language, 'source_sha256': digest(path), **verdict})
                print(f"{task['id']}/{language}: {'PASS' if verdict['semantic_ok'] else 'FAIL'} {verdict}", flush=True)
    totals = dict(tasks=len(tasks), nil_programs=sum(r['language'] == 'expr-v5' and r.get('semantic_ok', False) for r in results), unsupported=sum(r['language'] == 'expr-v5' and r.get('status') == 'unsupported' for r in results), reference_checks=sum(r.get('tests_passed', 0) for r in results if r['language'] == 'expr-v5'), native_checks=sum(r.get('native_tests_passed', 0) for r in results), python_checks=sum(r.get('tests_passed', 0) for r in results if r['language'] == 'python'), cpp_checks=sum(r.get('tests_passed', 0) for r in results if r['language'] == 'cpp'), inconclusive_checks=sum(len(r.get('inconclusive_checks', [])) for r in results))
    report = {'schema': 1, 'group': args.group, 'compiler_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=application.ROOT, text=True).strip(), 'source_hashes': fingerprint(), 'totals': totals, 'results': results}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print('TOTALS ' + json.dumps(totals), flush=True)
    if any(not r.get('semantic_ok', False) and r.get('failure_reason') != 'resource_inconclusive' for r in results if r.get('status') != 'unsupported'):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
