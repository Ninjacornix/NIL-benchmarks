# Expr-v5 incremental builders and broader application performance

Measured 2026-10-02 on macOS arm64, Apple Clang 21.0.0, Python 3.12.11.
NIL O2 uses checked C runtime LTO; C++17 uses O2. These are real whole-process
measurements, not projected kernel timings. All manifests have status `passed`.
Both repositories' commits are **local only; nothing was pushed**.

## Commands and method

```sh
./scripts/bench.sh runtime --full --workloads --repeats 9 --output /tmp/nil-application-builders-measured
./scripts/bench.sh runtime --full --application --repeats 9 --output /tmp/nil-application-builders-transform-measured
git worktree add --detach /tmp/nil-append-baseline ac92743
NIL_ROOT=/tmp/nil-append-baseline ./scripts/bench.sh runtime --full --application --repeats 9 --output /tmp/nil-application-builders-baseline-matched
```

Each exits 0 and prints `Benchmark artifacts: /private/tmp/` followed by its output
folder name. Medians below use nine samples after one warmup, rotating NIL/C++/Python
order. Compilation and verification are excluded. Startup, allocation, cached
filesystem I/O and stdout capture are included; no fsync, cold-disk control, CPU
isolation, confidence intervals or hardware-counter profile. All validation jobs
finished before measurement. Baseline runs follow the new-version runs, rather
than interleaving binaries; scheduler/thermal drift remains possible. This follows
the [existing application protocol](APPLICATION_STORAGE.md).

Every timed process verifies stdout/stderr and its output file; newline input files
remain unchanged. Report bytes are independently generated. Untimed returned-byte
append programs verify every byte at all scaling sizes. Each transform also has a
byte-exact output check and an untimed double-transform round trip.

Python deliberately uses idiomatic join/count/sum for report/newlines/reduce.
Append uses a bytearray append loop in Python and std::string push_back in C++;
NIL uses !concat with a one-byte RHS. C++ report appends decimal lines; Python joins
formatted strings. Newlines reads a file and counts newline bytes, rather than
materializing split views. Reduction constructs and sums an i64 buffer/vector
of ones; Python uses a list and sum. These stress different paths while producing
identical results, but are not identical implementation algorithms. The fixed-fill
reduction says little about arbitrary reductions. Sources are in
`application/workloads/`; the unchanged transform is in `application/`.

## Append scaling

Medians in milliseconds. The historical column is the overseer's supplied
five-sample measurement, not a contemporaneous, matched rerun (its full environment
is unavailable). Current N is an entry integer, not a baked-in constant.

| Appends / result bytes | NIL before (supplied) | NIL now | C++ | Python |
|---:|---:|---:|---:|---:|
| 10,000 | 4.18 | 2.802 | 2.498 | 14.870 |
| 40,000 | 14.60 | 3.541 | 2.603 | 15.525 |
| 160,000 | 292.00 | 6.048 | 2.806 | 18.872 |
| 640,000 | — | 15.999 | 3.931 | 32.584 |
| 1,048,576 | — | 24.445 | 4.894 | 44.518 |

The 1 MiB build is **24.445 ms**, below 50 ms. Between 40k→160k, 160k→640k
and 640k→1 MiB, added time per added byte is approximately 20.9, 20.7 and 20.7 ns.
The curve is approximately affine linear, with process startup dominating small
sizes. This is measured scaling, not an assertion based on source length.
Geometric growth copies the prefix only at capacity changes; spare-room append
copies the RHS. It still performs checked reservations/root tracking and creates
a one-byte RHS each iteration. At 1 MiB NIL loses to C++ by 5.00×; it beats this
Python loop but does not establish C++ parity. Retained aliases and self-concat
still copy; repeated alias-heavy building can remain quadratic.

## Three additional workloads

All measured sizes, medians in milliseconds. Report sizes are record counts;
newlines sizes are file bytes; reduce sizes are i64 elements.

| Workload | Size | NIL | C++ | Python | NIL/C++ |
|---|---:|---:|---:|---:|---:|
| report | 10,000 | 3.877 | 2.668 | 15.623 | 1.45× |
| report | 40,000 | 6.963 | 3.456 | 18.647 | 2.01× |
| report | 160,000 | 19.597 | 6.967 | 30.480 | 2.81× |
| newlines | 4,096 | 2.659 | 2.475 | 14.832 | 1.07× |
| newlines | 1,048,576 | 12.574 | 3.138 | 15.375 | 4.01× |
| newlines | 16,777,216 | 161.873 | 10.692 | 24.807 | 15.14× |
| reduce | 10,000 | 2.547 | 2.480 | 14.689 | 1.03× |
| reduce | 100,000 | 2.638 | 2.517 | 15.047 | 1.05× |
| reduce | 1,000,000 | 3.852 | 3.315 | 20.079 | 1.16× |

NIL loses to C++ in every listed workload/size by the observed medians. Small
startup-dominated differences do not establish a meaningful kernel-speed ranking.
NIL beats Python for append, reports and reduction here. It loses to Python for
16 MiB newline counting (6.53×), despite beating it at the smaller scan sizes.

Why these losses differ:

- Append retains per-operation allocation, full-capacity quota reservation and
  root bookkeeping that std::string lacks, even though growing prefix copies
  are amortized. No check was removed to improve the result.
- Report invokes !format and concat for each decimal record. The C runtime uses
  snprintf plus sequence allocation/root handling; C++ to_string/append avoids
  that immutable-sequence protocol. No counter profile assigns exact percentages.
- The NIL newline loop uses a lazy branch. Existing root retention excludes nested
  lazy regions, so its conservative transfers run each iteration. Disassembly
  shows repeated root-count/live-charge stores and scalar checked ldrb access;
  C++ uses vector cmeq byte comparisons. Python bytes.count is a native scan.
  This attributes the visible work, without claiming a measured breakdown or
  having removed proof obligations to make the benchmark faster.
- Integer reduction uses a simpler identity-state body without a lazy region.
  NIL retains checked element access, while C++ can optimize its vector traversal;
  startup and buffer construction are also included. The observed large-case gap
  is 1.16×, not universal reduction parity.

## Unchanged byte-transform workload

Correction (2026-10-03): the invocation labelled matched starting-source used
bench.sh, which overwrites NIL_ROOT. Its manifest records compiler 97b9971, the
same source as the new run, not ac92743. The following column is therefore a
same-version repeat, not a before/after baseline. Raw data are retained unchanged.
The actual old-source exploratory run below used Python 3.14.6. Historical values from
[the previous report](APPLICATION_RUNTIME.md) are kept separately.

| File bytes | Historical NIL | Repeat NIL now | New NIL | C++ now | Python now | New/repeat |
|---:|---:|---:|---:|---:|---:|---:|
| 4,096 | 2.603 | 2.688 | 2.615 | 2.531 | 14.658 | 0.973× |
| 1,048,576 | 4.484 | 4.668 | 4.793 | 3.059 | 61.609 | 1.027× |
| 16,777,216 | 34.617 | 34.849 | 35.528 | 12.338 | 764.281 | 1.019× |

**Strict non-regression is not proven:** new 1 MiB/16 MiB medians are nominally
2.7%/1.9% higher than the same-version repeat. The sample ranges overlap:
1 MiB new 4.343–4.956 ms versus repeat 4.402–5.224;
16 MiB new 34.526–36.297 versus repeat 34.632–35.680.
No statistical isolation separates code cost from noise. Charging capacity requires
an additional header field and read scratch is shrunk before publication; no
measured percentage is attributed to these changes. It would be incorrect to
claim exact unchanged timings. The prior <10 ms / <120 ms targets remain met.
New NIL/C++ ratios are 1.03× / 1.57× / 2.88×.

Separate NIL stage medians, not additive instrumented timings:

| File bytes | Read only ms | Read+write ms | Transform ms |
|---:|---:|---:|---:|
| 4,096 | 2.769 | 2.976 | 2.615 |
| 1,048,576 | 2.507 | 2.912 | 4.793 |
| 16,777,216 | 5.159 | 9.056 | 35.528 |

The 16 MiB transform minus read+write medians is about 26.47 ms. It remains
primarily a scalar checked loop, as in the prior runtime report.

An exploratory baseline invoked the facade directly with system Python 3.14.6;
it was retained but excluded from the matched comparison because the benchmark
facade normally chooses Python 3.12.11. Its medians are recorded here rather than
silently discarded:

| File bytes | Starting NIL | C++ | Python 3.14.6 |
|---:|---:|---:|---:|
| 4,096 | 2.608 | 2.499 | 20.102 |
| 1,048,576 | 4.720 | 3.092 | 91.358 |
| 16,777,216 | 35.129 | 12.422 | 1187.486 |

## Semantics, limits and correctness

The unchanged 64 MiB limit now charges **capacity × width + 40 bytes** per distinct
live allocation. This intentionally replaces payload + 32 accounting. Copying
and reuse reserve identical full transient capacities before mutation. Growth
doubles until the steady-state left/right/result budget clamps spare capacity;
required length still wins, and cannot bypass admission.

Verified one-byte append maximum: **33,554,372 bytes**; the next append fails E013.
Verified canonical transform maximum: **33,554,353 bytes** with the same 37-byte
output path; the next size fails E013 before writing. The former transform bound
was 33,554,365. Different paths/aliases/live values can reduce either bound;
quota and optional execution limits still cap programs. No views or mutable shared
buffers were introduced. Earlier profiles and the default are unchanged.

Debug/release CI each pass 197 tests with no warnings. ASan/UBSan passes 21 native
application tests. Three seeds compare 672 programs against 1,344 O0/O2 builds,
including eight new append-hostile families, with zero divergences and observed
E012–E018. See [compiler command evidence](../../../docs/validation/APPLICATION_BUILDERS.md).
Code review caught and fixed incidental HIR Vec capacity being charged for literals;
the generator did not catch it. No single-use proof was narrowed to hide a case.

## Provenance and limitations

Compiler source revision: `97b9971a46217eac963c21ea83926a9e2ad64943`
(documentation/gitlink dirty, measured compiler sources exactly hashed).
Benchmark revision: `8d2e9afeac5d9368b5faa91f8b54f814ff91f65b`
(clean during measurement; unpublished local commit).
Exploratory old-source compiler only: `ac92743caa4792413c9a7fa29e1395586e919939`;
the supposed matched baseline actually records `97b9971a46217eac963c21ea83926a9e2ad64943`.
All current measured source hashes were checked against the final source tree.
Manifests retain every sample, environment, revisions and source hashes. Disassembly,
validation logs and boundary/example scripts are retained with raw evidence.

Raw local archive, **not uploaded**:
`~/.local/share/nil/benchmarks/archive/application-builders-2026-10-02.zip`

SHA-256: `6f881f8d65ad6c9fae07abdfc835d4471f177731206b145057a2204fcd31ee0f`.

These results establish linear single-use building and expose workload-specific
losses. They do not establish general C++ parity, other-platform performance,
alias-heavy linearity, source-token savings, model generation success or LLM TCR.
No timing sample was dropped and no failed/slow workload was hidden.

