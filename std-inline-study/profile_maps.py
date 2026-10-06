"""Untimed allocation/copy/hash/probe counts in an external instrumented C copy.
Production compiler/runtime files are never edited. Timings use the original runtime.
"""
import argparse,json,os,shutil,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
p=argparse.ArgumentParser();p.add_argument('--compiler',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
if out.is_relative_to(ROOT):p.error('outside output required')
out.mkdir(parents=True,exist_ok=True);real=shutil.which(os.environ.get('NIL_CLANG','clang'))
wrapper=out/'clang-profile';wrapper.write_text('#!'+sys.executable+'\n'+'''import os,sys
from pathlib import Path
args=sys.argv[1:]
for i,arg in enumerate(args):
 if arg.endswith('.c'):
  s=Path(arg).read_text()
  if 'static uint64_t nil_live;' not in s:continue
  s=s.replace('static uint64_t nil_live;','static uint64_t nil_live;\\nstatic uint64_t p_alloc,p_hash_bytes,p_probes,p_reuse,p_copy,p_copy_bytes;')
  s=s.replace('nil_allocated+=bytes+NIL_SEQUENCE_OVERHEAD; value->next','++p_alloc; nil_allocated+=bytes+NIL_SEQUENCE_OVERHEAD; value->next')
  s=s.replace('uint64_t h=UINT64_C(14695981039346656037);','p_hash_bytes+=(uint64_t)key->length;uint64_t h=UINT64_C(14695981039346656037);')
  s=s.replace('while(table[slot]) {','while(table[slot]) {++p_probes;',1)
  s=s.replace('*bucket=slot;return UINT64_MAX;','++p_probes;*bucket=slot;return UINT64_MAX;',1)
  s=s.replace('if(capacity>NIL_MEMORY_LIMIT-NIL_SEQUENCE_OVERHEAD || nil_live>NIL_MEMORY_LIMIT-capacity-NIL_SEQUENCE_OVERHEAD) nil_fail(6,start,end);','if(capacity>NIL_MEMORY_LIMIT-NIL_SEQUENCE_OVERHEAD || nil_live>NIL_MEMORY_LIMIT-capacity-NIL_SEQUENCE_OVERHEAD) { fprintf(stderr,"quota_entries=%llu prospective=%llu live=%llu\\\\n",(unsigned long long)m->length,(unsigned long long)capacity,(unsigned long long)nil_live); nil_fail(6,start,end); }',1)
  s=s.replace('NilSequence *out=m;','if(reusable)++p_reuse;else{++p_copy;p_copy_bytes+=(uint64_t)m->length*48+nil_map_meta(m)->used;}\\nNilSequence *out=m;',1)
  s=s.replace('static void nil_release(void) {','static void nil_release(void) { fprintf(stderr,"allocations=%llu hash_bytes=%llu probes=%llu reuse=%llu copies=%llu copied_bytes=%llu\\\\n",(unsigned long long)p_alloc,(unsigned long long)p_hash_bytes,(unsigned long long)p_probes,(unsigned long long)p_reuse,(unsigned long long)p_copy,(unsigned long long)p_copy_bytes);')
  dest=Path(os.environ['NIL_MAP_PROFILE_DIR'])/'instrumented.c';dest.write_text(s);args[i]=str(dest)
os.execv(os.environ['NIL_MAP_REAL_CLANG'],[os.environ['NIL_MAP_REAL_CLANG'],*args])
''');wrapper.chmod(0o700)
env={**os.environ,'NIL_CLANG':str(wrapper),'NIL_MAP_REAL_CLANG':real,'NIL_MAP_PROFILE_DIR':str(out)};binary=out/'nil-profile'
built=subprocess.run([str(a.compiler.resolve()),'--profile','expr-v5','build',str(HERE/'maps.nil'),'-O2','-o',str(binary)],env=env,capture_output=True)
if built.returncode:raise RuntimeError(built.stderr.decode())
rows=[]
for w,n in [(8,100000),(64,100000),(64,250000)]:
 path=out/f'keys-{w}-{n}';path.write_bytes(b''.join(i.to_bytes(8,'little')+bytes(w-8) for i in range(n)))
 for op in range(5):
  r=subprocess.run([str(binary),str(path),str(n),str(w),str(op)],capture_output=True)
  if r.returncode:
   if b'E013' not in r.stderr:raise RuntimeError(r.stderr)
   rows.append(dict(key_bytes=w,entries=n,operation=['insert','hit','miss','iterate','update'][op],failure=r.stderr.decode()));continue
  expected=n if op in [0,4] else 3*n*(n-1)//2 if op in [1,3] else 3*n
  assert r.stdout==f'{expected}\n'.encode(),r.stdout
  counts={k:int(v) for k,v in (x.split('=') for x in r.stderr.decode().split())};rows.append(dict(key_bytes=w,entries=n,operation=['insert','hit','miss','iterate','update'][op],**counts))
(out/'results.json').write_text(json.dumps(dict(method='Untimed external copy of emitted C runtime; counters only, no production source edits; same exact checksums.',rows=rows),indent=2)+'\n');print(json.dumps(rows,indent=2))
