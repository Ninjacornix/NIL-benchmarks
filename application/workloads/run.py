"""Append scaling and three distinct application paths, with independent oracles."""
import hashlib
import os
from pathlib import Path
import statistics
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))
from support import ROOT


def is_scan(name):
    return name in ['newlines', 'byte_sum'] or name.startswith('newlines_')


def run(folder, repeats, smoke=False, selected=None):
    subprocess.run(['cargo', 'build', '--release', '--locked', '--offline', '-p', 'nil'], cwd=ROOT, check=True)
    compiler = ROOT/'target/release/nil'
    clang = os.environ.get('NIL_CLANG', 'clang')
    cpp_clang = os.environ.get('NIL_CLANGXX', clang.replace('clang', 'clang++'))
    cpp = folder/'workloads-cpp'
    subprocess.run([cpp_clang, '-std=c++17', '-O2', str(HERE/'main.cpp'), '-o', str(cpp)], capture_output=True, check=True)
    binaries = {}
    names = ['append', 'report', 'newlines', 'reduce', 'byte_sum', 'newlines_call', 'newlines_leaf', 'newlines_noinline', 'newlines_recursive', 'newlines_nested', 'newlines_seq_leaf', 'newlines_seq_return', 'newlines_slice', 'newlines_fresh', 'newlines_cond_alloc']
    if selected:
        unknown = set(selected)-set(names)
        if unknown: raise ValueError(f'Unknown workloads: {sorted(unknown)}')
        names = [name for name in names if name in selected]
    for name in names:
        binary = folder/('workload-'+name)
        environment = os.environ.copy()
        if name in ['newlines_noinline', 'newlines_recursive']:
            environment.update(NIL_CLANG=str(HERE/'noinline.py'), NIL_REAL_CLANG=shutil.which(clang),
                               NIL_NOINLINE_IR=str(folder/(name+'.ll')))
        subprocess.run([str(compiler), '--profile', 'expr-v5', 'build', str(HERE/(name+'.nil')), '-o', str(binary), '-O2'], capture_output=True, check=True, env=environment)
        binaries[name] = binary
    cases = []
    sizes = {'append': [10000, 40000, 160000, 640000, 1048576], 'report': [10000, 40000, 160000],
             'newlines': [4096, 1048576, 16777216], 'reduce': [10000, 100000, 1000000], 'byte_sum': [16777216], 'newlines_call': [16777216], 'newlines_leaf': [16777216], 'newlines_noinline': [16777216], 'newlines_recursive': [16777216], 'newlines_nested': [16777216], 'newlines_seq_leaf': [16777216], 'newlines_seq_return': [16777216], 'newlines_slice': [16777216], 'newlines_fresh': [16777216], 'newlines_cond_alloc': [16777216]}
    sizes = {name: values for name, values in sizes.items() if name in names}
    if smoke:
        sizes = {name: values[:1] for name, values in sizes.items()}
    for name, values in sizes.items():
        for n in values:
            output = folder/(name+'-output.bin')
            expected_file = b'sentinel'
            if is_scan(name):
                pattern = b'alpha,beta,gamma\n'
                data = (pattern*((n+len(pattern)-1)//len(pattern)))[:n]
                input_path = folder/'lines-input.bin'
                input_path.write_bytes(data)
                args = [str(input_path)]
                result = sum(data) if name == 'byte_sum' else data.count(b'\n')
            elif name == 'report':
                args = [str(n), str(output)]
                expected_file = ''.join(f'{i}\n' for i in range(n)).encode()
                result = len(expected_file)
            else:
                args = [str(n)]
                result = n
            reference = 'newlines' if name.startswith('newlines_') else name
            commands = {'nil': [str(binaries[name]), *args], 'cpp': [str(cpp), reference, *args],
                        'python': [sys.executable, str(HERE/'main.py'), reference, *args]}
            samples = {language: [] for language in commands}
            for round_index in range(repeats+1):
                order = list(commands)
                order = order[round_index%3:]+order[:round_index%3]
                for language in order:
                    output.write_bytes(b'sentinel')
                    start = time.perf_counter_ns()
                    process = subprocess.run(commands[language], capture_output=True, check=True, timeout=60)
                    elapsed = time.perf_counter_ns()-start
                    if process.stdout != f'{result}\n'.encode() or process.stderr or output.read_bytes() != expected_file:
                        raise ValueError(f'{name}/{language}/{n}: output oracle failure')
                    if is_scan(name) and input_path.read_bytes() != data:
                        raise ValueError('input mutated')
                    if round_index: samples[language].append(elapsed)
            cases.append(dict(workload=name, input_size=n, result=result, samples_ns=samples,
                              median_ns={language: statistics.median(values) for language, values in samples.items()},
                              output_sha256=hashlib.sha256(expected_file).hexdigest()))
    # The timed append loop returns length; independently verify actual contents
    # at all scaling points, without including this verification in timing.
    content_source = folder/'append-content.nil'
    content_source.write_text('1:s=@(!bytes(0,0),0,a;b<c;!concat(a,"x"),b+1,c;a)\n')
    content_binary = folder/'append-content'
    subprocess.run([str(compiler), '--profile', 'expr-v5', 'build', str(content_source), '-o', str(content_binary), '-O2'], capture_output=True, check=True)
    for n in sizes.get('append', []):
        process = subprocess.run([str(content_binary), str(n)], capture_output=True, check=True, timeout=60)
        if process.stdout != b'x'*n+b'\n' or process.stderr:
            raise ValueError(f'append content failure at {n}')
    # Every scan shape must implement count for arbitrary bytes, not just the
    # timed text fixture. In particular, recursive control stays equivalent.
    control = folder/'scan-binary-control.bin'
    control.write_bytes(bytes(range(256))*4)
    for name in binaries:
        if name == 'newlines' or name.startswith('newlines_'):
            process = subprocess.run([str(binaries[name]), str(control)], capture_output=True, check=True)
            if process.stdout != b'4\n' or process.stderr:
                raise ValueError(f'{name}: arbitrary-byte count oracle failure')
    return dict(scan_binary_control_verified=True, cases=cases, repeats=repeats, warmups=1, append_content_verified=bool(sizes.get('append')),
                clang_version=subprocess.check_output([clang, '--version'], text=True),
                method='Whole processes, one warmup and rotating NIL/C++/Python order. Compilation and output verification excluded. Cached files, no fsync or CPU isolation. Append loops in all languages; report uses incremental NIL/C++ and idiomatic Python join. Newline count uses a NIL/C++ scan and Python bytes.count; reduce uses a native i64 buffer/vector and Python list/sum. These are semantic equivalents, not identical runtime algorithms. Byte-sum is the branchless scan control; newlines_call preserves identity helpers in lazy arms; leaf uses a scalar comparison helper; seq_leaf passes the sequence into a checked-reading helper. noinline and recursive use a benchmark-only IR hook on helper nil_fn2, with noinline and disable-tail-calls attributes, to preserve actual calls. Nested scans use 256-byte inner loops; seq_return carries a sequence through an identity-returning helper, outside the scalar proof. C++/Python use the same direct count reference for every scan shape, not matched function shapes. No LLM/token efficiency inference.')
