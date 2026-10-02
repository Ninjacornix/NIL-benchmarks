# Expr-v5 checked application runtime: before/after

Measured 2026-10-02 on macOS arm64, Apple Clang 21.0.0; Python 3.12.11.
NIL and C++ use O2 (C++17); NIL now links emitted IR and the C runtime with LTO.
C++ remains the same single-translation-unit source/flags. All three transform
sources are unchanged from the [storage measurement](APPLICATION_STORAGE.md).

```sh
./scripts/bench.sh runtime --full --application --repeats 9 --output /tmp/nil-application-runtime-measured
```

Actual output: `Benchmark artifacts: /private/tmp/nil-application-runtime-measured`.
The manifest status is `passed`. Every warmup/sample passes complete-byte output,
stdout/stderr and unchanged-input checks. Untimed NIL double transforms round-trip
exactly at all three sizes. No numbers below are extrapolated.

## Whole-process results

Medians in milliseconds; nine samples after one warmup, rotating execution order.
Before values are the historical report, not remeasured contemporaneous samples.

| File bytes | NIL before | NIL after | C++ now | Python now | NIL speedup | NIL/C++ now |
|---:|---:|---:|---:|---:|---:|---:|
| 4,096 | 2.683 | 2.603 | 2.490 | 14.004 | 1.03× | 1.05× |
| 1,048,576 | 57.498 | 4.484 | 3.130 | 62.089 | 12.82× | 1.43× |
| 16,777,216 | 887.161 | 34.617 | 12.447 | 771.928 | 25.63× | 2.78× |

Both targets are met: 1 MiB <10 ms and 16 MiB <120 ms. At these two sizes NIL is
within 3× of this C++ implementation and ahead of this explicit Python loop.
That is not exact C++ parity or a general language-performance result.

## Attributed stage profile

Separate whole-process runs of read-only (`file_size.nil` semantics), read+write
(`copy.nil` semantics), and the complete transform, using the same fixtures,
O2, one warmup and nine samples. Stages rotate order separately. Output is checked
after each run; read-only leaves its output sentinel unchanged.

| File bytes | NIL read only ms | NIL read+write ms | NIL transform ms |
|---:|---:|---:|---:|
| 4,096 | 2.657 | 2.631 | 2.603 |
| 1,048,576 | 2.410 | 2.664 | 4.484 |
| 16,777,216 | 4.916 | 8.687 | 34.617 |

The supplied starting profile was roughly 30–40 ms for 1 MiB read-only/copy and
50 ms for the full transform. It was a diagnostic profile, not a statistically
matched baseline. Bulk fread removes the attributed byte-at-a-time read/quota
cost; the regular payload is published without a second full-file copy.

At 16 MiB, transform minus read+write is about 25.93 ms; at 1 MiB about 1.82 ms.
These differences locate the remaining cost primarily in the loop, but separate
process medians are not additive instrumented stage timings. Disassembly shows
NIL's hot path uses scalar `ldrb`/`strb`, length/width checks, live-quota comparison,
root-uniqueness checks and the conditional copy path. The C++ transform uses NEON
`mvn.16b`. NIL has no calls to nil_get/nil_length/nil_set_unique/nil_root_store in
this binary: LTO plus explicit always-inline accessors removed them. The observed remaining work is this scalar checked path, including slow-path
control flow and pointer/header dependence, rather than opaque access calls or
per-byte file I/O. The exact optimizer reason for lack of vectorization was not
measured; no precise percentage is assigned to one branch without a hardware-counter
profile. Startup dominates the 4 KiB runs.

## Semantics and capacity

Reference/native diagnostics and order remain unchanged. Debug/release each pass
188 tests; ASan/UBSan passes 17 application tests. Three seeds compare 576 programs
against 1,152 O0/O2 builds with zero divergences, including aliases/lazy branches,
and observed E012–E018 counts match the starting oracle. See the [compiler verification](https://github.com/Ninjacornix/NIL/blob/feat/application-core/docs/validation/APPLICATION_RUNTIME.md)
for exact commands and counts.

The canonical transform still succeeds at **33,554,365 bytes** for the same
`/tmp/nil-dynamic-acceptance/` paths; 33,554,366 fails E013 before writing.
The unchanged 64 MiB live/transient quota reserves old+result payloads and a live
output path. Other paths/live values can reduce capacity; bounded execution can
fail earlier with E008. Bulk reads and LTO do not raise this limit.

## Method, provenance and limits

Same transform method as the prior report: process startup, cached-file read,
allocation, byte inversion, write, stdout capture and exit. Builds, verification
and double-transform checks are excluded. Python explicitly loops over bytearray;
no translate shortcut. No fsync, cold-disk control, CPU isolation, confidence
interval, hardware counters or kernel-only timing. Final validation campaigns
were finished before measurement; brief example checks overlapped benchmark setup.
Normal OS/scheduler noise remains. Historical/current speedups can include noise.
This establishes this local workload's improvement, not other architectures,
plugins, source-token efficiency, generation correctness or LLM TCR.

Compiler revision: `27394d48b001a5e2948077120ba711e9970ebcb6` (documentation/gitlink dirty;
compiler sources exactly hashed in manifest). Benchmark revision:
`61efdf8b7902d0295079f303758c7397b46d180b` (clean at measurement).
The manifest retains all samples, stage samples, correctness hashes, source
hashes including the C runtime, compiler/interpreter/platform details and binary
sizes. Validation logs and disassembly are retained with the raw artifacts.

Raw local archive, **not uploaded**:
`~/.local/share/nil/benchmarks/archive/application-runtime-2026-10-02.zip`

SHA-256: `7171dac3cba1cfcd614a8445c9a07f2a445dc6286a48acef581cbecb9e1e207c`.
Raw artifacts remain outside both repositories. Checked-in sources/commands
reproduce the experiment; this archive is local evidence, not a public release.
