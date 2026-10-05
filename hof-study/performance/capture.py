#!/usr/bin/env python3
"""Benchmark-only capture/noinline hook; no compiler or language annotations."""
import os
from pathlib import Path
import re
import shutil
import sys
for arg in sys.argv[1:]:
    if arg.endswith('.ll'):
        path = Path(arg)
        source = path.read_text()
        target = os.environ.get('NIL_HOF_NOINLINE')
        if target:
            source, count = re.subn(r'(define [^\n]*@nil_fn'+target+r'\([^\n]*\)) (?:alwaysinline )?\{', r'\1 noinline "disable-tail-calls"="true" {', source)
            if count != 1: raise RuntimeError('Expected exactly one callback definition')
            path.write_text(source)
        shutil.copyfile(path, os.environ['NIL_HOF_CAPTURE'])
os.execv(os.environ['NIL_REAL_CLANG'], [os.environ['NIL_REAL_CLANG'], *sys.argv[1:]])
