"""Strengthen map control: materialized byte map, exact output and round-trip."""
import argparse,hashlib,json,os,shutil,statistics,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--repeats',type=int,default=25);args=p.parse_args()
if args.repeats<15:p.error('>=15 repetitions required')
folder=args.output.resolve();folder.mkdir(parents=True,exist_ok=True)
compiler=ROOT/'target/release/nil';clang=shutil.which(os.environ.get('NIL_CLANG','clang'))
names=['material_inline','material_direct','material_map','material_direct_noinline','material_map_noinline'];binaries={}
for name in names:
 source=HERE/(name.replace('_noinline','')+'.nil');binary=folder/name
 env=os.environ|{'NIL_CLANG':str(HERE/'capture.py'),'NIL_REAL_CLANG':clang,'NIL_HOF_CAPTURE':str(folder/(name+'.ll'))}
 if name.endswith('_noinline'):env['NIL_HOF_NOINLINE']='1' if name.startswith('material_map') else '2'
 subprocess.run([str(compiler),'--profile','expr-v5','build',str(source),'-o',str(binary),'-O2'],capture_output=True,check=True,env=env)
 binaries[name]=binary;(folder/(name+'.asm')).write_text(subprocess.check_output(['otool','-tvV',str(binary)],text=True))
n=16*1024*1024;data=bytes(range(256))*(n//256);transformed=data.translate(bytes(range(255,-1,-1)))
input_path=folder/'input.bin';output=folder/'output.bin';input_path.write_bytes(data);samples={name:[] for name in names}
for r in range(args.repeats+1):
 order=names[r%len(names):]+names[:r%len(names)]
 for name in order:
  output.write_bytes(b'sentinel');start=time.perf_counter_ns();result=subprocess.run([str(binaries[name]),str(input_path),str(output)],capture_output=True,check=True,timeout=120);elapsed=time.perf_counter_ns()-start
  assert result.stdout==f'{n}\n'.encode() and not result.stderr and output.read_bytes()==transformed,name
  if r:samples[name].append(elapsed)
assert input_path.read_bytes()==data
for name in names:
 output.write_bytes(transformed);roundtrip=folder/'roundtrip.bin'
 result=subprocess.run([str(binaries[name]),str(output),str(roundtrip)],capture_output=True,check=True);assert result.stdout==f'{n}\n'.encode() and not result.stderr and roundtrip.read_bytes()==data
report={'repeats':args.repeats,'warmups':1,'input_bytes':n,'output_byte_exact':True,'double_transform_roundtrip':True,'input_sha256':hashlib.sha256(data).hexdigest(),'output_sha256':hashlib.sha256(transformed).hexdigest(),'rows':[{'name':name,'min_ns':min(v),'median_ns':statistics.median(v),'max_ns':max(v),'samples_ns':v} for name,v in samples.items()],'method':'Whole read/map/write processes, cached input, rotating condition order, one warmup; output verification and builds excluded; no fsync or CPU isolation. Callback maps every byte to 255-byte; output verified on every attempt and each variant double-transformed. Both noinline variants use benchmark-only IR attributes; no compiler annotations.'}
(folder/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
