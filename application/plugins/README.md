# Equality plugin boundary measurement

Compare a preserved pre-migration compiler with the current compiler. This measures
validated source/HIR plugins, not opaque native dispatch. Sources are fixed; the
whole-file case deliberately exposes loss of the old optimized algorithm.

From the NIL root (submodule initialized), obtain the old compiler in an isolated tree:

```sh
git worktree add --detach /tmp/nil-plugin-before c4ffcfb
cargo build --release -p nil --locked --offline --manifest-path /tmp/nil-plugin-before/Cargo.toml --target-dir /tmp/nil-plugin-before-target
benchmarks/paired/.venv/bin/python benchmarks/application/plugins/run.py --before-compiler /tmp/nil-plugin-before-target/release/nil --before-revision c4ffcfb --repeats 25 --output /tmp/nil-plugin-boundary
```

The script builds current NIL, emits before/after IR, compiles O0/O2, generates a
16 MiB deterministic binary file, verifies all results, warms once, alternates
before/after order and retains every wall-time sample and provenance hash. Startup
and I/O are included; compilation is excluded; no CPU isolation. The tiny working
set and actual-file variants are explicitly distinguished. Effective delta/call
includes changed algorithm/optimization costs, not only function dispatch.
Outputs must be outside source checkouts. No third-party Python dependencies.

Existing controls:

```sh
./scripts/bench.sh runtime --full --workloads --workload newlines --workload append --repeats 25 --output /tmp/nil-plugin-controls
./scripts/bench.sh runtime --full --application --repeats 25 --output /tmp/nil-plugin-transform
benchmarks/paired/.venv/bin/python benchmarks/application/keyed/run.py --records --repeats 25 --output /tmp/nil-plugin-keyed
```

[Measured report](../../reports/2026-10-04/V5_PLUGINS.md) includes the material bulk
comparison regression, proof evidence, correctness receipts and all controls.
