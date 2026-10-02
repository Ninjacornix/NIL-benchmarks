#!/usr/bin/env python3
"""Benchmark-only IR hook: keep helper calls, leaving compiler semantics untouched."""
import os
from pathlib import Path
import re
import shutil
import sys

arguments = sys.argv[1:]
for argument in arguments:
    if argument.endswith('.ll'):
        path = Path(argument)
        source = path.read_text()
        source, changes = re.subn(
            r'(define [^\n]*@nil_fn2\([^\n]*\)) alwaysinline \{',
            r'\1 noinline "disable-tail-calls"="true" {', source)
        if changes != 1:
            raise RuntimeError('expected one typed helper nil_fn2')
        path.write_text(source)
        shutil.copyfile(path, os.environ['NIL_NOINLINE_IR'])
os.execv(os.environ['NIL_REAL_CLANG'], [os.environ['NIL_REAL_CLANG'], *arguments])
