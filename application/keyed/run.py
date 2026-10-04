"""Whole-process keyed scaling, including startup, decimal keys and checked ops."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get('NIL_ROOT', HERE.parents[2])).resolve()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--repeats', type=int, default=9)
    parser.add_argument('--records', action='store_true', help='also measure scalar-record insertion and the conservative record-field append boundary')
    parser.add_argument('--compiler', type=Path, help='Use a frozen compiler for paired historical comparisons')
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        parser.error('Output must be outside source checkouts')
    output.mkdir(parents=True, exist_ok=True)
    if args.compiler is None:
        subprocess.run(['cargo', 'build', '-p', 'nil', '--release', '--locked', '--offline'], cwd=ROOT, check=True)
    compiler = args.compiler.resolve() if args.compiler else ROOT / 'target/release/nil'
    records = []
    workloads = [('insert', [1000, 4000, 16000, 64000]), ('repack', [1000, 4000, 16000, 64000]), ('repack-held', [4096, 65536, 1048576])]
    if args.records:
        workloads += [('record-insert', [1000, 4000, 16000, 64000]), ('record-append', [10000, 40000, 160000])]
    for name, sizes in workloads:
        binary = output / name
        subprocess.run([str(compiler), '--profile', 'expr-v5', 'build', str(HERE / (name + '.nil')), '-O2', '-o', str(binary)], cwd=ROOT, check=True)
        for count in sizes:
            times = []
            for repeat in range(args.repeats + 1):
                start = time.perf_counter_ns()
                result = subprocess.run([str(binary), str(count)], capture_output=True, timeout=60)
                elapsed = (time.perf_counter_ns() - start) / 1e6
                expected = count if name in ('insert', 'record-insert', 'record-append') else 2 if name == 'repack-held' else 1
                if result.returncode or result.stdout != f'{expected}\n'.encode() or result.stderr:
                    raise RuntimeError(f'{name}/{count}: {result.stdout!r} {result.stderr!r}')
                if repeat:
                    times.append(elapsed)
            record = {'workload': name, 'iterations': 1000 if name == 'repack-held' else count, 'held_bytes': count if name == 'repack-held' else None, 'median_ms': statistics.median(times), 'samples_ms': times}
            records.append(record)
            print(json.dumps(record), flush=True)
    boundary = []
    for count in [262144, 262145, 262146, 524288]:
        result = subprocess.run([str(output / 'insert'), str(count)], capture_output=True, timeout=60)
        boundary.append({'iterations': count, 'returncode': result.returncode, 'stdout': result.stdout.decode(), 'stderr': result.stderr.decode()})
    record_boundary = []
    if args.records:
        for count in [262143, 262144, 262145, 262146]:
            result = subprocess.run([str(output / 'record-insert'), str(count)], capture_output=True, timeout=60)
            record_boundary.append({'iterations': count, 'returncode': result.returncode, 'stdout': result.stdout.decode(), 'stderr': result.stderr.decode()})
    report = {'record_boundary': record_boundary, 'schema': 1, 'methodology': 'Whole-process wall time; one warmup, median of repeats, output verified; no CPU isolation. Includes decimal key formatting and hash table growth. Repack increases an owned byte value by one byte each iteration, deliberately measuring the disclosed quadratic payload copy.', 'compiler_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'repeats': args.repeats, 'compiler_sha256': hashlib.sha256(compiler.read_bytes()).hexdigest(), 'source_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.nil')}, 'records': records, 'boundary': boundary}
    (output / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
    print('BOUNDARY ' + json.dumps(boundary), flush=True)
    if args.records:
        print('RECORD_BOUNDARY ' + json.dumps(record_boundary), flush=True)


if __name__ == '__main__':
    main()
