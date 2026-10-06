"""Round 18 fixed map matrix; raw output outside checkouts."""
import argparse,json,os,statistics,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
p=argparse.ArgumentParser();p.add_argument('--compiler',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--repeats',type=int,default=25);a=p.parse_args();out=a.output.resolve()
if out.is_relative_to(ROOT) or a.repeats<25:p.error('outside output and >=25 repeats required')
out.mkdir(parents=True,exist_ok=True);clang=os.environ.get('NIL_CLANG','clang');cpp=out/'cpp';nil=out/'nil'
subprocess.run([clang,'-std=c++17','-O2','-lc++',str(HERE/'maps.cpp'),'-o',str(cpp)],check=True,capture_output=True)
profile=out/'cpp-profile';subprocess.run([clang,'-std=c++17','-O2','-lc++','-DNIL_MAP_PROFILE=1',str(HERE/'maps.cpp'),'-o',str(profile)],check=True,capture_output=True)
subprocess.run([str(a.compiler.resolve()),'--profile','expr-v5','build',str(HERE/'maps.nil'),'-O2','-o',str(nil)],check=True,capture_output=True)
rows=[]
for w in [8,64]:
 for n in [10000,100000,250000]:
  data=b''.join(i.to_bytes(8,'little')+bytes(w-8) for i in range(n));path=out/f'keys-{w}-{n}';path.write_bytes(data)
  profile_counts={op:subprocess.check_output([str(profile),str(path),str(n),str(w),str(op),'ordered'],stderr=subprocess.PIPE) for op in []}
  profile_counts={}
  for op in range(5):
   result=subprocess.run([str(profile),str(path),str(n),str(w),str(op),'ordered'],capture_output=True,check=True);profile_counts[op]=result.stderr.decode().strip()
  samples={(lang,op):[] for lang in ['nil','ordered','unordered'] for op in range(5)};errors={};diagnostics={}
  names=list(samples)
  for rep in range(a.repeats+1):
   for lang,op in names[rep%len(names):]+names[:rep%len(names)]:
    if (lang,op) in errors:continue
    command=[str(nil),str(path),str(n),str(w),str(op)] if lang=='nil' else [str(cpp),str(path),str(n),str(w),str(op),lang]
    t=time.perf_counter_ns();r=subprocess.run(command,capture_output=True);ms=(time.perf_counter_ns()-t)/1e6
    expected=n if op in [0,4] else 3*n*(n-1)//2 if op in [1,3] else 3*n
    if r.returncode:
     if lang=='nil' and r.stderr.startswith(b'E013'):errors[(lang,op)]=r.stderr.decode();continue
     raise RuntimeError((lang,w,n,op,r.stdout,r.stderr))
    if r.stdout!=f'{expected}\n'.encode() or (lang=='nil' and r.stderr):raise RuntimeError((lang,w,n,op,r.stdout,r.stderr,expected))
    if rep:samples[(lang,op)].append(ms)
    diagnostics[(lang,op)]=r.stderr.decode().strip()
  for (lang,op),values in samples.items():
   row=dict(language=lang,key_bytes=w,entries=n,operation=['insert','hit','miss','iterate','update'][op],diagnostic=errors.get((lang,op)),probe_counters=profile_counts[op] if lang=='ordered' else None)
   if values:
    stats=lambda vs:dict(min_ms=min(vs),median_ms=statistics.median(vs),max_ms=max(vs))
    base=samples[(lang,0)];marginal=[v if op==0 else v-base[i] for i,v in enumerate(values)]
    row.update(stats(values),samples_ms=values,marginal_ns=dict(min=min(marginal)*1e6/(n if op==0 else 3*n),median=statistics.median(marginal)*1e6/(n if op==0 else 3*n),max=max(marginal)*1e6/(n if op==0 else 3*n)))
   rows.append(row)
  print(w,n,'done',flush=True)
result=dict(repeats=a.repeats,rows=rows,method='Whole process, warm rotating wall time; read/build included. Noninsert ns subtract paired build latency and divide by 3N: an estimate, not isolated kernel timing. Same Clang O2, no CPU isolation. C++ materializes query strings like NIL slice; update queries use views in ordered baseline. Every checksum checked. C++ ordered counters/hash-only profile are collected separately without timing the instrumented binary; no quota or immutable copy-on-write in C++ baselines.')
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print('rows',len(rows),'quota failures',sum(bool(r['diagnostic']) for r in rows))
