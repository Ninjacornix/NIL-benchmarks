# Part A4 — numeric forecasts for Round 21 steps 4, 5 and 6

Committed **before** ADR 043 and before any compiler change. These are
falsifiable predictions, not results. Misses are published in `ROUND21.md`
with the measured value beside the forecast.

Evidence these rest on: `benchmarks/reports/2026-10-07/ROUND21_BEFORE.md`
(natural/tuned qualification, whole-process timings, peak RSS, reference live
capacity and prospective quota reservation) and the Part A1 copy census
(`copy_census.py`, ledger in `copy_ledger.py`).

Machine: one macOS arm64 host, Apple clang 21.0.0. Ratios, not absolute
milliseconds, are the comparable quantity.

## Step 4 — configurable memory and call-depth limits, deep recursion

The A2 evidence that fixes the defaults: the worst admitted reference quota
reservation is **3sum at 81.29% of 64 MiB** (≈ 52.0 MiB), its live charge is
40.66%, and the largest natural process RSS is **3sum at 18.47 MiB**. Three more
programs exceed 15% of quota (course-schedule 15.50%, balanced-binary-tree
7.15%, last-stone-weight 7.15% live). No admitted program is close to the
current depth of 256 frames.

| ID | Forecast | Falsified if |
|---|---|---|
| F4.1 | Default memory limit becomes **256 MiB**, i.e. 4.92× the worst observed admitted reservation. | ADR 043 selects a different default, or 256 MiB leaves any admitted program above 50% of quota. |
| F4.2 | Default call depth becomes **1024** frames, 4× the current 256. | A deeper default is needed by an admitted program, or 1024 cannot be reached safely. |
| F4.3 | All **1,070** NeetCode checks and all **2,815** application-corpus checks (original group exactly **610**) still pass at the new defaults, with byte-identical output. | Any check changes result. |
| F4.4 | Running with `--memory-limit 64MiB` reproduces every current E013 **at the same instruction, code and span**, in the reference evaluator and native O0/O2. | Any E013 moves, changes code, or disappears. |
| F4.5 | Tests and fuzz keep the current small limits, so **no existing E013/E008 fuzz expectation changes**: three seeds stay at 644 programs, 1,288 native builds, 0 divergences, and the per-code counts stay identical across seeds. | Any observed-code count changes for an unchanged family. |
| F4.6 | The reference evaluator reaches depth 1024 **without a host stack overflow**, because frames are already heap allocated. Measured head-room: a 1024-deep recursion completes. | The reference segfaults or aborts below the configured depth. |
| F4.7 | Native stack exhaustion becomes a clean **E008** with the standard instruction-budget diagnostic text, never a segmentation fault, in **bounded** builds. Unbounded builds gain no new check and no measurable slowdown (≤2% on the three historical controls). | A native deep recursion faults, or an unbounded control regresses more than 2%. |
| F4.8 | Raising the default does **not** change any timing by more than noise: all three historical controls (append, scan, transform) stay within **±5%** of `ROUND21_BEFORE.md` medians, and no admitted program's natural/C++ ratio moves by more than **±5%**. | Any control or ratio moves more than 5% in the unfavourable direction. |
| F4.9 | Qualification is unchanged by limits alone: **natural stays 19/150 and tuned stays 22/150**. | Either count changes from a limits-only change. |

The "reserve quota as if copying" rule is a semantics decision for ADR 043, not a
forecast. Whatever it decides, F4.4 must still hold for the 64 MiB configuration.

## Step 5 — copy-hint diagnostic

| ID | Forecast | Falsified if |
|---|---|---|
| F5.1 | The hint is opt-in, has **no effect on exit codes, diagnostics, output bytes or host effects**, and is deterministic across runs of the same program and input. | Any observable behaviour differs with the flag on. |
| F5.2 | On the natural sources it names **at least one site** in each of `balanced-binary-tree`, `validate-binary-search-tree`, `spiral-matrix` and `last-stone-weight`, each identifying the later read that keeps the original live. | Any of the four produces no site. |
| F5.3 | Every site it names corresponds to a native `PAYLOAD_COPY` event in the Part A1 census for the same program, i.e. **no invented sites**. | A named site has no matching census event. |
| F5.4 | Hint output costs **0 tokens of source change**: no program is edited to obtain it. | A natural source has to change. |

## Step 6 — general ownership

Round 21 ships this **only** if the full soundness argument holds for live
aliases, returned aliases, lazy arms, recursion, record children, trap order,
quota observation and deferred roots, and the variant-shape matrix passes.

| ID | Forecast | Falsified if |
|---|---|---|
| F6.1 | **Primary forecast: this step does not ship in Round 21.** The budgeted outcome is a published soundness analysis plus the census data, with no narrower shape recognizer substituted. | It ships, which would be a favourable miss. |
| F6.2 | *Conditional on shipping*: `last-stone-weight` natural reaches **≤ 3× C++**, i.e. a median ≤ **37.4 ms** against its 12.48 ms C++ baseline, down from 26,904 ms. | It ships and stays above 3×. |
| F6.3 | *Conditional on shipping*: `spiral-matrix` natural reaches **≤ 3× C++**, i.e. a median ≤ **26.9 ms** against its 8.96 ms baseline, down from 1,422 ms. | It ships and stays above 3×. |
| F6.4 | *Conditional on shipping*: native `PAYLOAD_COPY` **AVOIDABLE** bytes fall by **≥ 50%** on the natural cohort, and **no** currently qualifying program regresses past 3×. | Reduction below 50%, or any qualified program regresses. |
| F6.5 | *Conditional on shipping*: natural qualification rises from **19/150**; the tuned count must not fall below 22/150. | Natural does not rise, or tuned falls. |
| F6.6 | If it does not ship, natural qualification stays **19/150** and tuned stays **22/150** for the round. | Either count changes without an ownership change. |

A shape recognizer that only matches the five cliff sources is rejected under
rule R2 regardless of the timings it produces.
