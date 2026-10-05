"""Acyclic imports can contain ordinary runtime cycles through callbacks."""
import argparse,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
folder=args.output.resolve();folder.mkdir(parents=True,exist_ok=True)
subprocess.run(['cargo','build','--locked','--offline','-p','nil-compiler'],cwd=ROOT,check=True)
rlib=max((ROOT/'target/debug/deps').glob('libnil_compiler-*.rlib'),key=lambda p:p.stat().st_mtime)
helper=folder/'reference'
subprocess.run(['rustc','--edition=2024',str(HERE/'recursion_reference.rs'),'--extern','nil_compiler='+str(rlib),'-L','dependency='+str(ROOT/'target/debug/deps'),'-o',str(helper)],check=True)
manifest=folder/'library.nil-module';manifest.write_text('nil-module 1\nid 13\nsource library.nil\nexport 0 0\n')
(folder/'library.nil').write_text('([i:i],i)=^a(b)\n')
rows=[]
for n in [10,126,128]:
 source=folder/f'program-{n}.nil';source.write_text(f'=!plugin(13,0,&b,{n})\n1=a==0?0:!plugin(13,0,&b,a-1)+1\n')
 ref=subprocess.check_output([str(helper),str(source),str(manifest)],text=True).strip()
 for opt in ['-O0','-O2']:
  binary=folder/f'native-{n}-{opt}'
  subprocess.run([str(ROOT/'target/release/nil'),'--profile','expr-v5','--module',str(manifest),'--bounded','build',str(source),'-o',str(binary),opt],capture_output=True,check=True)
  r=subprocess.run([str(binary)],capture_output=True)
  if n<128: assert ref==f'Ok(I64({n}))' and r.returncode==0 and r.stdout==f'{n}\n'.encode() and not r.stderr
  else: assert 'E008' in ref and r.returncode!=0 and r.stderr.startswith(b'E008') and not r.stdout
  rows.append(dict(n=n,optimization=opt,reference=ref,status=r.returncode,stdout=r.stdout.decode(),stderr=r.stderr.decode()))
(folder/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
