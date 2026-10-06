"""Exact historical NIL sources/fixtures, paired with saved/current compilers."""
import argparse,json,os,statistics,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
p=argparse.ArgumentParser();p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--repeats',type=int,default=25);a=p.parse_args()
out=a.output.resolve()
if out.is_relative_to(ROOT) or a.repeats<25:p.error('outside output, at least 25 repeats')
out.mkdir(parents=True,exist_ok=True);clang=os.environ.get('NIL_CLANG','clang')
bytes_data=bytes(range(256))*65536;scan_data=b'alpha,beta,gamma\n'*1048576
(out/'bytes.bin').write_bytes(bytes_data);(out/'lines.bin').write_bytes(scan_data)
paths={'append':ROOT/'benchmarks/application/workloads/append.nil','scan':ROOT/'benchmarks/application/workloads/newlines.nil','transform':ROOT/'benchmarks/application/transform.nil'}
commands={};expect={};samples={}
for arm,compiler in [('before',a.before),('after',a.after)]:
 for name,src in paths.items():
  key=arm+'_'+name;binary=out/key
  subprocess.run([str(compiler.resolve()),'--profile','expr-v5','build',str(src),'-o',str(binary),'-O2'],check=True,capture_output=True)
  args=['1048576'] if name=='append' else [str(out/'lines.bin')] if name=='scan' else [str(out/'bytes.bin'),str(out/'transformed.bin')]
  commands[key]=[str(binary),*args];expect[key]=1048576 if name!='transform' else 16777216;samples[key]=[]
cpp=out/'cpp';subprocess.run([clang,'-std=c++17','-O2','-lc++',str(HERE/'controls.cpp'),'-o',str(cpp)],check=True,capture_output=True)
cpp_scan=out/'cpp_scan';subprocess.run([clang,'-std=c++17','-O2','-lc++',str(ROOT/'benchmarks/application/workloads/main.cpp'),'-o',str(cpp_scan)],check=True,capture_output=True)
cpp_transform=out/'cpp_transform';subprocess.run([clang,'-std=c++17','-O2','-lc++',str(ROOT/'benchmarks/application/transform.cpp'),'-o',str(cpp_transform)],check=True,capture_output=True)
commands.update(cpp_append=[str(cpp),'append','1048576'],cpp_scan=[str(cpp_scan),'newlines',str(out/'lines.bin')],cpp_transform=[str(cpp_transform),str(out/'bytes.bin'),str(out/'transformed.bin')]);expect.update(cpp_append=1048576,cpp_scan=1048576,cpp_transform=16777216);samples.update(cpp_append=[],cpp_scan=[],cpp_transform=[])
for name in ['append','scan','transform']:
 keys=[arm+'_'+name for arm in ['before','after','cpp']]
 for repeat in range(a.repeats+1):
  for key in keys[repeat%3:]+keys[:repeat%3]:
   t=time.perf_counter_ns();r=subprocess.run(commands[key],capture_output=True);elapsed=(time.perf_counter_ns()-t)/1e6
   if r.returncode or r.stderr or r.stdout!=f'{expect[key]}\n'.encode():raise RuntimeError((key,r.stdout,r.stderr))
   if name=='transform' and (out/'transformed.bin').read_bytes()!=bytes(255-x for x in bytes_data):raise RuntimeError('wrong transform')
   if repeat:samples[key].append(elapsed)
subprocess.run([str(out/'after_transform'),str(out/'transformed.bin'),str(out/'roundtrip.bin')],check=True,capture_output=True)
assert (out/'roundtrip.bin').read_bytes()==bytes_data
rows={n:{'min_ms':min(v),'median_ms':statistics.median(v),'max_ms':max(v),'samples_ms':v} for n,v in samples.items()}
result={'repeats':a.repeats,'rows':rows,'sources':{n:str(p) for n,p in paths.items()},'method':'Exact historical sources, newline alpha/beta/gamma and transform bytes 0..255 fixtures; rotating warm whole-process wall time, byte-exact transform and double-roundtrip verified; append C++ reserve-free vector, scan and transform existing C++ controls. No CPU isolation.'}
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({n:{k:v for k,v in r.items() if k!='samples_ms'} for n,r in rows.items()},indent=2))
