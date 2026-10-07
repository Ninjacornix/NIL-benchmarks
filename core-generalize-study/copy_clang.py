#!/usr/bin/env python3
"""Set an external trace path only in the temporary generated measurement C file."""
import json,os,subprocess,sys,tempfile
from pathlib import Path
args=sys.argv[1:];trace=Path(os.environ['NIL_NATIVE_COPY_TRACE_FILE']).resolve();root=Path(__file__).resolve().parents[2]
if trace.is_relative_to(root):raise SystemExit('copy traces must be outside repository')
clang=os.environ.get('NIL_COPY_REAL_CLANG','clang')
with tempfile.TemporaryDirectory(prefix='nil-copy-runtime-') as d:
 replaced=0; runtime_inputs=0
 for i,arg in enumerate(args):
  path=Path(arg)
  if path.suffix=='.c' and path.is_file():
   runtime_inputs+=1
   source=path.read_text()
   if 'void nil_measure_site(uint64_t site)' in source:
    target=Path(d)/'measured.c';target.write_text('#define NIL_NATIVE_COPY_TRACE_PATH '+json.dumps(str(trace))+'\n'+source);args[i]=str(target);replaced+=1
 if runtime_inputs and replaced!=1:raise SystemExit(f'expected one measured runtime, got {replaced}')
 raise SystemExit(subprocess.run([clang,*args]).returncode)
