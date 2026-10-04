"""Alternating paired builder curves with frozen before/after compilers.
Existing benchmark sources are read unchanged; nested-field is a new diagnostic
shape, not a corpus task/baseline. Whole-process warm medians, verified outputs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NESTED_FIELD = '''record Cell(text:s,value:i)
1=b(!buffer[Cell](1,Cell("",0)),a)
(v[Cell],i)=@(a,b,0;c<b;a[0:Cell(!concat(a[0].text,"x"),c)],b,c+1;#a[0].text)
'''


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--before-compiler', type=Path, required=True)
    ap.add_argument('--after-compiler', type=Path, default=ROOT/'target/release/nil')
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--repeats', type=int, default=25)
    args=ap.parse_args()
    out=args.output.resolve()
    if out.is_relative_to(ROOT):ap.error('output must be outside checkout')
    if args.repeats<9:ap.error('at least nine repeats')
    out.mkdir(parents=True,exist_ok=True)
    nested=out/'nested-field.nil';nested.write_text(NESTED_FIELD)
    sources={'record-append':HERE.parent/'keyed/record-append.nil',
             'nested-build':HERE/'nested-build.nil',
             'nested-build-shared':HERE/'nested-build-shared.nil',
             'nested-field':nested}
    compilers={'before':args.before_compiler.resolve(),'after':args.after_compiler.resolve()}
    rows=[]
    for name,source in sources.items():
        binaries={}
        for variant,compiler in compilers.items():
            exe=out/(name+'-'+variant)
            subprocess.run([str(compiler),'--profile','expr-v5','build',str(source),'-O2','-o',str(exe)],cwd=ROOT,check=True)
            (out/(name+'-'+variant+'.ll')).write_bytes(subprocess.check_output([str(compiler),'--profile','expr-v5','llvm',str(source)]))
            binaries[variant]=exe
        sizes=[1000,4000,16000] if name.startswith('nested-build') else [10000,40000,160000]
        for n in sizes:
            expected=n*(n-1)//2 if name.startswith('nested-build') else n
            samples={k:[] for k in binaries}
            for rep in range(args.repeats+1):
                for variant in (list(binaries) if rep%2==0 else list(reversed(binaries))):
                    start=time.perf_counter_ns();r=subprocess.run([str(binaries[variant]),str(n)],capture_output=True,timeout=120)
                    elapsed=(time.perf_counter_ns()-start)/1e6
                    assert (r.returncode,r.stdout,r.stderr)==(0,f'{expected}\n'.encode(),b''),(name,n,variant,r)
                    if rep:samples[variant].append(elapsed)
            row=dict(workload=name,iterations=n,samples_ms=samples,median_ms={k:statistics.median(v) for k,v in samples.items()})
            rows.append(row);print(json.dumps({k:v for k,v in row.items() if k!='samples_ms'}),flush=True)
    # Larger after-only points distinguish startup from a linear builder cost.
    larger=[]
    for name in ['record-append','nested-build','nested-build-shared']:
        exe=out/(name+'-after')
        for n in [64000,256000]:
            if name=='record-append' and n==64000:continue
            expected=n if name=='record-append' else n*(n-1)//2
            samples=[]
            for rep in range(args.repeats+1):
                start=time.perf_counter_ns();r=subprocess.run([str(exe),str(n)],capture_output=True,timeout=120)
                elapsed=(time.perf_counter_ns()-start)/1e6
                assert (r.returncode,r.stdout,r.stderr)==(0,f'{expected}\n'.encode(),b''),(name,n,r)
                if rep:samples.append(elapsed)
            row=dict(workload=name,iterations=n,median_ms=statistics.median(samples),samples_ms=samples)
            larger.append(row);print(json.dumps({k:v for k,v in row.items() if k!='samples_ms'}),flush=True)
    report=dict(methodology=__doc__,repeats=args.repeats,warmups=1,records=rows,larger_after_only=larger,
                compiler_sha256={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in compilers.items()},
                source_sha256={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in sources.items()})
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
