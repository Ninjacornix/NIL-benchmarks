#!/usr/bin/env python3
"""Measurement-only Clang wrapper: patch temporary generated runtime, never compiler source.

Peak live charge is sampled after complete root reconciliations, not transient
retain-before-drop counts. Instrumented binaries are for counters, not timings.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
args=sys.argv[1:];temporary=None
for i,arg in enumerate(args):
 path=Path(arg)
 if path.suffix!='.c' or not path.is_file():continue
 text=path.read_text()
 if '#define NIL_MEMORY_LIMIT' not in text:continue
 assert 'static uint64_t nil_live;' in text
 # The observation function precedes the application macro; append reporting
 # after the complete runtime so the configured macro is in scope.
 text=text.replace('static uint64_t nil_live;', '''static uint64_t nil_live;
static uint64_t nil_measure_peak;
static void nil_measure_observe(void) { if(nil_live>nil_measure_peak) nil_measure_peak=nil_live; }''',1)
 text+='''\n__attribute__((destructor)) static void nil_measure_report(void) {
    fprintf(stderr,"NIL_MEASURE peak_observed_live=%" PRIu64 " limit=%" PRIu64 "\\n",nil_measure_peak,NIL_MEMORY_LIMIT);
}'''
 old='if(!nil_roots_dirty) return;'
 assert text.count(old)==1;text=text.replace(old,'if(!nil_roots_dirty) { nil_measure_observe(); return; }')
 old='if(differ) nil_roots_sync_slow(frame);'
 assert text.count(old)==1;text=text.replace(old,old+'\n    nil_measure_observe();')
 temporary=tempfile.TemporaryDirectory(prefix='nil-measure-c-');replacement=Path(temporary.name)/path.name;replacement.write_text(text);args[i]=str(replacement)
 break
try:status=subprocess.call([os.environ.get('NIL_MEASURE_REAL_CLANG','clang'),*args])
finally:
 if temporary:temporary.cleanup()
raise SystemExit(status)
