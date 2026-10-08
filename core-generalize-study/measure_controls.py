"""Exact historical controls: timings/RSS from plain binaries, charges separately."""
import argparse,hashlib,json,os,re,statistics,subprocess,tempfile,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;SUITE=HERE.parent;ROOT=SUITE.parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--repeats',type=int,default=25);p.add_argument('--compiler',type=Path);p.add_argument('--compiler-revision');p.add_argument('--baseline-compiler',type=Path);p.add_argument('--baseline-revision');a=p.parse_args()
 if bool(a.baseline_compiler)!=bool(a.baseline_revision):p.error('--baseline-compiler and --baseline-revision must be supplied together')
 if bool(a.compiler)!=bool(a.compiler_revision):p.error('--compiler and --compiler-revision must be supplied together')
 if a.repeats<25 or a.output.resolve().is_relative_to(ROOT):p.error('25+ repetitions and outside output required')
 clang=os.environ.get('NIL_CLANG','clang');compiler=a.compiler.resolve() if a.compiler else ROOT/'target/release/nil'
 paths={'append':SUITE/'application/workloads/append.nil','scan':SUITE/'application/workloads/newlines.nil','transform':SUITE/'application/transform.nil'}
 cpppaths={'append':SUITE/'ownership-study/controls.cpp','scan':SUITE/'application/workloads/main.cpp','transform':SUITE/'application/transform.cpp'}
 results={}
 with tempfile.TemporaryDirectory(prefix='nil-control-memory-') as directory:
  folder=Path(directory);data=bytes(range(256))*65536;lines=b'alpha,beta,gamma\n'*1048576
  (folder/'bytes.bin').write_bytes(data);(folder/'lines.bin').write_bytes(lines)
  for name,source in paths.items():
   binaries={m:folder/(m+'-'+name) for m in ['nil','counter','cpp']+(['before'] if a.baseline_compiler else [])}
   for mode in ['nil','counter']+(['before'] if a.baseline_compiler else []):
    env=os.environ.copy()
    if mode=='counter':env.update(NIL_CLANG=str(HERE/'measure_clang.py'),NIL_MEASURE_REAL_CLANG=clang)
    selected=a.baseline_compiler.resolve() if mode=='before' else compiler
    build=subprocess.run([str(selected),'--profile','expr-v5','build',str(source),'-o',str(binaries[mode]),'-O2'],env=env,capture_output=True)
    assert build.returncode==0 and not build.stderr,(name,mode,build.stderr)
   subprocess.run([clang,'--driver-mode=g++','-std=c++17','-O2','-ffp-contract=off',str(cpppaths[name]),'-o',str(binaries['cpp'])],check=True,capture_output=True)
   args=['1048576'] if name=='append' else [str(folder/'lines.bin')] if name=='scan' else [str(folder/'bytes.bin'),str(folder/'transformed.bin')]
   commands={m:[str(b),*args] for m,b in binaries.items()}
   if name in ('append','scan'):commands['cpp'].insert(1,'append' if name=='append' else 'newlines')
   expected=1048576 if name!='transform' else 16777216
   def execute(mode,rss=False):
    start=time.perf_counter_ns();r=subprocess.run((['/usr/bin/time','-l'] if rss else [])+commands[mode],capture_output=True,timeout=120);ms=(time.perf_counter_ns()-start)/1e6
    assert r.returncode==0 and r.stdout==f'{expected}\n'.encode(),(name,mode,r.stdout,r.stderr)
    if name=='transform':assert (folder/'transformed.bin').read_bytes()==bytes(255-x for x in data)
    err=r.stderr.decode()
    if rss:
     match=re.search(r'(\d+)\s+maximum resident set size',err);assert match,err;return ms,int(match[1])
    if mode=='counter':
     match=re.fullmatch(r'NIL_MEASURE peak_observed_live=(\d+) limit=(\d+)\n',err);assert match,err
     return ms,dict(peak_observed_live_bytes=int(match[1]),memory_limit_bytes=int(match[2]),guard_headroom_ratio=int(match[1])/int(match[2]))
    assert not err,err;return ms,None
   _,charge=execute('counter');rss={};samples={m:[] for m in ['nil','cpp']+(['before'] if a.baseline_compiler else [])}
   for mode in samples:
    values=[execute(mode,True)[1] for _ in range(3)];rss[mode]=dict(min_bytes=min(values),median_bytes=statistics.median(values),max_bytes=max(values),samples_bytes=values)
   for rep in range(a.repeats+1):
    modes=list(samples);shift=rep%len(modes);modes=modes[shift:]+modes[:shift]
    for mode in modes:
     ms,_=execute(mode)
     if rep:samples[mode].append(ms)
   timings={m:dict(min_ms=min(v),median_ms=statistics.median(v),max_ms=max(v),samples_ms=v) for m,v in samples.items()}
   results[name]=dict(timings=timings,rss=rss,charge=charge,cpp_time_ratio=timings['nil']['median_ms']/timings['cpp']['median_ms'],cpp_rss_ratio=rss['nil']['median_bytes']/rss['cpp']['median_bytes'])
   print(name,{m:round(v['median_ms'],3) for m,v in timings.items()},'RSS',rss,flush=True)
  roundtrip=folder/'roundtrip.bin';r=subprocess.run([str(binaries['nil']),str(folder/'transformed.bin'),str(roundtrip)],capture_output=True)
  assert r.returncode==0 and r.stdout==b'16777216\n' and not r.stderr and roundtrip.read_bytes()==data
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(dict(schema=1,compiler_revision=a.compiler_revision or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),compiler_binary_sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(),baseline_compiler_revision=a.baseline_revision,baseline_binary_sha256=hashlib.sha256(a.baseline_compiler.read_bytes()).hexdigest() if a.baseline_compiler else None,repeats=a.repeats,rss_unit='bytes (macOS)',metric='Whole-process warm medians; exact historical inputs; same clang/O2; counter binaries excluded from timings/RSS; transform byte-exact and double-transform verified',results=results),indent=2)+'\n')
if __name__=='__main__':main()
