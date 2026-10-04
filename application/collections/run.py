"""Native record-buffer scaling using the existing whole-process convention."""
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
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repeats', type=int, default=25)
    parser.add_argument('--workload', action='append', help='Select a controlled shape; omit to run all')
    parser.add_argument('--compiler', type=Path, help='Use a frozen compiler for paired historical comparisons')
    args = parser.parse_args()
    out = args.output.resolve()
    if out.is_relative_to(ROOT):
        parser.error('Output must be outside source checkouts')
    out.mkdir(parents=True, exist_ok=True)
    if args.compiler is None:
        subprocess.run(['cargo', 'build', '-p', 'nil', '--release', '--locked', '--offline'], cwd=ROOT, check=True)
    compiler = args.compiler.resolve() if args.compiler else ROOT / 'target/release/nil'
    rows = []
    shapes = [('build', [1000, 4000, 16000, 64000, 256000, 1048576]),
              ('update', [1000, 4000, 16000, 64000, 256000, 1048576]),
              ('nested-build', [1000, 4000, 16000]),
              ('nested-build-shared', [1000, 4000, 16000]),
              ('nested-update', [1000, 4000, 16000, 64000, 256000, 1048576]),
              ('alias-build', [1000, 4000, 16000])]
    if args.workload:
        if set(args.workload) - {name for name, _ in shapes}:
            parser.error('Unknown workload')
        shapes = [(name, sizes) for name, sizes in shapes if name in args.workload]
    for name, sizes in shapes + [('boundary', [])]:
        exe = out / name
        subprocess.run([str(compiler), '--profile', 'expr-v5', 'build', str(HERE / (name + '.nil')), '-O2', '-o', str(exe)], cwd=ROOT, check=True)
        for n in sizes:
            samples = []
            expected = n*(n-1) if name == 'alias-build' else n*(n-1)//2
            for rep in range(args.repeats + 1):
                start = time.perf_counter_ns()
                result = subprocess.run([str(exe), str(n)], capture_output=True, timeout=120)
                elapsed = (time.perf_counter_ns()-start)/1e6
                if result.returncode or result.stdout != f'{expected}\n'.encode() or result.stderr:
                    raise RuntimeError((name, n, result.returncode, result.stdout, result.stderr))
                if rep:
                    samples.append(elapsed)
            row = dict(workload=name, elements=n, median_ms=statistics.median(samples), samples_ms=samples)
            rows.append(row)
            print(json.dumps(row), flush=True)
    boundary = []
    for name, counts in ([] if args.workload else [('boundary', [4194300,4194301]), ('update', [2097148,2097149]), ('build', [2097146,2097147])]):
        for n in counts:
            result = subprocess.run([str(out/name), str(n)], capture_output=True, timeout=120)
            row = dict(workload=name, elements=n, returncode=result.returncode, stdout=result.stdout.decode(), stderr=result.stderr.decode())
            boundary.append(row)
            print('BOUNDARY '+json.dumps(row), flush=True)
    report = dict(schema=1, methodology='O2 whole-process wall time, one warmup, median of repeats, verified output, no CPU isolation; native only', repeats=args.repeats, compiler_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(), compiler_sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(), source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.nil')}, records=rows, boundary=boundary)
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__ == '__main__':
    main()
