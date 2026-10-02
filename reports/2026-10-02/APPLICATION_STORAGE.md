# Expr-v5 file-transform storage measurement

Measured 2026-10-02 on macOS arm64 using Apple Clang 21.0.0. NIL and C++ use
`-O2`; C++ uses C++17. Python: 3.12.11 (main, Jun  4 2025, 17:42:58) [Clang 20.1.4 ].

```sh
./scripts/bench.sh runtime --full --application --repeats 9 --output /tmp/nil-application-storage-measured
```

## Result

Every program reads a binary file, loops over its bytes using `255 - byte`, writes
the result and prints its byte count. Every warmup and sample passed a full-byte
oracle, exact stdout/stderr checks and an unchanged-input check. Results are median
wall-clock milliseconds over nine samples, after one warmup per language/size.

| File bytes | NIL ms | C++ ms | Python ms | NIL / C++ |
|---:|---:|---:|---:|---:|
| 4,096 | 2.683 | 2.463 | 14.397 | 1.09 |
| 1,048,576 | 57.498 | 3.184 | 64.119 | 18.06 |
| 16,777,216 | 887.161 | 12.182 | 760.782 | 72.82 |

NIL completes these workloads without cumulative quota exhaustion, but this
implementation is **not at C++ speed**. At 16 MiB it is also slower than the explicit
Python byte loop. Reclaiming storage and reusing replacements solves feasibility,
not all runtime overhead. This report does not attribute the remaining gap to a
single cause: the current native path includes per-byte root/quota checks, opaque
runtime calls and byte-at-a-time file reads; it was not profiled here.

## Method and limits

Timing includes process startup, cached-filesystem read/write, allocation, transform,
stdout capture and exit. Compilation and output verification are excluded. Execution
order rotates NIL/C++/Python; the filesystem is warmed by setup and verification.
There is no `fsync`, cold-disk control, CPU isolation, energy measurement or statistical
confidence interval. Python uses `bytearray` and an explicit loop, not `bytes.translate`.
C++ uses a byte vector and permits normal compiler vectorization. Samples were
collected locally while compiler validation jobs could still be running; these are
exploratory measurements, not a production performance ranking. Repeated samples
and semantic equivalence do not remove scheduler/filesystem noise.

Only three sizes and one byte operation were measured. No numbers are extrapolated
to other workloads or architectures. This does not measure source tokens, LLM
success/repair/TCR, plugin compression, kernel-only latency or zero-copy I/O.

## Storage boundary

A separate canonical-program check with paths under `/tmp/nil-dynamic-acceptance/`
completed 1 MiB and **33,554,365 bytes**, with complete output verification.
33,554,366 bytes failed with E013 before writing. The 64 MiB limit is unchanged;
the replacement's transient old/result charge and a live destination-path allocation
cap this program around 32 MiB. Exact capacity depends on other live values and
path length. Native v5 runs are unbounded by default; enabling `--bounded` or using
the reference evaluator with a small instruction budget may fail earlier with E008. This is a semantic quota, not an RSS limit.

## Provenance and raw data

Compiler revision at measurement: `04452d65ed3594874d824e6ac913b9a6992d6671`, with
uncommitted storage work. Benchmark revision: `e3c9f3a6828c7394d335fe95194f639878c7731b`,
also dirty. The facade manifest records exact source hashes, platform, interpreter,
compiler version, settings, sample arrays, correctness hashes and binary sizes.
Hashes include the hand-written C runtime. Timing changes are reproducible through
the checked-in runner; committing later does not change which source was measured.

Raw local archive (not uploaded):
`~/.local/share/nil/benchmarks/archive/application-storage-2026-10-02.zip`

SHA-256: `48dde77c0f7e9332a6a8987c1476025d1dfc93f41a11c8d260278ba88a6da287`.

This report is a small summary; raw artifacts remain outside the repository
under the benchmark suite's existing conventions. The archive is local evidence,
not a publicly available release artifact.

## Follow-up

The [checked-runtime optimization measurement](APPLICATION_RUNTIME.md) records
bulk reads, LTO/root changes, directly comparable timings and the new per-stage
profile. This storage report describes the earlier implementation.
