# NIL benchmarks

Benchmark source, paired programs, C++/Python baselines, tokenizer tools, reports,
and generation experiments for [NIL](https://github.com/Ninjacornix/NIL).
Compiler regression tests live in the compiler repository.

## Run through the compiler submodule

From the NIL checkout:

```sh
git submodule update --init benchmarks
./scripts/bench.sh token --smoke
./scripts/bench.sh runtime --smoke
./scripts/bench.sh generation --mock
```

Token smoke and generation mock use Python's standard library and do not download
models or tokenizers. Runtime smoke requires Rust 1.85+ and Clang; it compares
NIL, C++, and Python results. It is a correctness check, not a timing gate.

## Run from a separate checkout

```sh
git clone git@github.com:Ninjacornix/NIL-benchmarks.git
cd NIL-benchmarks
export NIL_ROOT=/absolute/path/to/NIL
python3 bench.py runtime --smoke
```

Without `NIL_ROOT`, the runner discovers a containing NIL checkout or a sibling
`NIL` directory. Rust helpers are built against that checkout's libraries with a
separate locked manifest. They are not compiler workspace targets.

## Full measurements

```sh
uv sync --project paired --locked
paired/.venv/bin/python bench.py token --full
paired/.venv/bin/python bench.py runtime --full
```

The tokenizer run uses pinned assets; its first execution may download them.
Runtime measurements include validation before timing.
Application workloads can be selected individually from the NIL checkout:

```sh
./scripts/bench.sh runtime --full --workloads --workload newlines_leaf --workload newlines_noinline
./scripts/bench.sh runtime --full --application
```

`--workload` is repeatable and requires `--workloads`. The forced-noinline and
recursive scan controls modify helper LLVM attributes only during benchmarking;
NIL has no user-visible inline annotation. See the
[call-shape study](reports/2026-10-03/CALL_ROOTS.md). To benchmark another compiler
checkout, set `NIL_ROOT` and invoke `bench.py` directly; the compiler's shell wrapper
selects its own checkout. See [paired](paired/README.md)
and [the measurement protocol](PROTOCOL.md) for methodology and limitations.

The [verified v5 application corpus](corpora/application-v5/README.md) includes
24 NIL programs and 25 Python/C++ baselines, executable oracles, a positive JSONL
exporter, and [four-tokenizer density results](reports/2026-10-03/V5_DENSITY.md).
Its runners reuse the generation evaluator/native path and paired tokenizer asset;
Gemma vocabulary-only counting adds a pinned benchmark Python binding because the
existing paired runner had no Gemma tokenizer. Density counting never runs inference.

Generation trials are optional. Read [generation](generation/README.md) first.
The explicit `generation --ollama MODEL` mode uses an already running server and
installed model. Smoke checks never start Ollama or install model weights.

## Results and reproducibility

Raw results default to `~/.local/share/nil/benchmarks/runs/`. Set `NIL_BENCH_HOME`
or pass `--output` to choose an external location. Source checkout directories
are rejected as output locations. Each facade run records compiler and benchmark
Git revisions, dirty state, source hashes, environment, settings, and status.
Do not commit logs, binaries, caches, generated trials, or large JSON datasets.
Publish durable datasets as release archives with manifests and SHA-256 hashes;
CI uses expiring artifacts. Reviewed summaries live in [reports](reports/README.md).
Historical reports retain their original measurement provenance.

## Tests and changes

```sh
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s paired/tests -v
python3 -m unittest discover -s generation/tests -v
```

Use Conventional Commits. Describe methodology changes and validation in PRs.
A compiler PR updating the submodule must pin an existing published suite commit.
Do not claim generation efficiency from source token counts or smoke results.

Application measurements (NIL/C++/Python file transforms, NIL read/read+write stages
and untimed double-transform verification):

```sh
./scripts/bench.sh runtime --full --application --repeats 9
./scripts/bench.sh runtime --smoke --application --repeats 1
```

These include process startup and cached filesystem I/O. See
[the measured method and limitations](reports/2026-10-02/APPLICATION_STORAGE.md).

Incremental builders and broader application paths:

```sh
./scripts/bench.sh runtime --full --workloads --repeats 9
./scripts/bench.sh runtime --smoke --workloads --repeats 1
```

This measures append scaling, formatted reports, newline counting and integer
reduction, with independent output checks. Python uses idiomatic join/count/sum;
the report states these algorithm differences. Whole-process medians include
startup and cached file I/O; they do not establish general language parity.

The workloads mode also measures 16 MiB byte-sum (branchless scan control) and
scalar-callee newline counting (the conservative call boundary). Both use the
same cached file and independent byte-result oracles as the ordinary scan.

The record follow-up can be reproduced with
`paired/.venv/bin/python application/keyed/run.py --records --repeats 25 --output /tmp/nil-record-controls`
from this submodule, after the parent compiler is built. It adds scalar-record map
insertion and record-field append controls without changing the existing keyed
workloads. The latter deliberately exposes conservative copying; it is not a claim
of linear field append. See [records evidence](reports/2026-10-04/V5_RECORDS.md).
