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
Runtime measurements include validation before timing. See [paired](paired/README.md)
and [the measurement protocol](PROTOCOL.md) for methodology and limitations.

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
