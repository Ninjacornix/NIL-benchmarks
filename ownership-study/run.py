"""Round 16 whole-process paired controls. Raw artifacts stay outside Git."""
import argparse,json,os,statistics,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
p=argparse.ArgumentParser();p.add_argument('--compiler',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--repeats',type=int,default=25);mode=p.add_mutually_exclusive_group();mode.add_argument('--prepare-only',action='store_true');mode.add_argument('--run-only',action='store_true');a=p.parse_args()
if a.repeats<25:p.error('at least 25 repeats')
out=a.output.resolve()
if out.is_relative_to(ROOT):p.error('output must be outside repository')
out.mkdir(parents=True,exist_ok=True)
compiler=a.compiler.resolve();clang=os.environ.get('NIL_CLANG','clang')
data=bytes(range(256))*65536; file=out/'input.bin';file.write_bytes(data)
if a.run_only:
 saved=json.loads((out/'prepared.json').read_text());commands=saved['commands'];proofs=saved['proofs'];failures={};expected={n:(out/(n+'.expected')).read_bytes() for n in commands}
else:
 programs={
 'append': '1=@(\"\",0;b<1048576;!concat(a,\"x\"),b+1;#a)',
 'filter_hand': '(s):s=b(!read(a))\n(s):s=@(a,\"\",0;c<#a;a,a[c]/2*2==a[c]?!concat(b,!bytes(1,a[c])):b,c+1;b)',
 'filter_std': '(s):s=!filter(&b,!read(a))\n1:b=a/2*2==a',
 'map_hand': '(s):s=b(!read(a))\n(s):s=@(a,!bytes(#a,0),0;c<#a;a,b[c:255-a[c]],c+1;b)',
 'map_std': '(s):s=!map(&b,!read(a))\n1=255-a',
 'scan': '(s)=b(!read(a))\n(s)=@(a,0,0;b<#a;a,b+1,c+(a[b]==10?1:0);c)',
 }
 sort=(ROOT/'benchmarks/hof-study/performance/sort.nil').read_text();programs['insertion_hof']=sort
 programs['insertion_hand']='1:v=b(c(a))\n(v):v=@(a,1;b<#a;d(a,b),b+1;a)\n1:v=@(!buffer(a,0),0,a;b<c;a[b:c-b],b+1,c;a)\n(v,i):v=@(a,b;b>0?a[b]<a[b-1]:false;e(a,b),b-1;a)\n(v,i):v=a[b-1:a[b]][b:a[b-1]]'
 programs['transform']=(ROOT/'benchmarks/application/transform.nil').read_text()
 module=ROOT/'std/sort.nil-module'
 fill='1:v=@(!buffer(a,0),0,1;b<#a;a[b:(c*25173+13849)-(c*25173+13849)/65536*65536],b+1,(c*25173+13849)-(c*25173+13849)/65536*65536;a)'
 for n in [1024,65536,1048576]:
  programs['sort_core_'+str(n)]='1:v=!sort(b(a),0)\n'+fill
  programs['sort_source_'+str(n)]='1:v=!7.0(&c,b(a))\n'+fill+'\n2:b=a<b'
 commands={};expected={};proofs={};failures={}
 
 for name,source in programs.items():
  src=out/(name+'.nil');src.write_text(source+'\n');binary=out/name
  subprocess.run([str(compiler),'--profile','expr-v5',*(['--module',str(module)] if name.startswith('sort_source_') else []),'build',str(src),'-o',str(binary),'-O2'],check=True,capture_output=True)
  ir=subprocess.check_output([str(compiler),'--profile','expr-v5',*(['--module',str(module)] if name.startswith('sort_source_') else []),'llvm',str(src)],text=True);(out/(name+'.ll')).write_text(ir)
  asm=subprocess.check_output(['otool','-tvV',str(binary)],text=True);(out/(name+'.asm')).write_text(asm)
  proofs[name]={'vector_cmeq':'cmeq.16b' in asm,'vector_sub':'sub.16b' in asm,'snapshot_calls':ir.count('call ptr @nil_set_unique_capture'),'temporary_calls':ir.count('call ptr @nil_make_temporary')}
  arg=name.rsplit('_',1)[1] if name.startswith('sort_') else '1048576' if name=='append' else '2048' if name.startswith('insertion') else str(file)
  commands[name]=[str(binary),arg,str(out/'transformed.bin')] if name=='transform' else [str(binary),arg]
  expected[name]=(b'1048576\n' if name=='append' else ('['+','.join(str(i) for i in range(1,2049))+']\n').encode() if name.startswith('insertion') else bytes(x for x in data if x%2==0)+b'\n' if name.startswith('filter') else bytes(255-x for x in data)+b'\n' if name.startswith('map') else b'65536\n')
 for name in programs:
  if name=='transform':expected[name]=b'16777216\n'
  if name.startswith('sort_'):
   n=int(name.rsplit('_',1)[1]);v=[];c=1
   for _ in range(n):c=(c*25173+13849)%65536;v.append(c)
   expected[name]=('['+','.join(map(str,sorted(v)))+']\n').encode()
 cpp=out/'controls.cpp';cpp.write_text((HERE/'controls.cpp').read_text());binary=out/'cpp'
 subprocess.run([clang,'-std=c++17','-O2','-lc++',str(cpp),'-o',str(binary)],check=True,capture_output=True)
 for op in ['append','filter','map','insertion']:
  name='cpp_'+op;arg='1048576' if op=='append' else '2048' if op=='insertion' else str(file)
  commands[name]=[str(binary),op,arg];expected[name]=expected[{'filter':'filter_hand','map':'map_hand','insertion':'insertion_hand'}.get(op,op)]
 transform_cpp=out/'cpp_transform'
 subprocess.run([clang,'-std=c++17','-O2','-lc++',str(ROOT/'benchmarks/application/transform.cpp'),'-o',str(transform_cpp)],check=True,capture_output=True)
 commands['cpp_transform']=[str(transform_cpp),str(file),str(out/'transformed.bin')];expected['cpp_transform']=b'16777216\n'
 for n in [1024,65536,1048576]:
  name='cpp_sort_'+str(n);commands[name]=[str(binary),'sort',str(n)];expected[name]=expected['sort_core_'+str(n)]
 for name,value in expected.items():(out/(name+'.expected')).write_bytes(value)
 (out/'prepared.json').write_text(json.dumps({'commands':commands,'proofs':proofs},indent=2)+'\n')
 if a.prepare_only:print('Prepared',len(commands),'controls',out);raise SystemExit(0)
samples={name:[] for name in commands};names=list(commands)
for repeat in range(a.repeats+1):
 for name in names[repeat%len(names):]+names[:repeat%len(names)]:
  if name in failures:continue
  start=time.perf_counter_ns();r=subprocess.run(commands[name],capture_output=True);elapsed=time.perf_counter_ns()-start
  if r.returncode:
   if name.startswith('sort_source_') and r.stderr.startswith(b'E013'):
    failures[name]=r.stderr.decode();continue
   raise RuntimeError((name,r.returncode,r.stderr))
  if r.stderr or r.stdout!=expected[name]:raise RuntimeError((name,r.returncode,r.stderr,r.stdout[:100],expected[name][:100]))
  if name in ['transform','cpp_transform'] and (out/'transformed.bin').read_bytes()!=bytes(255-x for x in data):raise RuntimeError('transform output mismatch')
  if repeat:samples[name].append(elapsed/1e6)
result={'compiler':str(compiler),'clang':subprocess.check_output([clang,'--version'],text=True),'repeats':a.repeats,'input_bytes':len(data),'method':'Rotating warm whole-process wall time; includes startup, read and stdout (capture); byte-exact output checked every run; no CPU isolation. Reserve-free builders. Same insertion algorithm, not std::sort.','proofs':proofs,'failures':failures,'rows':{n:{'min_ms':min(v),'median_ms':statistics.median(v),'max_ms':max(v),'samples_ms':v} for n,v in samples.items() if v}}
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({n:{k:v for k,v in r.items() if k!='samples_ms'} for n,r in result['rows'].items()},indent=2))
