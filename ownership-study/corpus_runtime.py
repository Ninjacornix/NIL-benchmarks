"""Before/after O2 runtimes for every supported frozen corpus golden, unchanged."""
import argparse,json,os,statistics,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];CORPUS=HERE.parent/'corpora/application-v5'
sys.path.insert(0,str(CORPUS));from external_suite import load_tasks,load_goldens
p=argparse.ArgumentParser();p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--repeats',type=int,default=25);a=p.parse_args()
out=a.output.resolve()
if out.is_relative_to(ROOT) or a.repeats<25:p.error('outside output and at least 25 repeats required')
out.mkdir(parents=True,exist_ok=True);goldens=load_goldens();rows=[]
for task in load_tasks('all'):
 if task['nil_status']=='unsupported':continue
 tid=task['id'];folder=out/tid;folder.mkdir(exist_ok=True);gold=goldens[tid];data=bytes.fromhex(gold['input']);answer=bytes.fromhex(gold['output']);(folder/'input.bin').write_bytes(data)
 bins={}
 for arm,compiler in [('before',a.before),('after',a.after)]:
  binary=folder/arm;subprocess.run([str(compiler.resolve()),'--profile','expr-v5','--bounded','build',str(CORPUS/'programs'/f'{tid}.nil'),'-o',str(binary),'-O2'],check=True,capture_output=True);bins[arm]=binary
 samples={'before':[],'after':[]}
 env={'PATH':os.environ['PATH'],'HOME':str(folder),'TMPDIR':str(folder),**gold.get('environment',{})}
 for repeat in range(a.repeats+1):
  for arm in (['before','after'] if repeat%2==0 else ['after','before']):
   (folder/'output.bin').write_bytes(b'sentinel')
   start=time.perf_counter_ns();r=subprocess.run([str(bins[arm]),'input.bin','output.bin'],cwd=folder,env=env,capture_output=True);ms=(time.perf_counter_ns()-start)/1e6
   if r.returncode or r.stderr or r.stdout!=f'{len(answer)}\n'.encode() or (folder/'output.bin').read_bytes()!=answer or (folder/'input.bin').read_bytes()!=data:raise RuntimeError((tid,arm,r.stderr,r.stdout))
   if repeat:samples[arm].append(ms)
 row={'task':tid,'bytes':len(data),'samples_ms':samples,**{arm:{'min_ms':min(v),'median_ms':statistics.median(v),'max_ms':max(v)} for arm,v in samples.items()}}
 rows.append(row);print(tid,row['before']['median_ms'],row['after']['median_ms'],flush=True)
result={'rows':rows,'repeats':a.repeats,'method':'O2 bounded native, one unchanged frozen golden per supported task, rotating warm whole-process latency, byte-exact verified every run. Small fixtures primarily measure process startup, not throughput.','before':str(a.before),'after':str(a.after)}
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
