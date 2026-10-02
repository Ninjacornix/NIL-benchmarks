# Interprocedural borrowing: call-shape controls and full workload set

Measured 2026-10-03 on Apple M2 / macOS arm64, Apple Clang 21.0.0,
Python 3.12.11. NIL O2 uses LTO; C++17 uses O2. All commits are local;
**nothing was pushed**. Scalar leaf factoring meets the <20 ms target:
**162.924 → 12.955 ms** at 16 MiB. This is a partial, sound fix: sequence-returning
helpers remain conservative and expensive; forced real recursion still loses to Python.

## Method and provenance

One warmup and nine samples, medians in milliseconds, rotating NIL/C++/Python
order. Whole processes include startup, checked arguments, cached file I/O and
printing; compilation and independent verification are excluded. No CPU isolation,
fsync or confidence intervals. The scan fixture is the same 16 MiB repeated
`alpha,beta,gamma\n` file in all controls, returning 1,048,576 newlines. This is the
existing suite fixture, not the overseer's unavailable file returning 65,643.
All shapes also count a separate arbitrary 0..255 fixture correctly outside timing.

Scalar leaf passes one byte into the identical comparison. Sequence leaf passes
bytes/index and performs checked get inside the helper. Nested loops process
256-byte chunks. Recursive control passes bytes/index/depth=1, invokes itself
once, and performs the identical comparison at the base case; it does extra call
work, not extra semantic counting. All scan shapes use the same direct C++ scan
and Python `bytes.count` references, **not** C++/Python implementations with matched
call shapes. Byte sum is a separate branchless semantic control (`sum` in Python).

The noinline and recursive controls use a benchmark-only Clang wrapper that adds
`noinline "disable-tail-calls"="true"` to helper `nil_fn2` in emitted LLVM before
compilation. Production NIL syntax/emitter is untouched. LTO and O2 remain enabled.
This deliberately prevents inlining/tail-call elimination; it is not a promise
about LLVM's default heuristic for a large function. The recursive control really
calls itself in the resulting binary. Native tests separately cover bounded
self/mutual/deep recursion at O0/O2.

```sh
git worktree add --detach /tmp/nil-call-before ef6ddf1
NIL_ROOT=/tmp/nil-call-before benchmarks/paired/.venv/bin/python benchmarks/bench.py runtime --full --workloads --repeats 9 --output /tmp/nil-call-final-before-workloads
benchmarks/paired/.venv/bin/python benchmarks/bench.py runtime --full --workloads --repeats 9 --output /tmp/nil-call-final-after-workloads
NIL_ROOT=/tmp/nil-call-before benchmarks/paired/.venv/bin/python benchmarks/bench.py runtime --full --application --repeats 9 --output /tmp/nil-call-final-before-transform
benchmarks/paired/.venv/bin/python benchmarks/bench.py runtime --full --application --repeats 9 --output /tmp/nil-call-final-after-transform
NIL_ROOT=/tmp/nil-call-before benchmarks/paired/.venv/bin/python benchmarks/bench.py runtime --full --workloads --workload newlines_seq_return --repeats 9 --output /tmp/nil-call-final-before-boundary-v2
benchmarks/paired/.venv/bin/python benchmarks/bench.py runtime --full --workloads --workload newlines_seq_return --repeats 9 --output /tmp/nil-call-final-after-boundary-v2
```

All six commands exit 0, print their `/private/tmp/` artifact directory, and record
`status: passed`. Verified compiler revisions: before `ef6ddf1`, after `4f7a99f`.
Workload pairs use benchmark revision `273c8ae`; the supplemental boundary pair
uses `96ea22b`. Transform before uses `273c8ae`, after `bad408e`; transform runner,
NIL/C++/Python inputs match exactly. Relevant benchmark source hashes match within
every pair, as does the C runtime hash. Python is 3.12.11 throughout. Dirty state
on the after compiler is only docs/gitlink. The direct facade preserves NIL_ROOT;
`scripts/bench.sh` resets it and must not select the detached baseline this way.
All validation processes finished before timing.

## Call matrix at 16 MiB

| Workload / input | NIL before | NIL after | C++ before | C++ after | Python before | Python after |
|---|---:|---:|---:|---:|---:|---:|
| Inline conditional | 13.056 | 13.156 | 11.246 | 10.939 | 25.297 | 25.086 |
| Scalar leaf helper | 162.924 | 12.955 | 11.189 | 10.689 | 25.508 | 24.824 |
| Forced non-inline scalar leaf | 162.545 | 20.989 | 10.986 | 10.687 | 25.091 | 25.004 |
| Forced recursive sequence-reading helper | 612.308 | 51.667 | 11.035 | 10.929 | 25.059 | 24.943 |
| Nested 256-byte loops + leaf | 333.076 | 18.015 | 10.986 | 10.907 | 25.193 | 24.915 |
| Sequence-reading leaf helper | 308.991 | 13.051 | 11.011 | 10.628 | 25.118 | 24.666 |
| Identity helpers in lazy arms | 162.901 | 12.914 | 11.037 | 10.671 | 25.127 | 24.899 |
| Sequence-returning identity (conservative) | 340.572 | 345.810 | 10.225 | 10.591 | 24.079 | 24.503 |
| Branchless byte sum | 11.362 | 10.938 | 9.591 | 9.533 | 57.515 | 57.662 |

Leaf and sequence-reading helpers now match inline within timing noise. Forced
non-inline scalar calls add **0.467 ns/iteration** over inline, recursive control
adds **2.295 ns/iteration**, nested loops add **0.290 ns/iteration**. These are
whole-process median differences divided by input bytes, not instrumented cycle
measurements. Inline versus branchless adds **0.132 ns/iteration**. Helpers no
longer pay per-iteration root/live-charge transfers.

Forced non-inline lowering still pays actual scalar calls and prevents loop-wide
vectorization through that call. Recursive disassembly keeps the frame/recursive
call and checked generic-width element read (bounds, length, width branch). Nested
control has additional inner-loop limits/backedges. These are visible remaining
operations; the timings do not isolate a percentage attributable to each.

The sequence-returning identity loop has byte-identical emitted IR before/after, and stays around
346 ms (32.65× direct C++, 14.11× Python). It keeps the full transfer protocol;
scalar-returning classification cannot establish borrowing for its sequence-valued
instructions. Allocation-free sequence-result summaries are further work. This
boundary is explicit, not silently changed to make a fast number.

## Evidence independent of inlining

```sh
target/release/nil --profile expr-v5 llvm benchmarks/application/workloads/newlines_leaf.nil
nm /tmp/nil-call-final-after-workloads/workload-newlines_noinline
otool -tvV /tmp/nil-call-final-after-workloads/workload-newlines_noinline
otool -tvV /tmp/nil-call-final-after-workloads/workload-newlines_recursive
```

Before LLVM optimization, scanner `nil_fn1` changes from nine stores/four slots
(six stores per continuing iteration) to zero stores/no root frame; calls remain.
The sequence-reading helper also loses its two stores/frame. The allocating
file-reading caller keeps four stores. See [actual emitted IR](../../../docs/architecture/CALL_ROOTS_IR.md).

`nm` retains `_nil_fn2` in the noinline binary. Disassembly contains a real
`bl _nil_fn2` in its scanner; the leaf itself is a comparison/cset/ret. Recursive
binary has both a scanner call and a self-call inside `_nil_fn2`, followed by its
checked load path. Raw IR and disassembly are archived. This is a HIR fixed-point
property established before LLVM, not an inliner accident.

## Full existing workload set

| Workload / input | NIL before | NIL after | C++ before | C++ after | Python before | Python after |
|---|---:|---:|---:|---:|---:|---:|
| append / 10,000 | 3.058 | 3.190 | 2.677 | 2.757 | 15.478 | 15.456 |
| append / 40,000 | 3.725 | 3.773 | 2.700 | 2.788 | 16.203 | 16.261 |
| append / 160,000 | 6.352 | 6.294 | 3.040 | 3.120 | 19.733 | 19.481 |
| append / 640,000 | 16.140 | 16.211 | 4.220 | 4.272 | 34.879 | 33.154 |
| append / 1,048,576 | 24.928 | 24.884 | 5.395 | 5.249 | 45.071 | 45.696 |
| report / 10,000 | 3.969 | 4.038 | 3.053 | 2.915 | 15.919 | 15.987 |
| report / 40,000 | 7.297 | 7.111 | 3.776 | 3.926 | 18.846 | 18.637 |
| report / 160,000 | 20.069 | 20.295 | 7.081 | 6.997 | 31.187 | 31.151 |
| newlines / 4,096 | 2.679 | 2.919 | 2.602 | 2.725 | 14.726 | 15.308 |
| newlines / 1,048,576 | 3.578 | 3.578 | 3.157 | 3.189 | 15.792 | 15.832 |
| newlines / 16,777,216 | 13.056 | 13.156 | 11.246 | 10.939 | 25.297 | 25.086 |
| reduce / 10,000 | 2.852 | 2.920 | 2.724 | 2.826 | 15.193 | 15.225 |
| reduce / 100,000 | 2.918 | 2.939 | 2.861 | 2.674 | 15.673 | 15.344 |
| reduce / 1,000,000 | 4.042 | 3.974 | 3.682 | 3.571 | 20.561 | 20.594 |

Append 1 MiB is **24.884 ms**; the 10k/40k/160k/640k curve remains linear above
process startup. Before was 24.928 ms. Inline 16 MiB scan is 13.056 → 13.156 ms
(<1% median variation); branchless is 11.362 → 10.938 ms. Small-process medians
fluctuate, e.g. 4 KiB inline 2.679 → 2.919 ms; these samples do not establish a
statistical speedup/regression. No implementation changes were made to append or
transform paths, and their emitted IR is byte-identical to baseline.

| Workload / input | NIL before | NIL after | C++ before | C++ after | Python before | Python after |
|---|---:|---:|---:|---:|---:|---:|
| Transform / 4,096 | 2.875 | 2.807 | 2.805 | 2.646 | 15.035 | 14.838 |
| Transform / 1,048,576 | 5.099 | 4.742 | 3.390 | 3.464 | 64.162 | 61.860 |
| Transform / 16,777,216 | 36.023 | 35.431 | 13.782 | 13.250 | 764.290 | 787.586 |

Every transform output is byte-exact and applying it twice round-trips the original.
Append contents were independently verified at all five sizes; formatted report
contents and unchanged scan inputs are checked after every invocation. Quota and
maximum input sizes are unchanged by this root optimization.

## Every loss and what this establishes

NIL remains slower than C++ in every reported row, including roughly 4.74× at
1 MiB append and 2.90× at 160k formatted report. Those allocating builder/format
paths remain unchanged; capacity growth, allocation/accounting and per-element
checked runtime operations still cost more than C++ string building. We have not
profiled their individual percentages in this study.

NIL is faster than Python in all rows except the forced recursive scan and the
conservative sequence-returning scan (51.667/345.811 ms versus 24.943/24.503 ms).
Python's C `bytes.count` avoids per-byte helper calls entirely. Forced non-inline
scalar scan is 20.989 ms, below Python's 25.004 ms but slower than inline and C++.
This demonstrates removal of a specific abstraction tax, not C++ parity for all
programs or workloads. No tokenizer/model/TCR claim follows from runtime timings.

## Safety, setup findings and raw output

[Validation](../../../docs/validation/CALL_ROOTS.md): 206 debug/release tests,
zero Clippy warnings; 29 ASan/UBSan native tests; 864 differential programs / 1,728
O0/O2 builds, zero divergences across three seeds, each E012–E018 covered. Self,
mutual and near-limit recursion, called effects in lazy arms, alias-hostile and
sequence-returning/recursive-live families are included. Generation is scenario-
based, not arbitrary/coverage-guided; successful samples are bounded evidence.

An initial recursive control did extra counting for byte 255; it was corrected to
exact counting before final measurements and the independent arbitrary-byte oracle
was added. A supplemental control initially received a size instead of a file
argument; it failed, was fixed/regression-tested, and rerun. Filtered metadata now
marks append verification false when not selected. Setup results are not used in
these tables. No sanitizer/reference divergence was found; two obsolete IR counts
were updated after expected root removal. A concurrent Cargo/fuzzer launch failure
was rerun successfully before timing.

Raw manifests/samples, command logs, unoptimized LLVM and disassembly remain local:
`~/.local/share/nil/benchmarks/archive/call-roots-2026-10-03.zip`.
SHA-256 `ece248a5a375fbbe2447012d468562e8bd25a17a2101c42d8d60b93fe755e90f`.
Nothing was uploaded. The compiler gitlink points to local benchmark commits;
checkout on another machine requires publishing them later, outside this goal.
