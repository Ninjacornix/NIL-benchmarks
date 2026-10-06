"""Same <128 conditional builder, source push versus equivalent concat."""
import argparse,json,os,statistics,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
p=argparse.ArgumentParser();p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--repeats',type=int,default=25);a=p.parse_args();out=a.output.resolve()
if out.is_relative_to(ROOT) or a.repeats<25:p.error('outside output, >=25 repeats')
out.mkdir(parents=True,exist_ok=True);data=bytes(range(256))*65536;path=out/'input.bin';path.write_bytes(data);expected=bytes(x for x in data if x<128)+b'\n';commands={}
for arm,compiler in [('before',a.before),('after',a.after)]:
 for form,name in [('concat','w1_inline_once'),('push','w4_push')]:
  binary=out/(arm+'_'+form);subprocess.run([str(compiler.resolve()),'--profile','expr-v5','build',str(ROOT/'benchmarks/builders-study'/f'{name}.nil'),'-O2','-o',str(binary)],check=True,capture_output=True);commands[arm+'_'+form]=[str(binary),str(path)]
cpp_source=out/'cpp.cpp';cpp_source.write_text((ROOT/'benchmarks/ownership-study/controls.cpp').read_text().replace('c%2==0','c<128'));cpp=out/'cpp';subprocess.run([os.environ.get('NIL_CLANG','clang'),'-std=c++17','-O2','-lc++',str(cpp_source),'-o',str(cpp)],check=True,capture_output=True);commands['cpp']=[str(cpp),'filter',str(path)]
samples={k:[] for k in commands};names=list(commands)
for rep in range(a.repeats+1):
 for name in names[rep%len(names):]+names[:rep%len(names)]:
  t=time.perf_counter_ns();r=subprocess.run(commands[name],capture_output=True);ms=(time.perf_counter_ns()-t)/1e6
  if r.returncode or r.stderr or r.stdout!=expected:raise RuntimeError((name,r.stderr,r.stdout[:50]))
  if rep:samples[name].append(ms)
rows={k:dict(min_ms=min(v),median_ms=statistics.median(v),max_ms=max(v),samples_ms=v) for k,v in samples.items()};(out/'results.json').write_text(json.dumps(dict(repeats=a.repeats,rows=rows,method='Warm rotating whole process; startup/read/stdout included; one warmup; byte-exact checked every run; input bytes 0..255 repeated to 16 MiB, keep <128. Same Clang O2, no CPU isolation.'),indent=2)+'\n');print({k:round(v['median_ms'],3) for k,v in rows.items()})
