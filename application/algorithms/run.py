"""Whole-process algorithm scaling: setup, checked traversal and sorting included."""
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
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        parser.error('Output must be outside source checkouts')
    output.mkdir(parents=True, exist_ok=True)
    subprocess.run(['cargo', 'build', '-p', 'nil', '--release', '--locked', '--offline'], cwd=ROOT, check=True)
    records = []
    for name, sizes in [('sort-buffer', [1000,4000,16000,64000,1048576]), ('sort-buffer-alias', [1000,4000,16000,64000]), ('sort-map', [1000,4000,16000,64000]), ('each-buffer', [1000,4000,16000,64000,1048576]), ('each-map', [1000,4000,16000,64000])]:
        binary = output / name
        subprocess.run([str(ROOT / 'target/release/nil'), '--profile', 'expr-v5', 'build', str(HERE / (name + '.nil')), '-O2', '-o', str(binary)], cwd=ROOT, check=True)
        for count in sizes:
            times = []
            for repeat in range(args.repeats + 1):
                start = time.perf_counter_ns()
                result = subprocess.run([str(binary), str(count)], capture_output=True, timeout=60)
                elapsed = (time.perf_counter_ns() - start) / 1e6
                expected = count if name.startswith('each') else count+1 if name.endswith('alias') else 1
                if result.returncode or result.stdout != f'{expected}\n'.encode() or result.stderr:
                    raise RuntimeError(f'{name}/{count}: {result.stdout!r} {result.stderr!r}')
                if repeat:
                    times.append(elapsed)
            record = {'workload': name, 'iterations': 1000 if name == 'repack-held' else count, 'held_bytes': count if name == 'repack-held' else None, 'median_ms': statistics.median(times), 'samples_ms': times}
            records.append(record)
            print(json.dumps(record), flush=True)
    boundary = []
    report = {'schema': 1, 'methodology': 'Whole-process wall time; one warmup, median of repeats, output verified; no CPU isolation. Includes construction, full sorting validation/iteration, startup and output. Map keys are formatted decimals; sorted maps include owned key materializations. No cross-language speed claim. Alias sorting retains and reads the original.', 'compiler_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'repeats': args.repeats, 'source_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.nil')}, 'records': records, 'boundary': boundary}
    (output / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
    print('BOUNDARY ' + json.dumps(boundary), flush=True)


if __name__ == '__main__':
    main()
