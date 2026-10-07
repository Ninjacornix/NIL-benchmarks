"""Natural/tuned measurements on admitted problems only. No held-out attempts.

Uninstrumented binaries supply timings/RSS. A separate temporary-runtime overlay
supplies peak observed live charge; its overhead is excluded from timings.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import statistics
import subprocess
import sys
import tempfile
import time
HERE=Path(__file__).resolve().parent;SUITE=HERE.parent;ROOT=SUITE.parent
sys.path.insert(0,str(SUITE/'corpora/neetcode150'))
import fixtures,reference

def run(cmd,cwd,env=None,timeout=120):
 return subprocess.run(cmd,cwd=cwd,env=env,capture_output=True,timeout=timeout)

def checked(cmd,work,data,answer,env=None,measurement=False,rss=False):
 (work/'input.bin').write_bytes(data);(work/'output.bin').unlink(missing_ok=True)
 started=time.perf_counter_ns();p=run((['/usr/bin/time','-l'] if rss else [])+cmd,work,env);ms=(time.perf_counter_ns()-started)/1e6
 assert p.returncode==0,(cmd,p.returncode,p.stderr.decode(errors='replace'))
 assert p.stdout==f'{len(answer)}\n'.encode() and (work/'output.bin').read_bytes()==answer and (work/'input.bin').read_bytes()==data
 err=p.stderr.decode();value=None
 if measurement:
  m=re.fullmatch(r'NIL_MEASURE peak_observed_live=(\d+) limit=(\d+)\n',err);assert m,err
  value={'peak_observed_live_bytes':int(m[1]),'memory_limit_bytes':int(m[2]),'quota_headroom_ratio':int(m[1])/int(m[2])}
 elif rss:
  m=re.search(r'(\d+)\s+maximum resident set size',err);assert m,err
  value=int(m[1])
 else:assert not err,err
 return ms,value

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--repeats',type=int,default=15);p.add_argument('--task',action='append');a=p.parse_args()
 if a.repeats<15:p.error('at least 15 repetitions')
 if a.output.resolve().is_relative_to(ROOT):p.error('raw measurements belong outside git')
 cohort=json.loads((HERE/'NATURAL.json').read_text());tasks=json.loads((SUITE/'corpora/neetcode150/tasks.json').read_text())['tasks'];expected=json.loads((SUITE/'corpora/neetcode150/goldens.json').read_text())
 helper=ROOT/'target/release/examples/core_check';clang=os.environ.get('NIL_CLANG','clang');results=[]
 a.output.parent.mkdir(parents=True,exist_ok=True);progress=a.output.with_suffix('.jsonl');progress.write_text('')
 for row in cohort['tasks']:
  slug=row['task']
  if a.task and slug not in a.task:continue
  task=next(t for t in tasks if t['id']==slug);name,data=list(fixtures.cases(task))[-1];answer=reference.SOLVERS[slug](data)
  assert hashlib.sha256(data).hexdigest()==expected[slug][name]['input_sha256'] and hashlib.sha256(answer).hexdigest()==expected[slug][name]['output_sha256']
  result={'task':slug,'source_hashes':{},'timings':{},'rss':{},'charge':{}}
  with tempfile.TemporaryDirectory(prefix='nil-generalize-') as d:
   folder=Path(d);work=folder/'work';work.mkdir();commands={}
   cpp=folder/'cpp';cpp_source=SUITE/'corpora/neetcode150/programs'/f'{slug}.cpp'
   subprocess.run([clang,'--driver-mode=g++','-std=c++17','-O2','-ffp-contract=off',str(cpp_source),'-o',str(cpp)],check=True,capture_output=True);commands['cpp']=[str(cpp),'input.bin','output.bin']
   for mode,source in [('natural',HERE/'natural'/f'{slug}.nil'),('tuned',SUITE/'corpora/neetcode150/programs'/f'{slug}.nil')]:
    assert hashlib.sha256(source.read_bytes()).hexdigest()==row[mode+'_sha256'];result['source_hashes'][mode]=row[mode+'_sha256']
    binary=folder/mode;build=run([str(helper),str(source),'perf-O2',str(binary)],folder);assert build.returncode==0 and build.stdout==b'BUILD\tOK\n' and not build.stderr,build.stderr
    commands[mode]=[str(binary),'input.bin','output.bin']
    counter=folder/(mode+'-counter');env=os.environ.copy();env['NIL_CLANG']=str(HERE/'measure_clang.py');env['NIL_MEASURE_REAL_CLANG']=clang
    build=run([str(helper),str(source),'perf-O2',str(counter)],folder,env);assert build.returncode==0 and build.stdout==b'BUILD\tOK\n' and not build.stderr,build.stderr
    _,result['charge'][mode]=checked([str(counter),'input.bin','output.bin'],work,data,answer,measurement=True)
   for mode,cmd in commands.items():
    values=[checked(cmd,work,data,answer,rss=True)[1] for _ in range(3)]
    result['rss'][mode]={'min_bytes':min(values),'median_bytes':statistics.median(values),'max_bytes':max(values),'samples_bytes':values}
   samples={k:[] for k in commands}
   for rep in range(a.repeats+1):
    modes=list(commands);modes=modes[rep%3:]+modes[:rep%3]
    for mode in modes:
     elapsed,_=checked(commands[mode],work,data,answer)
     if rep:samples[mode].append(elapsed)
   for mode,values in samples.items():result['timings'][mode]={'min_ms':min(values),'median_ms':statistics.median(values),'max_ms':max(values),'samples_ms':values}
   for mode in ['natural','tuned']:
    ratio=result['timings'][mode]['median_ms']/result['timings']['cpp']['median_ms'];result['timings'][mode]['cpp_ratio']=ratio;result['timings'][mode]['qualified']=ratio<=3
    result['rss'][mode]['cpp_ratio']=result['rss'][mode]['median_bytes']/result['rss']['cpp']['median_bytes']
  results.append(result)
  with progress.open('a') as f:f.write(json.dumps(result)+'\n')
  print(slug,{m:round(result['timings'][m]['cpp_ratio'],3) for m in ['natural','tuned']},flush=True)
 report={'schema':1,'compiler_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'natural_revision':cohort['revision'],'machine':subprocess.check_output(['uname','-a'],text=True).strip(),'clang':subprocess.check_output([clang,'--version'],text=True).splitlines()[0],'repeats':a.repeats,'method':__doc__,'rss_unit':'bytes (macOS /usr/bin/time -l)','held_out_attempted':0,'results':results,'qualified':{m:sum(r['timings'][m]['qualified'] for r in results) for m in ['natural','tuned']}}
 a.output.write_text(json.dumps(report,indent=2)+'\n');print('QUALIFIED',report['qualified'],flush=True)
if __name__=='__main__':main()
