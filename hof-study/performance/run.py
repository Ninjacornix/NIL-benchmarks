"""Direct/HOF map controls and informational comparator insertion sort baseline."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import time
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--repeats', type=int, default=25)
args = parser.parse_args()
if args.repeats < 15: parser.error('Need >=15 measured repetitions')
folder = args.output.resolve()
if folder.is_relative_to(ROOT): parser.error('Results must be outside checkout')
folder.mkdir(parents=True, exist_ok=True)
subprocess.run(['cargo', 'build', '--release', '--locked', '--offline', '-p', 'nil'], cwd=ROOT, check=True)
compiler = ROOT/'target/release/nil'
clang = shutil.which(os.environ.get('NIL_CLANG','clang'))
names = ['inline','direct','map','direct_noinline','map_noinline','sort','core_sort']
binaries = {}
for name in names:
    source = HERE/(name.replace('_noinline','')+'.nil')
    binary = folder/name
    env = os.environ | {'NIL_CLANG':str(HERE/'capture.py'), 'NIL_REAL_CLANG':clang, 'NIL_HOF_CAPTURE':str(folder/(name+'.ll'))}
    if name.endswith('_noinline'): env['NIL_HOF_NOINLINE'] = '1' if name.startswith('map') else '2'
    subprocess.run([str(compiler),'--profile','expr-v5','build',str(source),'-o',str(binary),'-O2'], check=True, capture_output=True, env=env)
    binaries[name] = binary
    assembly = subprocess.check_output(['otool','-tvV',str(binary)],text=True)
    (folder/(name+'.asm')).write_text(assembly)
pattern = b'alpha,beta,gamma\n'
n = 16*1024*1024
data = (pattern*((n+len(pattern)-1)//len(pattern)))[:n]
path = folder/'input.bin'; path.write_bytes(data)
rows = []
for group,size in [(names[:5],n),(names[5:],256),(names[5:],1024),(names[5:],2048)]:
    expected = (str(data.count(b'\n'))+'\n').encode() if size==n else ('['+','.join(str(i) for i in range(1,size+1))+']\n').encode()
    samples = {name:[] for name in group}
    for round_index in range(args.repeats+1):
        order = group[round_index%len(group):]+group[:round_index%len(group)]
        for name in order:
            command = [str(binaries[name]),str(path) if size==n else str(size)]
            start = time.perf_counter_ns(); result = subprocess.run(command,capture_output=True,check=True,timeout=120); elapsed = time.perf_counter_ns()-start
            if result.stdout != expected or result.stderr: raise ValueError(f'{name}/{size}: wrong output')
            if round_index: samples[name].append(elapsed)
    for name,values in samples.items():
        rows.append({'name':name,'size':size,'min_ns':min(values),'median_ns':statistics.median(values),'max_ns':max(values),'samples_ns':values})
if path.read_bytes()!=data: raise ValueError('Input changed')
report = {'repeats':args.repeats,'warmups':1,'rows':rows,'verified':True,'input_sha256':hashlib.sha256(data).hexdigest(),'clang':subprocess.check_output([clang,'--version'],text=True),'sources':{str(p.name):hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.nil')},'method':'Warm whole-process medians, rotating condition order, builds and output validation excluded; no fsync or CPU isolation. map is per-element transformation plus scalar reduction over 16 MiB, compared with identical direct/inline loops. noinline is a benchmark-only IR attribute on the callback in both direct and HOF programs, preserving actual calls. Sort compares library-style comparator insertion sort versus the core sorting algorithm on descending buffers, including construction and identical output formatting; it does not isolate dispatch or establish general library-sort performance.'}
(folder/'results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
