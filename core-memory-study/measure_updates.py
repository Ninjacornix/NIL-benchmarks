"""Source std swap/pop versus the equivalent checked caller form.

Warm subprocess wall times, rotating order, 25+ repetitions. Inputs are runtime
arguments; every timed run checks its result. Timing runs must be isolated from
CI/fuzz. This measures source-boundary cost, not a C++ comparison or corpus task.
"""
import argparse, hashlib, json, statistics, subprocess, tempfile, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repeats', type=int, default=25)
    args = parser.parse_args()
    if args.repeats < 25 or args.output.resolve().is_relative_to(ROOT):
        parser.error('25+ repeats and outside-checkout output required')
    compiler = ROOT / 'target/release/nil'
    rows = []
    with tempfile.TemporaryDirectory(prefix='nil-std-updates-') as directory:
        folder = Path(directory)
        for kind in ['bytes', 'buffer']:
            for operation in ['swap', 'pop']:
                initial = f'!{kind}(256,97)[1:98]' if operation == 'swap' else f'!{kind}(a,97)'
                finish = 'a[0]+a[1]' if operation == 'swap' else '#a'
                bodies = {'std': '!swap(a,0,1)' if operation == 'swap' else '!pop(a)',
                          'caller': '(right=a[1];left=a[0];a[0:right][1:left])' if operation == 'swap' else '!slice(a,0,#a-1)'}
                sources = {mode: f'1=@({initial},0,a;b<c;{body},b+1,c;{finish})\n' for mode, body in bodies.items()}
                binaries = {}
                for mode, source in sources.items():
                    path = folder / f'{kind}-{operation}-{mode}.nil'
                    path.write_text(source)
                    binary = path.with_suffix('')
                    build = subprocess.run([str(compiler), '--profile', 'expr-v5', 'build', str(path), '-O2', '-o', str(binary)], capture_output=True)
                    assert build.returncode == 0 and not build.stderr, build.stderr
                    binaries[mode] = binary
                samples = {mode: [] for mode in binaries}
                expected = b'195\n' if operation == 'swap' else b'0\n'
                for rep in range(args.repeats + 1):
                    modes = list(binaries)
                    if rep % 2: modes.reverse()
                    for mode in modes:
                        started = time.perf_counter_ns()
                        result = subprocess.run([str(binaries[mode]), '1048576'], capture_output=True, timeout=120)
                        elapsed = (time.perf_counter_ns() - started) / 1e6
                        assert result.returncode == 0 and result.stdout == expected and not result.stderr, result
                        if rep: samples[mode].append(elapsed)
                timings = {mode: dict(min_ms=min(values), median_ms=statistics.median(values), max_ms=max(values), samples_ms=values) for mode, values in samples.items()}
                row = dict(type=kind, operation=operation, iterations=1048576, timings=timings, std_caller_ratio=timings['std']['median_ms']/timings['caller']['median_ms'], source_sha256={mode: hashlib.sha256(source.encode()).hexdigest() for mode,source in sources.items()}, sources=sources)
                rows.append(row)
                print(kind, operation, {mode: round(value['median_ms'],3) for mode,value in timings.items()}, flush=True)
    report = dict(schema=1, method=__doc__, repeats=args.repeats, compiler_base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(), results=rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')

if __name__ == '__main__': main()
