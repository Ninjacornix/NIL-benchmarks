import subprocess, sys, time, statistics
from pathlib import Path
nil = str(Path(__file__).resolve().parents[2] / 'target/release/nil')
data = Path('input.bin').read_bytes()
keep = {'v': lambda b: b % 2 == 0, 'w': lambda b: b < 128}
names = sys.argv[1:]
expected = {}
for n in names:
    r = subprocess.run([nil,'--profile','expr-v5','build',f'{n}.nil','-o',n,'-O2'],capture_output=True,text=True)
    if r.returncode: print(n,'BUILD FAIL',r.stderr[:300]); sys.exit(1)
    expected[n] = bytes(b for b in data if keep[n[0]](b))
samples = {n: [] for n in names}
for i in range(13):
    for n in names[i % len(names):] + names[:i % len(names)]:
        t = time.perf_counter(); out = subprocess.run([f'./{n}','input.bin'],capture_output=True).stdout; dt = (time.perf_counter()-t)*1e3
        if out.rstrip(b'\n') != expected[n]: print(n, 'WRONG OUTPUT', len(out), len(expected[n])); sys.exit(1)
        if i: samples[n].append(dt)
for n in names: s = samples[n]; print(f'{n:16} min {min(s):8.1f}  median {statistics.median(s):8.1f}  max {max(s):8.1f} ms  (output verified)')
