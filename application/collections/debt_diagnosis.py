"""Runtime-only field-append attribution, with identical LLVM IR.
Counters/timers instrument allocation, reclamation and payload copying. These
perturb code generation, so component timings are diagnosis, not headline results.
Uninstrumented paired controls remain the performance evidence.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREFIX = r'''
static uint64_t diag_malloc_count,diag_malloc_ns,diag_free_count,diag_free_ns;
static uint64_t diag_copy_count,diag_copy_bytes,diag_copy_ns,diag_collect_visits,diag_child_visits;
static uint64_t diag_clock(void) { struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return (uint64_t)t.tv_sec*1000000000+t.tv_nsec; }
static void *diag_malloc(size_t n) { uint64_t t=diag_clock();void *p=malloc(n);diag_malloc_ns+=diag_clock()-t;diag_malloc_count++;return p; }
static void diag_free(void *p) { uint64_t t=diag_clock();free(p);diag_free_ns+=diag_clock()-t;diag_free_count++; }
static void *diag_copy(void *a,const void *b,size_t n) { uint64_t t=diag_clock();void *p=memcpy(a,b,n);diag_copy_ns+=diag_clock()-t;diag_copy_count++;diag_copy_bytes+=n;return p; }
__attribute__((destructor)) static void diag_report(void) {
 fprintf(stderr,"{\"malloc_count\":%llu,\"malloc_ns\":%llu,\"free_count\":%llu,\"free_ns\":%llu,\"copy_count\":%llu,\"copy_bytes\":%llu,\"copy_ns\":%llu,\"collect_visits\":%llu,\"child_visits\":%llu}\n",
 (unsigned long long)diag_malloc_count,(unsigned long long)diag_malloc_ns,(unsigned long long)diag_free_count,(unsigned long long)diag_free_ns,(unsigned long long)diag_copy_count,(unsigned long long)diag_copy_bytes,(unsigned long long)diag_copy_ns,(unsigned long long)diag_collect_visits,(unsigned long long)diag_child_visits);
}
#define malloc diag_malloc
#define free diag_free
#define memcpy diag_copy
'''

def instrument(source):
    source = source.replace('NilSequence *value=*link;', 'diag_collect_visits++;NilSequence *value=*link;')
    source = source.replace('for(int64_t i=0;i<v->length;i++) nil_row_roots', 'for(int64_t i=0;i<v->length;i++,diag_child_visits++) nil_row_roots')
    # Instrument only application.c; keep the generated entry driver unmodified.
    return PREFIX + source + '\n#undef malloc\n#undef free\n#undef memcpy\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--repeats', type=int, default=9)
    ap.add_argument('--alignment', type=int, choices=[16,64,4096], help='Diagnostic-only controlled allocator alignment')
    args = ap.parse_args()
    out = args.output.resolve()
    if out.is_relative_to(ROOT): ap.error('output must be outside checkout')
    out.mkdir(parents=True, exist_ok=True)
    current = ROOT / 'crates/nil-llvm/src/application.c'
    wrapper = out / 'clang-wrapper'
    wrapper.write_text('''#!/usr/bin/env python3
import os,sys
from pathlib import Path
for item in sys.argv[1:]:
 p=Path(item)
 if p.name=='module.ll' and p.is_file():Path(os.environ['DIAG_IR']).write_bytes(p.read_bytes())
 if p.name=='runtime.c' and p.is_file():
  text=p.read_text();old=Path(os.environ['DIAG_CURRENT']).read_text()
  assert text.count(old)==1
  p.write_text(text.replace(old,Path(os.environ['DIAG_SOURCE']).read_text()))
os.execv(os.environ['DIAG_CLANG'],[os.environ['DIAG_CLANG'],*sys.argv[1:]])
''')
    wrapper.chmod(0o755)
    records=[]
    for name, revision in [('historical','1689ffe'),('collections','d72a23d'),('current',None)]:
        source = current.read_text() if revision is None else subprocess.check_output(['git','show',revision+':crates/nil-llvm/src/application.c'],cwd=ROOT,text=True)
        c = out / (name+'.c')
        diagnostic = instrument(source)
        if args.alignment:
            diagnostic = diagnostic.replace('void *p=malloc(n);', f'void *p=NULL;if(posix_memalign(&p,{args.alignment},n))p=NULL;')
        c.write_text(diagnostic)
        env=dict(os.environ,NIL_CLANG=str(wrapper),DIAG_IR=str(out/(name+'.ll')),DIAG_CURRENT=str(current),DIAG_SOURCE=str(c),DIAG_CLANG=shutil.which('clang'))
        exe = out / name
        subprocess.run([str(ROOT/'target/release/nil'),'--profile','expr-v5','build',str(HERE.parent/'keyed/record-append.nil'),'-O2','-o',str(exe)],cwd=ROOT,env=env,check=True)
        for n in [10000,40000,160000]:
            samples=[]
            for _ in range(args.repeats):
                r=subprocess.run([str(exe),str(n)],capture_output=True,check=True)
                assert r.stdout==f'{n}\n'.encode()
                samples.append(json.loads(r.stderr))
            row=dict(runtime=name,revision=revision,iterations=n,samples=samples,medians={k:statistics.median(s[k] for s in samples) for k in samples[0]})
            records.append(row);print(json.dumps({k:v for k,v in row.items() if k!='samples'}),flush=True)
    assert len({(out/(n+'.ll')).read_bytes() for n in ['historical','collections','current']})==1
    (out/'results.json').write_text(json.dumps(dict(methodology=__doc__,alignment=args.alignment,records=records),indent=2)+'\n')

if __name__=='__main__':main()
