"""End-to-end cached-file byte loops; correctness gates every timed sample."""
import hashlib
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from support import ROOT


def run(folder, repeats, smoke=False):
    subprocess.run(['cargo', 'build', '--release', '--locked', '--offline', '-p', 'nil'], cwd=ROOT, check=True)
    nil = folder / 'transform-nil'
    cpp = folder / 'transform-cpp'
    stages = {name: folder/name for name in ['read-only', 'read-write']}
    compiler = ROOT / 'target/release/nil'
    clang = os.environ.get('NIL_CLANG', 'clang')
    cpp_clang = os.environ.get('NIL_CLANGXX', clang.replace('clang', 'clang++'))
    version = subprocess.check_output([clang, '--version'], text=True)
    built = time.perf_counter_ns()
    subprocess.run([str(compiler), '--profile', 'expr-v5', 'build', str(HERE/'transform.nil'), '-o', str(nil), '-O2'], capture_output=True, check=True)
    nil_build_ns = time.perf_counter_ns()-built
    for name, binary in stages.items():
        subprocess.run([str(compiler), '--profile', 'expr-v5', 'build', str(HERE/(name+'.nil')), '-o', str(binary), '-O2'], capture_output=True, check=True)
    built = time.perf_counter_ns()
    subprocess.run([cpp_clang, '-std=c++17', '-O2', str(HERE/'transform.cpp'), '-o', str(cpp)], capture_output=True, check=True)
    cpp_build_ns = time.perf_counter_ns()-built
    commands = {'nil': [str(nil)], 'cpp': [str(cpp)], 'python': [sys.executable, str(HERE/'transform.py')]}
    cases = []
    for size in ([4096] if smoke else [4096, 1048576, 16777216]):
        input_path = folder/'input.bin'
        output_path = folder/'output.bin'
        data = (bytes(range(256))*((size+255)//256))[:size]
        expected = bytes(255-byte for byte in data)
        input_path.write_bytes(data)
        samples = {name: [] for name in commands}
        for round_index in range(repeats+1):
            # Rotate paired execution order; first round warms caches/interpreters.
            order = list(commands)
            order = order[round_index%3:]+order[:round_index%3]
            for name in order:
                output_path.write_bytes(b'sentinel')
                started = time.perf_counter_ns()
                process = subprocess.run([*commands[name], str(input_path), str(output_path)], capture_output=True, check=True, timeout=60)
                elapsed = time.perf_counter_ns()-started
                if process.stdout != f'{size}\n'.encode() or process.stderr or output_path.read_bytes() != expected or input_path.read_bytes() != data:
                    raise ValueError(f'{name}: byte transform correctness failure at size {size}')
                if round_index: samples[name].append(elapsed)
        # Round-trip is an untimed extra correctness gate, never a timed sample.
        roundtrip = folder/'roundtrip.bin'
        subprocess.run([str(nil), str(output_path), str(roundtrip)], capture_output=True, check=True, timeout=60)
        if roundtrip.read_bytes() != data:
            raise ValueError(f'double transform round-trip failure at size {size}')
        stage_samples = {name: [] for name in stages}
        for round_index in range(repeats+1):
            order = list(stages)
            order = order[round_index%2:]+order[:round_index%2]
            for name in order:
                output_path.write_bytes(b'sentinel')
                args = [str(input_path)] if name == 'read-only' else [str(input_path), str(output_path)]
                started = time.perf_counter_ns()
                process = subprocess.run([str(stages[name]), *args], capture_output=True, check=True, timeout=60)
                elapsed = time.perf_counter_ns()-started
                expected_output = b'sentinel' if name == 'read-only' else data
                if process.stdout != f'{size}\n'.encode() or process.stderr or output_path.read_bytes() != expected_output or input_path.read_bytes() != data:
                    raise ValueError(f'{name}: stage correctness failure at size {size}')
                if round_index: stage_samples[name].append(elapsed)
        cases.append(dict(bytes=size, input_sha256=hashlib.sha256(data).hexdigest(), output_sha256=hashlib.sha256(expected).hexdigest(), samples_ns=samples,
                          median_ns={name: statistics.median(values) for name, values in samples.items()},
                          stage_samples_ns=stage_samples, stage_median_ns={name: statistics.median(values) for name, values in stage_samples.items()}, double_transform_roundtrip=True))
    return dict(cases=cases, clang_version=version, compiler_build_ns={'nil': nil_build_ns, 'cpp': cpp_build_ns},
                binary_bytes={'nil': nil.stat().st_size, 'cpp': cpp.stat().st_size}, warmups=1, repeats=repeats,
                method='Whole process: startup, cached-file read, byte-by-byte inversion, write, stdout count and exit. Builds and output verification excluded. No fsync; not cold disk or kernel-only latency. Python explicitly loops, not bytes.translate. Read-only/read-write stage medians are separate whole-process runs, not additive instrumentation. Double transform is verified outside timing. No source tokens or LLM generation/repair measurement.')
