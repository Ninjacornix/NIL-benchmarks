# Guarded ownership study

Round 16 controls for ADR 036. These are new controls, not rewritten corpus
solutions. `controls.cpp` and the study scripts are original project work under
the benchmark repository's MIT license. Frozen corpus sources and contracts are
read only.

Run from the NIL checkout root, with the benchmark Python environment available:

```sh
cargo build -p nil --release --locked --offline
# Save the baseline executable before changing the compiler:
cp target/release/nil /tmp/nil-before
benchmarks/paired/.venv/bin/python benchmarks/ownership-study/run.py --compiler /tmp/nil-before --output /tmp/ownership-before
benchmarks/paired/.venv/bin/python benchmarks/ownership-study/run.py --compiler target/release/nil --output /tmp/ownership-after
benchmarks/paired/.venv/bin/python benchmarks/ownership-study/historical.py --before /tmp/nil-before --after target/release/nil --output /tmp/ownership-history
benchmarks/paired/.venv/bin/python benchmarks/ownership-study/corpus_runtime.py --before /tmp/nil-before --after target/release/nil --output /tmp/ownership-corpus
benchmarks/paired/.venv/bin/python benchmarks/ownership-study/census.py --output /tmp/ownership-census
```

The recorded baseline was main `80afb64`, benchmark `3c29173`. For reproduction
from a later compiler, build that revision in a separate local checkout first.
Source comparator merge sort requires `std/sort.nil-module` from this round even
when using the baseline compiler; it was already supported by the module/HOF ABI.

All timings are O2 warm whole-process wall time, including process launch and
applicable file I/O, buffer initialization and printing. One warm-up is discarded;
25 rotating repetitions report min/median/max. Same Apple Clang 21 and C++ O2,
reserve-free vector growth, no CPU isolation. Byte output is checked every run.
Insertion baselines use the same insertion algorithm, not `std::sort`. Sorting
controls include deterministic initialization and full array output; these are
not isolated kernel benchmarks. Small frozen corpus fixtures mostly measure
startup. `historical.py` uses the exact old workload source/fixtures and also
checks a double-transform round trip.

`run.py --prepare-only` saves binaries, LLVM IR and arm64 disassembly outside git;
`--run-only` repeats those controls without compilation. Outputs must be outside
the checkout. Token density, model efficiency and static uniqueness throughout
arbitrary callees are not measured here. The census distinguishes 52 sites,
41 semantic last uses and only 7 closed fresh call-entry proofs. Runtime guards
remain mandatory after callees create aliases.

See [results and limits](../reports/2026-10-06/OWNERSHIP.md). Source comparator
sort stays an explicit module prototype; it does not replace core `!sort`.
