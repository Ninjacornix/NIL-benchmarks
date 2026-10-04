"""Isolate record-root runtime cost with identical emitted legacy-program IR."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get('NIL_ROOT', HERE.parents[2])).resolve()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repeats', type=int, default=25)
    parser.add_argument('--before', default='1689ffe')
    args = parser.parse_args()
    out = args.output.resolve()
    if out.is_relative_to(ROOT):
        parser.error('Output must be outside checkouts')
    out.mkdir(parents=True, exist_ok=True)
    current = ROOT/'crates/nil-llvm/src/application.c'
    before = out/'before.c'
    before.write_bytes(subprocess.check_output(['git','show',args.before+':crates/nil-llvm/src/application.c'],cwd=ROOT))
    wrapper = out/'clang-wrapper'
    wrapper.write_text('''#!/usr/bin/env python3
import os
from pathlib import Path
import sys
args=sys.argv[1:]
for item in args:
 p=Path(item)
 if p.name=='module.ll' and p.is_file():
  Path(os.environ['NIL_CONTROL_IR']).write_bytes(p.read_bytes())
 if p.name=='runtime.c' and p.is_file() and os.environ['NIL_CONTROL_VARIANT']=='before':
  text=p.read_text();current=Path(os.environ['NIL_CONTROL_CURRENT']).read_text()
  if text.count(current)!=1:raise RuntimeError('runtime composition changed')
  p.write_text(text.replace(current,Path(os.environ['NIL_CONTROL_BEFORE']).read_text()))
os.execv(os.environ['NIL_CONTROL_CLANG'],[os.environ['NIL_CONTROL_CLANG'],*args])
''')
    wrapper.chmod(0o755)
    env = dict(os.environ,NIL_CLANG=str(wrapper),NIL_CONTROL_CURRENT=str(current),NIL_CONTROL_BEFORE=str(before),NIL_CONTROL_CLANG=shutil.which('clang'))
    source = HERE.parent/'workloads/append.nil'
    for variant in ['before','after']:
        env['NIL_CONTROL_VARIANT']=variant
        env['NIL_CONTROL_IR']=str(out/(variant+'.ll'))
        subprocess.run([str(ROOT/'target/release/nil'),'--profile','expr-v5','build',str(source),'-O2','-o',str(out/variant)],env=env,cwd=ROOT,check=True)
    assert (out/'before.ll').read_bytes()==(out/'after.ll').read_bytes(), 'IR changed'
    samples={k:[] for k in ['before','after']}
    for rep in range(args.repeats+1):
        for variant in (['before','after'] if rep%2==0 else ['after','before']):
            start=time.perf_counter_ns()
            result=subprocess.run([str(out/variant),'1048576'],capture_output=True,timeout=60)
            ms=(time.perf_counter_ns()-start)/1e6
            assert (result.returncode,result.stdout,result.stderr)==(0,b'1048576\n',b''), result
            if rep:samples[variant].append(ms)
    report=dict(before_revision=subprocess.check_output(['git','rev-parse',args.before],cwd=ROOT,text=True).strip(),after_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),methodology='Identical current emitted append IR, only application.c replaced by pre-collection runtime; O2/LTO compiler flags unchanged; alternating paired whole-process timing, one warmup, output verified, no CPU isolation. This isolates runtime composition, not a whole historical compiler comparison.',repeats=args.repeats,samples_ms=samples,median_ms={k:statistics.median(v) for k,v in samples.items()},ir_sha256=hashlib.sha256((out/'after.ll').read_bytes()).hexdigest(),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),runtime_sha256={'before':hashlib.sha256(before.read_bytes()).hexdigest(),'after':hashlib.sha256(current.read_bytes()).hexdigest()})
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)


if __name__ == '__main__':
    main()
