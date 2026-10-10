"""Isolated CLI frontend/IR and reference heap controls for Round 25.

Run alone after validation. Original source/fixture hashes are recorded; no
natural source, task contract, oracle, or golden is changed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / 'benchmarks'
sys.path.insert(0, str(BENCH / 'corpora/neetcode150'))
import fixtures
import reference


def summary(values):
    return dict(min_ms=min(values), median_ms=statistics.median(values),
                max_ms=max(values), samples_ms=values)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--repeats', type=int, default=25)
    parser.add_argument('--reference-timeout', type=int, default=300)
    args = parser.parse_args()
    if args.repeats < 15 or args.output.resolve().is_relative_to(ROOT):
        parser.error('15+ repetitions and output outside the checkout required')
    source = BENCH / 'corpora/application-v5/programs/ex_go_counting.nil'
    if not source.exists():
        source = next((BENCH / 'corpora/application-v5').rglob('ex_go_counting.nil'))
    samples = {'before': [], 'after': []}
    compilers = {'before': args.baseline.resolve(), 'after': ROOT / 'target/release/nil'}
    for repeat in range(args.repeats + 1):
        order = list(compilers)
        if repeat % 2:
            order.reverse()
        for mode in order:
            started = time.perf_counter_ns()
            result = subprocess.run([str(compilers[mode]), '--profile', 'expr-v5',
                                     'llvm', str(source)], capture_output=True, timeout=120)
            elapsed = (time.perf_counter_ns() - started) / 1e6
            assert result.returncode == 0 and not result.stderr, result.stderr
            assert b'define' in result.stdout
            if repeat:
                samples[mode].append(elapsed)
    slug = 'last-stone-weight'
    task = next(t for t in json.loads((BENCH / 'corpora/neetcode150/tasks.json').read_text())['tasks'] if t['id'] == slug)
    label, data = list(fixtures.cases(task))[-1]
    answer = reference.SOLVERS[slug](data)
    natural = BENCH / 'core-generalize-study/natural' / (slug + '.nil')
    with tempfile.TemporaryDirectory(prefix='nil-r25-reference-') as directory:
        work = Path(directory)
        (work / 'input.bin').write_bytes(data)
        started = time.perf_counter_ns()
        command = [str(ROOT / 'target/release/examples/core_check'), str(natural),
                   str(work / 'input.bin'), str(work / 'output.bin'), str(work / 'stdout.bin')]
        try:
            result = subprocess.run(command, capture_output=True, timeout=args.reference_timeout)
            assert result.returncode == 0 and not result.stderr, result.stderr
            assert (work / 'output.bin').read_bytes() == answer
            assert (work / 'input.bin').read_bytes() == data
            assert (work / 'stdout.bin').read_bytes() == b''
            observation = dict(outcome='verified', stdout=result.stdout.decode())
        except subprocess.TimeoutExpired:
            observation = dict(outcome='timeout', timeout_seconds=args.reference_timeout)
        observation['elapsed_ms'] = (time.perf_counter_ns() - started) / 1e6
    report = dict(frontend_ir={k: summary(v) for k, v in samples.items()},
                  compiler_sha256={k: hashlib.sha256(v.read_bytes()).hexdigest() for k, v in compilers.items()},
                  compiler_patch_sha256=hashlib.sha256(subprocess.check_output(['git', 'diff', '--binary', 'HEAD', '--', 'crates', 'cli', 'tools', 'std'], cwd=ROOT)).hexdigest(),
                  new_ownership_fixed_point='Not implemented in R1; R2 remains pending',
                  method='Whole-process CLI llvm: parse/check/HIR/IR, no Clang; one warmup; alternating order',
                  source=str(source.relative_to(BENCH)), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  source_bytes=source.stat().st_size, reference_heap=observation,
                  fixture=label, input_sha256=hashlib.sha256(data).hexdigest(),
                  natural_sha256=hashlib.sha256(natural.read_bytes()).hexdigest(),
                  reference_command=command, compiler_revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
