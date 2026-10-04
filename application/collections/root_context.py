"""Controlled explanation of the historical comparison-dependent copy slowdown.
Use the frozen starting compiler/runtime and identical field-append IR. Change
ONLY NIL_RECORD_BUFFERS from 0 to 1. Both are sound for this old-type workload;
the generic variant adds no actual child visits but changes root inlining/SCCs.
Alternating warm whole-process timings, output checked, no CPU isolation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--compiler', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--repeats', type=int, default=25)
    args=ap.parse_args();out=args.output.resolve()
    if out.is_relative_to(ROOT):ap.error('output must be outside checkout')
    out.mkdir(parents=True,exist_ok=True)
    wrapper=out/'clang-wrapper'
    wrapper.write_text('''#!/usr/bin/env python3
import os,sys
from pathlib import Path
for item in sys.argv[1:]:
 p=Path(item)
 if p.name=='module.ll' and p.is_file():Path(os.environ['CONTEXT_IR']).write_bytes(p.read_bytes())
 if p.name=='runtime.c' and p.is_file():
  text=p.read_text();assert text.count('#define NIL_RECORD_BUFFERS 0')==1
  if os.environ['CONTEXT_GENERIC']=='1':p.write_text(text.replace('#define NIL_RECORD_BUFFERS 0','#define NIL_RECORD_BUFFERS 1'))
os.execv(os.environ['CONTEXT_CLANG'],[os.environ['CONTEXT_CLANG'],*sys.argv[1:]])
''');wrapper.chmod(0o755)
    binaries={}
    for variant,generic in [('specialized','0'),('generic','1')]:
        exe=out/variant;binaries[variant]=exe
        env=dict(os.environ,NIL_CLANG=str(wrapper),CONTEXT_CLANG=shutil.which('clang'),CONTEXT_GENERIC=generic,CONTEXT_IR=str(out/(variant+'.ll')))
        subprocess.run([str(args.compiler.resolve()),'--profile','expr-v5','build',str(HERE.parent/'keyed/record-append.nil'),'-O2','-o',str(exe)],env=env,cwd=ROOT,check=True)
        asm=subprocess.check_output(['otool','-tvV',str(exe)],text=True)
        (out/(variant+'.asm')).write_text(asm)
    assert (out/'specialized.ll').read_bytes()==(out/'generic.ll').read_bytes()
    records=[]
    for n in [10000,40000,160000]:
        samples={k:[] for k in binaries}
        for rep in range(args.repeats+1):
            for variant in (list(binaries) if rep%2==0 else list(reversed(binaries))):
                start=time.perf_counter_ns();r=subprocess.run([str(binaries[variant]),str(n)],capture_output=True,timeout=60)
                elapsed=(time.perf_counter_ns()-start)/1e6
                assert (r.returncode,r.stdout,r.stderr)==(0,f'{n}\n'.encode(),b'')
                if rep:samples[variant].append(elapsed)
        row=dict(iterations=n,median_ms={k:statistics.median(v) for k,v in samples.items()},samples_ms=samples)
        records.append(row);print(json.dumps({k:v for k,v in row.items() if k!='samples_ms'}),flush=True)
    report=dict(methodology=__doc__,records=records,repeats=args.repeats,compiler_sha256=hashlib.sha256(args.compiler.read_bytes()).hexdigest(),
                ir_sha256=hashlib.sha256((out/'specialized.ll').read_bytes()).hexdigest(),
                root_calls={k:sum('bl\t_nil_retain' in line or 'bl\t_nil_drop' in line for line in (out/(k+'.asm')).read_text().splitlines()) for k in binaries})
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
