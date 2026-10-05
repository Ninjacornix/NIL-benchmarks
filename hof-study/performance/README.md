# Static HOF performance controls

Run from the main repository with the benchmarks Python environment:

```sh
benchmarks/paired/.venv/bin/python benchmarks/hof-study/performance/run.py --repeats 25 --output /tmp/nil-hof/performance
benchmarks/paired/.venv/bin/python benchmarks/hof-study/performance/materialized.py --repeats 25 --output /tmp/nil-hof/materialized
```

Apple arm64 `otool` is required for disassembly. The scripts build O2 native
executables, perform one warm-up, rotate variants and record whole-process
min/median/max and individual nanosecond samples. Outputs must be outside the
checkout. The first control maps byte classification then reduces at 16 MiB;
the second writes a full mapped byte sequence, checks every byte and verifies a
double-transform round trip. `capture.py` saves actual compiler IR and applies
benchmark-only noinline/disable-tail-calls to the passed function in both direct
and HOF controls; it does not modify the compiler or its runtime.

`sort.nil` is a comparator-driven insertion sort, not the same algorithm as core
sort. It includes construction and exposes conservative buffer-copy costs. Its
timing is informational and must not be described as isolated callback overhead.
No fixture or algorithm tuning was done after timing results.

The Round 13 report includes exact sources, input hashes, versions, samples and
IR/disassembly proof. These author-written benchmark sources use the repository
license; they are not additional corpus tasks.
