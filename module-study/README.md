# Source module naming study

The naming rule was measured and committed before implementation in ADR 032.
`naming.json` counts a hypothetical rewrite of all local positional calls in the
unchanged 66 supported source files into `!plugin(1,EXPORT,args...)`. It is a
spelling-cost analysis, not a set of typechecked rewrites. It uses pinned GGUF
vocabularies only (no inference) and tiktoken cl100k/o200k without special tokens.

Run from NIL root:

```sh
mkdir -p /tmp/nil-modules
benchmarks/paired/.venv/bin/python benchmarks/module-study/naming.py
# Writes /tmp/nil-modules/naming.json, prints three cuts.
benchmarks/paired/.venv/bin/python benchmarks/module-study/split_tokens.py --output /tmp/module-tokens.json
```

`split_tokens.py` measures the two verified alternate module solutions and separates
source sharing/refactoring, imported reference spelling and manifest cost. Files are
tokenized independently, with shared library source counted once in the bundle;
per-entry totals conservatively include the full library. It never contacts Ollama.
Neither measurement establishes total tokens until a correct generated program.
