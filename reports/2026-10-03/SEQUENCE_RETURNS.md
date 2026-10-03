# Sequence-return borrowing and checked scan vectorization

## Result and boundary

At 16 MiB, returning a parameter fell from **342.681 ms to 12.160 ms**.
The borrowing property is computed in HIR before inlining, including recursive
nonallocating groups, and permits sequence aliases as results. It assumes no
arena allocation, mutation, collection or host effects across the entire borrowed
interval. Allocating callers register returned aliases before their next allocation.
No immutable-value, trap, quota or evaluation-order contract changed.

Slices in v5 allocate copies; they are not borrowed subvalues. Slice, fresh and
conditional alias/fresh controls remain conservative: **755.569 / 698.248 /
781.401 ms**. Each calls its helper once per byte; the slice/fresh result is one
byte, not a full-file copy on every iteration. The conditional returns the original
only at index zero and allocates a one-byte slice otherwise, exercising both arms.
These are genuine outstanding allocation/root costs, not solved by this goal.

Inline newline counting fell from **12.281 to 7.566 ms**; scalar leaf from **12.254
to 7.563 ms**. LLVM reports vectorization width 16/interleave 2 and emits
`cmeq.16b`/`cmeq.8b`, absent in the baseline scan. Parameter-return and
sequence-reading helpers still use checked scalar accesses: **12.160 / 12.226 ms**.
Nested computed chunk starts remain checked (**17.192 ms**); forced non-inlined
calls and forced recursive calls cost **19.704 / 49.527 ms**.

## Method and reproducibility

Apple M2, macOS 27 arm64, Rust 1.98.1, Apple Clang 21.0.0, Python 3.12.11.
Before compiler `e922bb4b3026516db848058136081c81dead8315`; after
`03c0f496cc105a61ee16b720b3f34c264f3d0f87`; identical benchmark suite
`49a6ec8635807d034fe15c2bb77839aeac48b8f0`. Source hashes are recorded in
all manifests. Dirty flags reflect the uncommitted submodule pointer/documentation;
compiler sources were committed. Both sides used the same benchmark sources.

Nine timed samples after one warmup, rotating NIL/C++/Python order; compilation
and verification excluded. Whole processes include startup, cached-file I/O,
stdout and exit; no fsync, CPU isolation or cold-disk assertion. NIL O2 uses the
existing LTO runtime build; C++ uses clang++ -std=c++17 -O2. Scan fixture repeats
`alpha,beta,gamma\n`: 16 MiB returns **986895**, not the overseer's unavailable
65643 fixture. Arbitrary-byte fixtures are also verified outside timing.

C++/Python scan references are direct scans for every call shape, not equivalent
allocation/recursion strategies. The noinline/recursive benchmark hook forces
actual helper calls using LLVM attributes; these are benchmark controls, not
language annotations. Python uses bytes.count for newlines and list/sum for
reduction; report generation uses join. These are equivalent tasks, not identical
algorithms. Fast NIL scan times do not establish universal superiority to C++, nor
is this a source-token or LLM experiment. Per-access width specialization and bounds
proof both changed; their isolated percentage contributions were not measured.

```sh
# Baseline: detached worktree at e922bb4; same benchmark checkout outside it.
NIL_ROOT=/tmp/nil-seq-before benchmarks/paired/.venv/bin/python benchmarks/bench.py runtime --full --workloads --repeats 9 --output /tmp/nil-seq-before-workloads
NIL_ROOT=/tmp/nil-seq-before benchmarks/paired/.venv/bin/python benchmarks/bench.py runtime --full --application --repeats 9 --output /tmp/nil-seq-before-transform
benchmarks/paired/.venv/bin/python benchmarks/bench.py runtime --full --workloads --repeats 9 --output /tmp/nil-seq-after-workloads
benchmarks/paired/.venv/bin/python benchmarks/bench.py runtime --full --application --repeats 9 --output /tmp/nil-seq-after-transform
# All four: exit 0, manifest status passed; 25 workload + 3 transform cases per side.
python3 -m unittest discover -s benchmarks/tests -v
# exit 0; 9 tests.
```

## Full matrix

Medians in milliseconds; b/a mean before/after. Scan input sizes are bytes;
append/report/reduce sizes are iterations/elements. The new sequence-return
controls were run against both compiler revisions, not extrapolated.

| Workload | Size | NIL b | NIL a | C++ b | C++ a | Python b | Python a |
|---|---:|---:|---:|---:|---:|---:|---:|
| append | 10,000 | 2.632 | 2.765 | 2.436 | 2.402 | 14.100 | 13.893 |
| append | 40,000 | 3.361 | 3.281 | 2.440 | 2.526 | 14.971 | 14.817 |
| append | 160,000 | 5.856 | 5.829 | 2.730 | 2.804 | 18.429 | 18.484 |
| append | 640,000 | 15.681 | 15.618 | 3.787 | 3.786 | 31.844 | 31.641 |
| append | 1,048,576 | 24.100 | 24.802 | 4.793 | 4.997 | 42.567 | 43.817 |
| report | 10,000 | 3.673 | 3.595 | 2.634 | 2.728 | 14.904 | 14.758 |
| report | 40,000 | 6.943 | 6.727 | 3.599 | 3.444 | 17.937 | 17.641 |
| report | 160,000 | 19.585 | 19.192 | 6.660 | 6.368 | 29.416 | 29.134 |
| newlines | 4,096 | 2.509 | 2.468 | 2.434 | 2.415 | 13.936 | 13.832 |
| newlines | 1,048,576 | 3.034 | 2.881 | 2.848 | 3.083 | 14.713 | 15.115 |
| newlines | 16,777,216 | 12.281 | 7.566 | 9.929 | 10.149 | 23.671 | 23.470 |
| reduce | 10,000 | 2.416 | 2.490 | 2.380 | 2.479 | 13.948 | 13.781 |
| reduce | 100,000 | 2.490 | 2.523 | 2.426 | 2.430 | 14.399 | 14.458 |
| reduce | 1,000,000 | 3.600 | 3.436 | 3.290 | 3.244 | 19.495 | 19.398 |
| byte_sum | 16,777,216 | 10.199 | 6.132 | 8.749 | 8.808 | 55.529 | 56.207 |
| newlines_call | 16,777,216 | 12.279 | 7.592 | 10.081 | 10.164 | 23.638 | 23.807 |
| newlines_leaf | 16,777,216 | 12.254 | 7.563 | 10.061 | 10.256 | 23.724 | 23.723 |
| newlines_noinline | 16,777,216 | 19.796 | 19.704 | 10.028 | 10.094 | 23.635 | 23.559 |
| newlines_recursive | 16,777,216 | 49.519 | 49.527 | 10.030 | 9.984 | 23.499 | 23.355 |
| newlines_nested | 16,777,216 | 17.295 | 17.192 | 9.989 | 10.022 | 23.588 | 23.558 |
| newlines_seq_leaf | 16,777,216 | 12.316 | 12.226 | 10.179 | 9.940 | 23.989 | 23.656 |
| newlines_seq_return | 16,777,216 | 342.681 | 12.160 | 10.404 | 10.005 | 24.076 | 23.356 |
| newlines_slice | 16,777,216 | 758.350 | 755.569 | 10.253 | 10.383 | 24.188 | 24.065 |
| newlines_fresh | 16,777,216 | 695.748 | 698.248 | 10.022 | 10.370 | 23.822 | 24.127 |
| newlines_cond_alloc | 16,777,216 | 789.455 | 781.401 | 10.262 | 10.426 | 23.805 | 23.963 |

NIL loses to C++ on every append, report and reduction row, the 4 KiB newline
scan, forced calls, recursive/nested/sequence-reading/sequence-return controls,
and all allocating-call controls. Append/report retain runtime construction,
formatting, quota and geometric growth costs; reduction includes runtime buffer
construction versus C++ vector construction, with small differences dominated
by startup noise. The exact source of those small reduction gaps was not isolated. Recursive NIL also
loses to Python's direct count. Allocating slice/fresh/conditional controls lose
to Python by roughly 29–33x because they allocate and manage roots per byte;
Python's count does neither. No other workload row loses to Python. Those losses
must not be hidden behind SIMD results for nonallocating inline scans.

## Append and transform regression controls

Append remains linear: 10k / 40k / 160k / 640k take **2.765 / 3.281 / 5.829 /
15.618 ms**; 1 MiB takes **24.802 ms**, versus 24.100 before (+2.9%). This is a
small timing variation, not evidence of identical latency. Emitted append IR is
byte-identical before/after, SHA-256
`fde97ab4d41c82c7f7f762a8f670f21700379d98dbca6c62319bb6013f39e945`.

Transform output is byte-exact; every size passes double-transform round-trip.

| Bytes | NIL b | NIL a | C++ b | C++ a | Python b | Python a |
|---:|---:|---:|---:|---:|---:|---:|
| 4,096 | 2.602 | 2.623 | 2.506 | 2.463 | 14.116 | 14.069 |
| 1,048,576 | 4.501 | 4.549 | 3.109 | 3.265 | 60.942 | 61.313 |
| 16,777,216 | 37.571 | 36.421 | 15.590 | 13.767 | 793.196 | 776.083 |

NIL loses to C++ at all three transform sizes, while beating Python. Relative
to before, 4 KiB/1 MiB medians rose 0.8%/1.1%, and 16 MiB fell 3.1%; no systematic
regression is apparent. Transform IR is byte-identical, SHA-256
`632f7d1fc9d70615bd0ced53c9dbb2435424a7b476c6133f59a824f413aff568`.
Stage medians below are separate whole-process controls, not additive timings.

| Bytes | Read b | Read a | Read/write b | Read/write a |
|---:|---:|---:|---:|---:|
| 4,096 | 3.604 | 3.486 | 4.024 | 3.748 |
| 1,048,576 | 2.444 | 2.530 | 2.697 | 2.655 |
| 16,777,216 | 4.970 | 5.096 | 11.554 | 9.279 |

## Exact vectorization proof and remaining boundary

The emitter proves only this class: sequence state is unchanged, index starts at
a literal nonnegative constant, increments by exactly one, and the condition is
exactly index < length of that same sequence. The entire interval is allocation-
and mutation-free. The 64 MiB quota bounds length far below i64 overflow. Thus
initial nonnegativity and induction, together with the dominating loop condition,
prove every body access in range; no extra failing preheader trap is emitted.
Data/length are extracted in the preheader; direct byte/i64 loads remain in the
body. Facts end before finish, which can observe index == length.

Only known alignment (1 for bytes, 8 for i64) is emitted, backed by a C layout
assertion. No noalias or nonempty dereferenceable promise is added: aliases and
empty sequences remain legal. Computed starts, shifted indices, mismatched
bounds, changing sequences, allocating loops and callee-local reads keep nil_get.
LLVM may inline scalar helpers and vectorize this proved loop; the borrowing
proof itself does not depend on that inlining. Recursion and genuinely allocating
intervals stay conservative. No further performance workstream begins here.

The C runtime still defines unproved access checks and operation/trap semantics;
it is no longer the sole implementation of proved element loads. The emitter
now shares the private sequence layout contract, explicitly asserted in C.

[Actual before/after alias and allocation IR](../../../docs/architecture/SEQUENCE_RETURN_IR.md),
[typed load IR, proof and LLVM remarks](../../../docs/architecture/INDUCTION_READ_IR.md),
[ADR 021](../../../docs/adr/021.md),
[208-test, sanitizer and three-seed differential evidence](../../../docs/validation/SEQUENCE_RETURNS.md).

Review found range facts initially leaking into finish, where index can equal
length; the scope was fixed and regression/fuzz cases added before the final
sanitizer runs. No final sanitizer or differential failure was found. The fuzz
campaign is 80 seeded scenario families, not unrestricted coverage-guided proof.

## Raw evidence

Four passing manifests include every sample, source/tool provenance and output
hashes; IR, vectorization remarks, assembly, CI/sanitizer/fuzz and benchmark logs
are archived locally outside both repositories. No upload or push was performed.
Archive: `/Users/ninjacornix/.local/share/nil/benchmarks/archive/sequence-returns-2026-10-03.zip`.
SHA-256: `8ccc70ace766847dde16928b5245ee6c5d5cb35c48ae9bb92417fd2f6e048d5a`.
Only this concise report and source fixtures are committed; machine-specific
binaries, large data and raw samples stay outside repository history.
