"""Before/after equality migration: repeated calls and whole-sequence sensitivity.
Whole-process wall time, warmup, verified outputs, no CPU isolation. Neither a
pure dispatch microbenchmark nor a claim about an opaque native ABI.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before-compiler', type=Path, required=True)
    parser.add_argument('--before-revision', default='c4ffcfb')
    parser.add_argument('--repeats', type=int, default=25)
    parser.add_argument('--workload', action='append', choices=['hot', 'hot-file', 'whole-file'])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.repeats < 5:
        parser.error('at least five repeats required')
    out = args.output.resolve()
    if out.is_relative_to(ROOT):
        parser.error('results must be outside source checkouts')
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(['cargo', 'build', '--release', '-p', 'nil', '--locked', '--offline'], cwd=ROOT, check=True)
    compilers = {'before': args.before_compiler.resolve(), 'after': ROOT / 'target/release/nil'}
    size = 16 * 1024 * 1024
    data = bytes(range(256)) * (size // 256)
    input_file = out / 'input.bin'
    input_file.write_bytes(data)
    tasks = [('hot', [str(size)], b'65536\n', size),
             ('hot-file', [str(input_file)], b'65536\n', size + 1),
             ('whole-file', [str(input_file)], b'true\n', 1)]
    if args.workload:
        tasks = [task for task in tasks if task[0] in args.workload]
    cases = []
    for task, values, expected, calls in tasks:
        for opt in ['O0', 'O2']:
            binaries = {}
            ir_counts = {}
            for name, compiler in compilers.items():
                binary = out / f'{task}-{name}-{opt}'
                subprocess.run([str(compiler), '--profile', 'expr-v5', 'build', str(HERE / (task + '.nil')), '-' + opt, '-o', str(binary)], check=True)
                ir = subprocess.check_output([str(compiler), '--profile', 'expr-v5', 'llvm', str(HERE / (task + '.nil'))], text=True)
                (out / f'{task}-{name}.ll').write_text(ir)
                ir_counts[name] = {key: ir.count(key) for key in ['call ptr @nil_roots_enter(', 'call void @nil_root_store(', 'call ptr @nil_set_unique(', 'call ptr @nil_set(', 'call i1 @nil_equal(', 'call i1 @nil_plugin0_fn0(', 'call i1 @nil_bulk_compare(']}
                binaries[name] = binary
            samples = {name: [] for name in compilers}
            # Paired, alternating order avoids timing every old binary first.
            for repeat in range(args.repeats + 1):
                for name in list(compilers) if repeat % 2 == 0 else reversed(compilers):
                    start = time.perf_counter_ns()
                    result = subprocess.run([str(binaries[name]), *values], capture_output=True, timeout=60)
                    elapsed = time.perf_counter_ns() - start
                    if result.returncode or result.stdout != expected or result.stderr:
                        raise RuntimeError(f'{task}/{name}/{opt}: {result.stdout!r} {result.stderr!r}')
                    if repeat:
                        samples[name].append(elapsed)
            medians = {name: statistics.median(v) for name, v in samples.items()}
            record = {'workload': task, 'optimization': opt, 'input_bytes': size,
                      'working_set': 'one mutable byte, logical N iterations' if task == 'hot' else '16 MiB file plus scratch or second read',
                      'calls': calls, 'output': expected.decode(), 'samples_ns': samples, 'median_ns': medians,
                      'effective_delta_ns_per_call': (medians['after'] - medians['before']) / calls,
                      'ir_counts': ir_counts}
            cases.append(record)
            print(json.dumps({k: v for k, v in record.items() if k not in ['samples_ns', 'ir_counts']}), flush=True)
    report = {'schema': 1, 'methodology': __doc__, 'repeats': args.repeats, 'warmups': 1,
              'before_revision': args.before_revision,
              'after_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'compiler_sha256': {k: digest(v) for k, v in compilers.items()},
              'source_sha256': {p.name: digest(p) for p in HERE.glob('*.nil')},
              'input_sha256': digest(input_file), 'platform': platform.platform(),
              'clang': subprocess.check_output(['clang', '--version'], text=True), 'cases': cases}
    (out / 'results.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
