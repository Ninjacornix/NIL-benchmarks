#!/usr/bin/env python3
"""Reproduce the pre-ledger read-error/quota conflict on macOS, without compiler edits.

A reported conflict is expected for this audit, NOT a successful parity test.
Use --require-parity to make an admission check fail on any conflict.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import time

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
ROOT = BENCH.parent
CODE = re.compile(rb'(E\d{3}) @(\d+)\.\.(\d+) ')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def definitions():
    path = '"nil-quota-fault.bin"'
    read = f'#!read({path})'
    bytes_prefix = '=large=!bytes(67108500,0);'
    return [
        dict(id='no-quota-read-error', source=f'={read}\n', size=4096, fault=4096, expected=('E015', 'E015')),
        dict(id='quota-only-real-read', source=f'{bytes_prefix}n={read};#large+n\n', size=4096, fault=None, expected=('E013', 'E013')),
        dict(id='error-prefix-below-quota', source=f'{bytes_prefix}n={read};#large+n\n', size=4096, fault=64, expected=('E015', 'E015')),
        dict(id='byte-value-retained', source=f'{bytes_prefix}n={read};#large+n\n', size=4096, fault=4096, expected=('E015', 'E013')),
        dict(id='buffer-value-retained', source=f'=large=!buffer(8388562,0);n={read};#large+n\n', size=4096, fault=4096, expected=('E015', 'E013')),
        dict(id='record-child-retained', source=f'record Holder(text:s,n:i)\n=large=Holder(!bytes(67108500,0),0);n={read};#large.text+n\n', size=4096, fault=4096, expected=('E015', 'E013')),
        dict(id='record-buffer-child-retained', source=f'record Holder(text:s)\n=large=!buffer[Holder](1,Holder(!bytes(67108500,0)));n={read};#large[0].text+n\n', size=4096, fault=4096, expected=('E015', 'E013')),
        dict(id='map-and-byte-value-retained', source=f'=large=!bytes(67108000,0);map=!map();n={read};#large+!size(map)+n\n', size=4096, fault=4096, expected=('E015', 'E013')),
        dict(id='selected-lazy-arm', source=f'{bytes_prefix}n=(true?{read}:0);#large+n\n', size=4096, fault=4096, expected=('E015', 'E013')),
        dict(id='callee-read-retained-argument', source=f'{bytes_prefix}b(large)\n(s)=n={read};#a+n\n', size=4096, fault=4096, expected=('E015', 'E013')),
        dict(id='unselected-lazy-arm', source=f'{bytes_prefix}n=(false?{read}:0);#large+n\n', size=4096, fault=4096, expected=('OK', 'OK'), value=67108500, calls=0),
        dict(id='dead-allocation-does-not-charge-read', source=f'=dead=!bytes(67108500,0);{read}\n', size=4096, fault=4096, expected=('E015', 'E015')),
        dict(id='short-real-file-fits', source=f'{bytes_prefix}n={read};#large+n\n', size=64, fault=None, expected=('OK', 'OK'), value=67108564),
        dict(id='error-before-any-prefix', source=f'{bytes_prefix}n={read};#large+n\n', size=4096, fault=0, expected=('E015', 'E015')),
    ]


def observation(result):
    diagnostic = CODE.match(result.stderr)
    if diagnostic:
        if result.returncode != 1 or result.stdout:
            raise AssertionError(f'Unexpected failure status/output: {result!r}')
        return dict(code=diagnostic[1].decode(), span=[int(diagnostic[2]), int(diagnostic[3])], stdout_hex=result.stdout.hex())
    if result.returncode or result.stderr:
        raise AssertionError(f'Infrastructure failure, not a language diagnostic: {result!r}')
    return dict(code='OK', span=None, stdout_hex=result.stdout.hex())


def command(args, cwd=ROOT, env=None):
    result = subprocess.run(list(map(str, args)), cwd=cwd, env=env, capture_output=True, timeout=120)
    if result.returncode:
        raise RuntimeError(f'Command failed: {args}: {result.stderr!r}')
    return result.stdout.decode().strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--compiler', type=Path, default=ROOT / 'target/release/nil')
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--require-parity', action='store_true')
    args = parser.parse_args()
    if platform.system() != 'Darwin':
        parser.error('The deterministic interposer uses Darwin FILE/F_GETPATH. No portable-platform claim.')
    if args.repeats < 1:
        parser.error('--repeats must be positive')
    out = args.out.expanduser().resolve()
    if out.is_relative_to(ROOT) or out.is_relative_to(BENCH):
        parser.error('Raw artifacts must be outside source checkouts')
    out.mkdir(parents=True, exist_ok=True)
    start = time.time()
    compiler = args.compiler.resolve()
    reference = out / 'reference-read'
    dylib = out / 'host-failure.dylib'
    deps = ROOT / 'target/release/deps'
    compile_reference = ['rustc', '--edition=2024', str(HERE / 'reference_read.rs'), '-L', f'dependency={deps}',
                         '--extern', f'nil_compiler={ROOT}/target/release/libnil_compiler.rlib',
                         '--extern', f'nil_hir={ROOT}/target/release/libnil_hir.rlib', '-o', str(reference)]
    command(compile_reference)
    compile_fault = ['clang', '-std=c11', '-Werror', '-Wno-deprecated-declarations', '-dynamiclib',
                     str(HERE / 'host_failure.c'), '-o', str(dylib)]
    command(compile_fault)
    results = []
    native_build_commands = []
    harness_inputs = {p.name: digest(p) for p in sorted(HERE.glob('*')) if p.is_file()}
    for task in definitions():
        work = out / task['id']
        work.mkdir(exist_ok=True)
        source = work / 'source.nil'
        source.write_text(task['source'])
        (work / 'nil-quota-fault.bin').write_bytes(b'x' * task['size'])
        variants = [('reference', [str(reference), str(source)])]
        for mode in ('bounded', 'unbounded'):
            for opt in ('O0', 'O2'):
                binary = work / f'native-{mode}-{opt}'
                build = [compiler, '--profile', 'expr-v5', f'--{mode}', 'build', source, '-o', binary, f'-{opt}']
                command(build)
                native_build_commands.append(list(map(str, build)))
                variants.append((binary.name, [str(binary)]))
        records = []
        for repeat in range(args.repeats):
            for name, invoke in variants:
                stem = work / f'{name}-{repeat}'
                env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'HOME': str(work)}
                if task['fault'] is not None:
                    env |= {'DYLD_INSERT_LIBRARIES': str(dylib), 'NIL_AUDIT_TRACE': str(stem) + '.trace.json',
                            'NIL_AUDIT_FAIL_AFTER': str(task['fault'])}
                result = subprocess.run(invoke, cwd=work, env=env, capture_output=True, timeout=30)
                Path(str(stem) + '.stdout').write_bytes(result.stdout)
                Path(str(stem) + '.stderr').write_bytes(result.stderr)
                seen = observation(result)
                expected = task['expected'][0 if name == 'reference' else 1]
                allowed = set(task['expected']) if args.require_parity else {expected}
                assert seen['code'] in allowed, (task['id'], name, seen, allowed)
                trace = json.loads(Path(str(stem) + '.trace.json').read_text()) if task['fault'] is not None else None
                if seen['code'] == 'OK':
                    assert result.stdout == f"{task['value']}\n".encode()
                elif seen['span'] != [task['source'].index('!read'), task['source'].index('!read') + 1]:
                    raise AssertionError((task['id'], name, 'wrong diagnostic span', seen))
                if trace is not None:
                    if 'calls' in task:
                        assert trace['read_calls'] == task['calls']
                    elif name == 'reference' or seen['code'] == 'E015':
                        assert trace['failure_request_bytes'] > 0
                        assert trace['prefix_bytes'] == task['fault'] and trace['EIO_returns'] == 1, (task['id'], name, trace)
                    else:
                        assert seen['code'] == 'E013' and 0 < trace['prefix_bytes'] < task['fault'] and trace['EIO_returns'] == 0
                records.append(dict(variant=name, repeat=repeat, command=invoke, exit=result.returncode, observation=seen, trace=trace))
        by_repeat = [{r['variant']: r['observation'] for r in records if r['repeat'] == repeat} for repeat in range(args.repeats)]
        divergences = sum(observed != trial['reference'] for trial in by_repeat for name, observed in trial.items() if name != 'reference')
        conflict = bool(divergences)
        results.append(dict(task=task, source_sha256=digest(source), parity=not conflict, diagnostic_divergences=divergences, records=records))
        ref_codes = ','.join(sorted({r['observation']['code'] for r in records if r['variant'] == 'reference'}))
        native_codes = ','.join(sorted({r['observation']['code'] for r in records if r['variant'] != 'reference'}))
        print(f"{task['id']}: {'CONFLICT' if conflict else 'PARITY'} reference={ref_codes} native={native_codes} O0/O2 bounded/unbounded repeats={args.repeats}", flush=True)
    manifest = {str(p.relative_to(out)): digest(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name not in ('report.json', 'manifest.json')}
    report = dict(schema=1, status='BLOCKED_B1' if any(not r['parity'] for r in results) else 'PARITY',
                  main_revision=command(['git', 'rev-parse', 'HEAD']), benchmark_revision=command(['git', 'rev-parse', 'HEAD'], cwd=BENCH),
                  compiler_sha256=digest(compiler), platform=platform.platform(), clang=command(['clang', '--version']).splitlines()[0],
                  rustc=command(['rustc', '--version']), compile_reference=compile_reference, compile_fault=compile_fault,
                  native_build_commands=native_build_commands, harness_inputs=harness_inputs,
                  NIL_CLANG=os.environ.get('NIL_CLANG', 'clang'),
                  started_epoch=start, finished_epoch=time.time(), repeats=args.repeats,
                  totals=dict(families=len(results), conflict_families=sum(not r['parity'] for r in results),
                              reference_runs=len(results)*args.repeats, native_runs=len(results)*args.repeats*4,
                              comparisons=len(results)*args.repeats*4,
                              diagnostic_divergences=sum(r['diagnostic_divergences'] for r in results)),
                  results=results, raw_manifest=manifest)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('TOTALS ' + json.dumps(report['totals']), flush=True)
    print('ADMISSION ' + report['status'], flush=True)
    if args.require_parity and report['status'] != 'PARITY':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
