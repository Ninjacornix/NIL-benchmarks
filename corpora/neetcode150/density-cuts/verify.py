"""Validate measurement copies against exactly the frozen NeetCode oracles."""
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import verify as trusted
from support import ROOT,build_helpers

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
 if out.is_relative_to(ROOT):p.error('raw logs outside checkout')
 build_helpers('core_check');helper=ROOT/'target/release/examples/core_check';golden=json.loads((HERE.parent/'goldens.json').read_text());rows=[]
 for t in trusted.tasks():
  task=t['id']
  if not (HERE/'minimal-io'/(task+'.nil')).exists():continue
  with tempfile.TemporaryDirectory(prefix='nil-density-cuts-') as d:
   folder=Path(d);commands={};hashes={};errors=[]
   for cut in ['minimal-io','kernel-host']:
    source=HERE/cut/(task+'.nil');hashes[cut+'/nil']=hashlib.sha256(source.read_bytes()).hexdigest()
    for opt in ['O0','O2']:
     binary=folder/(cut+'-'+opt);c,o,e=trusted.run([str(helper),str(source),'build-'+opt,str(binary)],folder)
     if c or e or o!=b'BUILD\tOK\n':errors.append((cut,opt,e.decode(errors='replace')))
     else:commands[cut+'/'+opt]=[str(binary),'input.bin','output.bin']
    commands[cut+'/reference']=[str(helper),str(source),'input.bin','output.bin','stdout.bin']
   for lang,ext in [('python','py'),('cpp','cpp')]:
    source=HERE/'minimal-io'/(task+'.'+ext);hashes['minimal-io/'+lang]=hashlib.sha256(source.read_bytes()).hexdigest()
    if lang=='python':commands[lang]=[sys.executable,'-I',str(source),'input.bin','output.bin']
    else:
     binary=folder/'cpp';r=subprocess.run([os.environ.get('NIL_CLANG','clang'),'--driver-mode=g++','-std=c++17','-O2',str(source),'-o',str(binary)],capture_output=True)
     if r.returncode:errors.append(('cpp','build',r.stderr.decode()))
     else:commands[lang]=[str(binary),'input.bin','output.bin']
   # Counted HOF kernels are fragments instantiated by their host adapters;
   # a standalone HOF has no first-order entry point. Non-HOF fragments also
   # receive the independent CLI check. Every HOF body executes below.
   kernel=(HERE/'kernels'/(task+'.nil')).read_text()
   if task not in {'3sum','generate-parentheses','letter-combinations-of-a-phone-number'}:
    r=subprocess.run([str(ROOT/'target/release/nil'),'--profile','expr-v5','check',str(HERE/'kernels'/(task+'.nil'))],capture_output=True)
    if r.returncode:errors.append(('nil-kernel','check',r.stderr.decode()))
   checks=[]
   for name,data in trusted.fixtures.cases(t):
    answer=trusted.reference.SOLVERS[task](data);locked=golden[task][name]
    assert trusted.sha(data)==locked['input_sha256'] and trusted.sha(answer)==locked['output_sha256']
    for language,command in commands.items():
     work=folder/(name+'-'+language.replace('/','-'));work.mkdir()
     v=trusted.observed(command,work,data,answer,language.endswith('/reference'))
     checks.append({'fixture':name,'language':language,**v})
   row={'task':task,'hashes':hashes,'errors':errors,'checks':checks,'pass':not errors and len(checks)==8*len(golden[task]) and all(c['pass'] for c in checks)};rows.append(row)
   print(task,'PASS' if row['pass'] else 'FAIL',len(checks),errors,flush=True)
   if not row['pass']:
    print([c for c in checks if not c['pass']],flush=True)
    # Keep failures visible but avoid cascading long native runs.
    break
 report={'tasks':len(rows),'checks':sum(len(r['checks']) for r in rows),'passed':sum(c['pass'] for r in rows for c in r['checks']),'results':rows}
 out.write_text(json.dumps(report,indent=2)+'\n');print('TOTALS',json.dumps({k:v for k,v in report.items() if k!='results'}))
 if len(rows)!=29 or not all(r['pass'] for r in rows):raise SystemExit(1)
if __name__=='__main__':main()
