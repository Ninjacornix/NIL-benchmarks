"""Sandboxed full-program baseline entry adapter, not included in generated source."""
import runpy
import sys

namespace = runpy.run_path(sys.argv[1])
value = namespace['solve']('input.bin', 'output.bin')
if type(value) is not int:
    raise TypeError('solve must return an integer')
print(value)
