# Lazy-region root retention: full before/after

Measured 2026-10-03, macOS arm64, Apple Clang 21.0.0, Python 3.12.11.
NIL O2 uses LTO; C++17 uses O2. All commits remain local; **nothing was pushed**.
The final 16 MiB newline count meets the <20 ms target without changing syntax,
checks, laziness, immutable values or the 64 MiB capacity-aware quota.

## Commands and provenance

```sh
git worktree add --detach /tmp/nil-lazy-before 09c30a6
NIL_ROOT=/tmp/nil-lazy-before benchmarks/paired/.venv/bin/python benchmarks/bench.py runtime --full --workloads --repeats 9 --output /tmp/nil-lazy-final-before-workloads
NIL_ROOT=/tmp/nil-lazy-before benchmarks/paired/.venv/bin/python benchmarks/bench.py runtime --full --application --repeats 9 --output /tmp/nil-lazy-final-before-transform
./scripts/bench.sh runtime --full --workloads --repeats 9 --output /tmp/nil-lazy-final-after-workloads
./scripts/bench.sh runtime --full --application --repeats 9 --output /tmp/nil-lazy-final-after-transform
```

Each command exits 0 and prints its `/private/tmp/` artifact folder. All four
manifests say `passed`. Recorded compiler revisions are checked: before
`09c30a6ac6f210db8e9b54d10e39cd9bfcc801a9`, after
`a747b46f088725656dcfcb777f5e0012b4321651`.
Benchmark revision `b7d00b531cb2dae66fd48ccd4b0772577501d2b7`
was clean during measurement. Compiler dirty state reflects docs/gitlink only;
all measured before/after source hashes were checked against their actual trees.
Both use Python 3.12.11. The facade is invoked directly for the before checkout
because bench.sh intentionally resets NIL_ROOT to its own checkout.


## Scan and branchless control

Same 16 MiB `alpha,beta,gamma\n` file, cached read, identical loop shape.
Medians in milliseconds; nine samples after one warmup, rotating language order.
The byte-sum control adds each byte; the scan adds a conditional 1 or 0.

| 16 MiB workload | NIL before | NIL after | C++ before | C++ after | Python before | Python after |
|---|---:|---:|---:|---:|---:|---:|
| newlines | 160.733 | 12.310 | 10.133 | 10.230 | 23.943 | 24.265 |
| byte_sum | 10.473 | 10.300 | 8.713 | 8.656 | 56.334 | 56.405 |
| newlines_call | 160.812 | 161.036 | 10.153 | 10.078 | 24.064 | 23.760 |

The direct conditional scan improves **13.06×** to
**12.310 ms**, **1.20× C++**, ahead of Python.
Whole-process scan minus sum medians, divided by 16,777,216 iterations, give
**8.956 ns/iteration before** and **0.120 ns/iteration after**.
These are differences of separate medians, not instrumented instruction costs;
startup/read noise is included. The same calculation for C++ after is
0.094 ns/iteration. No figure is extrapolated.

`newlines_call` calls a scalar identity function in each arm. The current local
proof cannot establish arbitrary callees' nonallocation/nonescape effects, so it
keeps conservative loop transfers. This control remains **161.036 ms**,
about 8.865 ns/iteration above the direct scan.
Its emitted IR is byte-identical to the starting version. C++/Python use the
semantically equivalent direct newline count for this control; it measures NIL's
proof boundary, not a matched language-level function-call microbenchmark.
Future interprocedural summaries could admit pure scalar callees. This goal does
not silently assume those summaries or discard this slow result.

## Every workload and size

All medians in milliseconds. Append sizes are result bytes; report sizes are
records; newlines/byte-sum sizes are file bytes; reduce sizes are i64 elements.
Both language baseline columns are retained rather than showing only NIL changes.

| Workload | Size | NIL before | NIL after | C++ before | C++ after | Python before | Python after |
|---|---:|---:|---:|---:|---:|---:|---:|
| append | 10,000 | 2.751 | 2.793 | 2.493 | 2.559 | 14.359 | 14.918 |
| append | 40,000 | 3.378 | 3.532 | 2.520 | 2.474 | 15.186 | 15.304 |
| append | 160,000 | 5.954 | 5.995 | 2.842 | 2.949 | 18.800 | 18.869 |
| append | 640,000 | 15.976 | 15.933 | 3.893 | 3.904 | 32.548 | 32.826 |
| append | 1,048,576 | 24.615 | 24.552 | 4.973 | 4.857 | 44.422 | 44.238 |
| report | 10,000 | 3.756 | 3.722 | 2.848 | 2.734 | 15.432 | 15.867 |
| report | 40,000 | 6.939 | 6.949 | 3.457 | 3.531 | 18.120 | 18.272 |
| report | 160,000 | 19.675 | 19.543 | 6.761 | 6.629 | 29.988 | 29.689 |
| newlines | 4,096 | 2.659 | 2.493 | 2.484 | 2.454 | 14.128 | 14.341 |
| newlines | 1,048,576 | 12.333 | 3.026 | 2.904 | 2.833 | 14.810 | 14.651 |
| newlines | 16,777,216 | 160.733 | 12.310 | 10.133 | 10.230 | 23.943 | 24.265 |
| reduce | 10,000 | 2.508 | 2.555 | 2.368 | 2.457 | 14.331 | 14.392 |
| reduce | 100,000 | 2.636 | 2.676 | 2.533 | 2.545 | 15.252 | 14.804 |
| reduce | 1,000,000 | 3.671 | 3.585 | 3.139 | 3.264 | 19.951 | 19.735 |
| byte_sum | 16,777,216 | 10.473 | 10.300 | 8.713 | 8.656 | 56.334 | 56.405 |
| newlines_call | 16,777,216 | 160.812 | 161.036 | 10.153 | 10.078 | 24.064 | 23.760 |
| transform | 4,096 | 2.577 | 2.642 | 2.452 | 2.497 | 14.272 | 14.660 |
| transform | 1,048,576 | 4.832 | 4.749 | 3.182 | 3.110 | 65.125 | 62.226 |
| transform | 16,777,216 | 35.144 | 35.010 | 12.421 | 12.371 | 768.496 | 797.776 |

NIL loses to C++ in **every final measured row** by these medians. At small sizes
startup dominates and tiny differences do not establish a kernel ranking. NIL
beats Python in all primary workloads and byte-sum; **the scalar-callee control
still loses to Python**. Large-case losses include append (~5.05× C++), formatted
report (~2.95×), reduction (~1.10×), transform (~2.83×) and the conservative call
scan (~15.98×). Root removal does not establish general C++ parity.

Append still incurs checked concat, RHS allocation and root bookkeeping. Report
adds snprintf-based formatting/sequence allocation; reduction and transform retain
checked scalar access. Calls, intrinsics, sequence-returning arms and nested loops
remain unproved by the local scalar-region analysis. No hardware-counter profile
assigns exact percentages to each residual cost.

## Append and transform non-regression evidence

The append curve remains approximately linear: 2.793 / 3.532 / 5.995 / 15.933 ms
at 10k / 40k / 160k / 640k; 1 MiB is **24.552 ms** versus **24.615 ms** before.
At 160k→640k and 640k→1 MiB, added time per added byte is approximately 20.7 and
21.1 ns. Small-size median increases are retained in the table, not hidden.
The final append IR is byte-identical to before, SHA-256
`fde97ab4d41c82c7f7f762a8f670f21700379d98dbca6c62319bb6013f39e945`.

Transform medians are **2.642 / 4.749 / 35.010 ms** at 4 KiB / 1 MiB / 16 MiB,
versus **2.577 / 4.832 / 35.144 ms** before. The 4 KiB median is nominally 2.5%
higher; larger cases are slightly lower. Whole-process samples fluctuate; this
is not a proof of exact timing equality. Transform IR is byte-identical, SHA-256
`632f7d1fc9d70615bd0ced53c9dbb2435424a7b476c6133f59a824f413aff568`,
and C runtime/flags are unchanged. There is no changed append/transform lowered
program in the final implementation. All outputs are byte-exact, append contents
are checked at every size, and double transforms round-trip at every file size.

## Placement discovery and retained prototype results

The first implementation applied borrow elision to all nonallocating scalar
regions, including non-lazy condition/finish regions in unproved allocating loops.
Its 16 MiB scan measured 12.320 ms, but append measured 26.184 ms at 1 MiB versus
24.167 ms in that cohort (8.3% higher). IR inspection shows two finish-region
stores and one slot removed in append, outside its continuing path. This changed
code generation; no counter profile establishes why the median rose.

The final implementation retains the unchanged recursive scalar proof but applies
borrowing at lazy edges and fully proved loop conditions. Other condition/finish
regions in unproved allocating loops retain their original transfer protocol.
This preserves append/transform IR exactly. The placement decision is general,
not keyed to a program, and is documented in ADR 019. It was made for measured
performance; all correctness tests had passed before it. Final debug/release,
sanitizers and three differential seeds were rerun afterward. No single-use
proof was narrowed to hide an unsound case.

All prototype medians remain here and in raw artifacts (different cohort):

| Workload | Size | Prototype NIL | C++ | Python |
|---|---:|---:|---:|---:|
| append | 10,000 | 2.839 | 2.428 | 14.539 |
| append | 40,000 | 3.491 | 2.508 | 15.115 |
| append | 160,000 | 6.165 | 2.812 | 18.450 |
| append | 640,000 | 17.037 | 3.822 | 32.149 |
| append | 1,048,576 | 26.184 | 4.735 | 42.763 |
| report | 10,000 | 3.646 | 2.690 | 15.009 |
| report | 40,000 | 6.688 | 3.410 | 17.903 |
| report | 160,000 | 19.114 | 6.441 | 29.155 |
| newlines | 4,096 | 2.568 | 2.488 | 13.909 |
| newlines | 1,048,576 | 3.163 | 2.947 | 14.581 |
| newlines | 16,777,216 | 12.320 | 10.238 | 24.027 |
| reduce | 10,000 | 2.443 | 2.494 | 14.279 |
| reduce | 100,000 | 2.626 | 2.489 | 14.502 |
| reduce | 1,000,000 | 3.631 | 3.237 | 19.590 |
| byte_sum | 16,777,216 | 10.319 | 8.726 | 55.910 |
| newlines_call | 16,777,216 | 84.473 | 10.026 | 23.685 |
| transform | 4,096 | 2.561 | 2.463 | 14.258 |
| transform | 1,048,576 | 4.552 | 2.956 | 62.068 |
| transform | 16,777,216 | 34.869 | 11.918 | 781.209 |

The prototype also measured 84.473 ms for the unproved call scan due to broader
condition-region borrowing. That extra optimization was not kept when preserving
unproved-loop protocols. Its final 161.036 ms cost is explicitly reported.
No samples were deleted or a fastest run selected as the final result.

## Correctness and IR evidence

Debug/release CI each pass **202 tests**, no warnings; ASan/UBSan passes **25 native
application tests** (leak detection disabled). Three seeds compare **768 programs**
against **1,536 O0/O2 builds**, zero divergences. Per seed E012–E018 counts are
20 / 12 / 16 / 12 / 16 / 12 / 12, plus 156 successes. All nine intrinsics and new
nested lazy/effect/old-read families are exercised. See
[exact compiler commands](../../../docs/validation/LAZY_REGIONS.md).

The [actual lowered IR](../../../docs/architecture/SCALAR_LAZY_IR.md) removes
six root stores per continuing scan iteration. Roots remain at setup/exit;
CFG branches, selected-arm instructions and phi joins remain. Semantic capture
liveness, checks, instruction ticks and effect ordering are unchanged. Tests
cover unselected division/bounds traps, short-circuit conditional forms, no
unselected host output, ordered effects around/inside branches, failure after
prior effects, and live captures across allocation, all at O0/O2.

Sanitizers/differential campaigns found no runtime defect. New test-authoring
errors (unsupported operator spelling, wrong division code, a generator function
ID typo) were corrected; a preliminary oracle's assumed newline count was also
corrected. These were harness mistakes, not compiler-semantic changes.

Provenance review also corrected the earlier APPLICATION_BUILDERS report: its
supposed matched starting-source run was actually another new-source run because
bench.sh resets NIL_ROOT. The manifest proves this. Historical labels/evidence
were corrected without changing raw data. This report verifies actual revisions,
Python versions and source hashes for every final before/after manifest.

## Method and scope

Same whole-process method as APPLICATION_BUILDERS: one warmup, nine samples,
rotating NIL/C++/Python order, cached files, stdout capture and verified output.
Before and after compiler versions are separate cohorts, not interleaved pairs.
No CPU isolation, cold-disk control, fsync, confidence intervals, kernel-only
measurement or counter attribution. Heavy correctness jobs finished before both
prototype and final timings. Normal scheduler/cache/thermal variation remains.
Python append uses bytearray loops, reports join formatted lines, newline counting
uses bytes.count, reduction uses list/sum and byte-sum uses sum(bytes). Transform
uses the same explicit Python byte loop as earlier reports. C++ uses native
strings/vectors and scans; these are semantic equivalents, not identical algorithms.
Builds, oracle checks and round trips are outside timing. No syntax or SIMD builtin
was added to avoid the conditional. No check, capability, quota or earlier profile
was weakened. The unchanged 64 MiB limit still caps applications; no views, plugin
ABI or user-visible ownership syntax was introduced.

Raw archive, local only and **not uploaded**:
`~/.local/share/nil/benchmarks/archive/lazy-regions-2026-10-03.zip`

SHA-256: `081756047c480e940aafe650ea7a9551d1a0d6d4088038b5c6d77d1dd02898bb`.

The archive retains every sample from initial/final cohorts, manifests, logs,
actual IR and the prototype diff. Sources/commands reproduce the fixtures;
archived revisions and hashes identify what was measured. This establishes the
local scalar-lazy improvement and exposes the call boundary, not general C++
parity, other architectures, source-token savings, model correctness or LLM TCR.

