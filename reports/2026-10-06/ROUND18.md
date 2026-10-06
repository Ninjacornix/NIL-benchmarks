# Round 18 — runtime audit, stable updates, source leaf expansion and maps

## Part 0: independent audit verdict

**No unsound reconciliation case found.** No reference/native divergence or sanitizer finding occurred. This is an independent source review and adversarial testing, not an exhaustive proof. Audit commit `c64df4b` precedes ADRs and performance implementation; [audit argument and receipts](../../../docs/validation/ROUND18_AUDIT.md) cover dirty-frame synchronization, retain-before-drop, child roots, relocation, doubled slots, input frames and global state. Three new regressions exercise pending stores through 241 call frames, child-bearing record-buffer growth in a callee, and adjacent successful/failing copy-quota boundaries. Six new fuzz families exercise the same class beyond the regression shapes.

**Unfavourable findings: the non-target performance gate remains open.** Source-sort medians are repeatedly 4–9% higher; the investigation below does not establish a safe production fix or a sufficient causal explanation. Round 18 is **not declared complete**. Also, all five 250k-entry/64-byte-key NIL map controls trap E013 during construction, at 131,073 live entries with the retained input. Map iteration materializes keys and hashes them again instead of directly visiting dense values. Filters, materialized updates and comparator/source sort remain slower than C++. Writable map/transform loops remain scalar. Bounded native calls intentionally retain their call machinery; trivial-source expansion applies only to unbounded native execution.

No unsound runtime fix or revert was needed. The single-threaded global runtime remains unsuitable for concurrent embedding without redesign. Each future root/live reader must observe the deferred protocol; passing aggregate tests is not a substitute for that invariant.

## Method and provenance

Main baseline `8647ba7`, benchmark baseline `0766a90`; branches `feat/std-inline` and `exp/std-inline`, no upstream. ADRs 039/040 committed in `7ebaa8d` before implementation commits `f80e4b1` and `0d6fd7f`. Map forecasts committed in benchmark `46f7fe0` before measurement. No pushes.

Apple Silicon macOS, Apple Clang 21.0.0, Rust 1.98.1. Native O2, existing application LTO; C++17 O2 and libc++. All timing rows use 25 measured warm whole-process repetitions after one discarded warmup, rotating control order, no CPU isolation. Startup, input read, construction and stdout/file output are included. Every result is checksum- or byte-exact checked. Original and final 23-control batches were separate; C++ controls rotate within each batch. Push uses fully interleaved before/after revisions. Cross-round numbers are context, not paired measurements on a controlled machine. No statistical significance claim from medians alone.

Raw JSON, logs, IR, disassembly and executables stay outside git in `/tmp/nil-round18/`. The committed report records summaries and SHA-256 receipts. Corpus verification reports the then-current HEAD `7ebaa8d` because final compiler changes were still uncommitted during gates; the tested working-tree code is the code subsequently committed as `f80e4b1`/`0d6fd7f`, with no later compiler changes. The binary receipt below identifies the measured build.

## Part A: stable observed update frames

[ADR 039](../../../docs/adr/039.md) admits one last-use replacement of flat Bytes/Buffer loop state, with other sequence states identity-carried. Other instructions must be scalar and body-derived borrowing; no allocating/effectful calls, nested regions, record children, snapshots or additional updates. Reconcile after installing preheader roots. All replacement bounds/byte/quota/physical-uniqueness checks remain. If the returned pointer is unchanged, skip its redundant store/reconciliation; if copying changes it, store and reconcile immediately. The next iteration therefore starts exact even when a caller alias forces copying. Generic replacements retain observations.

IR evidence, before → after (`map_hand.ll`):

```llvm
; Before, body
%v17 = call ptr @nil_set_unique(ptr %v10, i64 %v11, i64 %v16, i64 51, i64 63)
call void @nil_root_store(ptr %v6, ptr %v17)
; After, preheader
call void @nil_roots_observe()
; After, body — still a checked replacement
%v17 = call ptr @nil_set_unique_observed(ptr %v10, i64 %v11, i64 %v16, i64 51, i64 63)
call void @nil_root_store_observed(ptr %v6, ptr %v17)
```

`stable_update_frame_skips_only_proved_observations` asserts the IR and tests an external alias (copy fallback) at O0/O2; effectful loops retain ordinary observations. Existing application IR regression now requires the observed helper and preheader, and still rejects unconditional copying. Scan disassembly retains `cmeq.16b` (e.g. `0x100000690`, `0x100000700`). Map and transform do **not** vectorize; this round removes root reconciliation, not checked stores.

Forecast 32–39 ms for map/transform and target <=37.9: **hit**. Hand/std map 36.098/36.164, transform 35.783 ms. Round 17 published 47.28/44.83, same-session baseline 48.13/45.20. Round 16 comparison cited by the maintainer/ADR038 is 37.94/37.90; stored OWNERSHIP.md's separate batch is 35.652/35.030. Do not mix these as paired samples. Filters were forecast within 10%: hand 76.898→77.008, std 80.666→80.728 ms, **hit**.

### Full controls, including remaining losses

Each timing cell is **min/median/max ms**, 25 repetitions. Round17 column is its published median. This fixed-bound 1 MiB append control already benefits from Round16 growth lowering; it is not the old runtime-sized ~22 ms control.

| Control | Round16 median | Round17 median | Same-session before | After | After/before median |
|---|---:|---:|---:|---:|---:|
| append | 5.737 | 5.464 | 5.750/6.018/6.704 | 5.084/6.126/6.919 | 1.018x |
| filter_hand | 538.919 | 75.757 | 76.046/76.898/78.615 | 76.171/77.008/104.515 | 1.001x |
| filter_std | 274.521 | 79.444 | 79.240/80.666/82.809 | 79.970/80.728/84.808 | 1.001x |
| map_hand | 35.652 | 47.284 | 47.264/48.127/51.688 | 35.067/36.098/39.798 | 0.750x |
| map_std | 35.551 | 47.322 | 47.047/48.015/51.359 | 35.491/36.164/70.063 | 0.753x |
| scan | 8.482 | 8.623 | 8.127/8.658/9.491 | 8.403/8.831/12.954 | 1.020x |
| insertion_hof | 60.755 | 48.297 | 48.299/48.943/49.671 | 48.959/49.655/51.113 | 1.015x |
| insertion_hand | 60.651 | 47.867 | 48.194/48.665/49.659 | 48.747/49.259/51.603 | 1.012x |
| transform | 35.030 | 44.829 | 43.478/45.198/47.419 | 34.713/35.783/39.061 | 0.792x |
| sort_core_1024 | 3.974 | 4.325 | 2.934/4.129/5.326 | 3.061/4.324/5.222 | 1.047x |
| sort_source_1024 | 3.683 | 3.627 | 3.411/3.698/4.628 | 3.570/3.753/4.788 | 1.015x |
| sort_core_65536 | 9.559 | 9.555 | 9.332/9.691/10.091 | 9.391/9.729/10.084 | 1.004x |
| sort_source_65536 | 72.123 | 72.522 | 72.451/75.520/88.957 | 72.831/80.930/89.572 | 1.072x |
| sort_core_1048576 | 131.151 | 128.101 | 130.155/131.105/142.648 | 129.703/131.000/132.026 | 0.999x |
| sort_source_1048576 | 1360.087 | 1354.030 | 1408.261/1454.805/1566.653 | 1381.955/1527.827/1589.615 | 1.050x |
| cpp_append | — | 5.011 | 4.895/5.224/6.387 | 5.093/5.308/6.794 | 1.016x |
| cpp_filter | — | 29.938 | 29.416/30.385/33.625 | 29.677/30.324/32.382 | 0.998x |
| cpp_map | — | 18.868 | 18.455/19.122/20.382 | 18.400/19.323/28.582 | 1.011x |
| cpp_insertion | — | 4.676 | 4.522/4.748/5.167 | 4.507/4.975/6.857 | 1.048x |
| cpp_transform | — | 13.330 | 12.608/13.275/17.326 | 12.348/13.260/16.385 | 0.999x |
| cpp_sort_1024 | — | 4.373 | 2.751/4.159/4.364 | 3.096/4.305/6.846 | 1.035x |
| cpp_sort_65536 | — | 8.674 | 8.485/8.790/9.957 | 8.624/8.918/10.207 | 1.015x |
| cpp_sort_1048576 | — | 95.043 | 95.826/96.151/96.843 | 96.041/96.499/98.744 | 1.004x |

After medians: append 1.15x C++, hand/std filter 2.54/2.66x, hand/std map 1.87x, transform 2.70x, insertion callback 9.98x. Source merge sort at 1M remains 15.83x C++ std::sort; it is an explicit prototype, not a migrated std operation. C++ insertion uses the same insertion algorithm. Comparator/source-sort losses are retained in the table.

Non-target filter/append/scan/insertion medians move approximately 0–2%, with overlapping ranges. Source-sort 64k/1M separate-batch medians move +7.2/+5.0%; ranges overlap, but that alone is insufficient to dismiss a regression. Follow-ups below retain those observations; their higher medians must not be labelled unchanged merely because ranges overlap.

### Non-target source-sort investigation: unresolved

All follow-ups use 25 rotating repetitions and exact full-array output checks. Cells min/median/max ms. These are separate campaigns, not samples pooled after selecting favourable runs.

| Campaign / control | Before | After / variant | Median ratio |
|---|---:|---:|---:|
| sort-repeat.json / sort_source_65536 | 73.173/77.679/126.019 | 72.302/84.632/153.909 | 1.090x |
| sort-repeat.json / sort_source_1048576 | 1400.174/1473.067/2096.790 | 1413.328/1560.968/1783.128 | 1.060x |
| sort-repeat.json / sort_core_1024 | 2.888/3.688/5.269 | 2.862/3.828/4.872 | 1.038x |
| sort-alone.json / sort_source_1048576 | 1405.600/1455.862/1611.271 | 1414.349/1516.031/1612.037 | 1.041x |
| sort-isolation-final.json / old_ir_new_runtime | 1328.144/1363.815/1481.468 | 1331.132/1426.482/1612.596 | 1.046x |
| sort-isolation-final.json / old_ir_grouped_runtime | 1321.812/1355.871/1619.156 | 1414.204/1432.724/1595.468 | 1.057x |
| sort-identical.json / sort_source_1048576 | 1320.251/1347.529/1767.107 | 1322.199/1387.769/1503.956 | 1.030x |
| sort-canonical.json / sort_source_65536 | 73.912/77.494/91.570 | 73.626/81.325/90.630 | 1.049x |
| sort-canonical.json / sort_source_1048576 | 1384.365/1448.042/1571.508 | 1432.008/1549.235/1595.676 | 1.070x |
| sort-shared-path.json / final_compiler | 1387.941/1466.976/1637.449 | 1423.730/1545.506/1600.561 | 1.054x |
| sort-shared-path.json / identical_text | 1413.349/1460.139/1611.420 | 1515.536/1540.736/1606.186 | 1.055x |

Initial interleaved source-sort 64k/1M ratios: 1.090/1.060. A paired bootstrap (10,000 samples, seed18039, resample paired repetitions and take ratio of medians) yields 95% intervals1.026–1.136 /1.029–1.080. The standalone1M interval is1.026–1.061. These do **not** support dismissing the difference as ordinary sample noise.

Investigation outside the repository:

- Final C runtime plus captured baseline build IR isolates the runtime from the emitter. It still has a higher median.
- Grouping frame pointer/dirty flag in an external C copy restores the **entire disassembled text**, including addresses, to the baseline (only the printed executable path differs). It also has a higher median. This is not a justified production fix, so it was not implemented.
- A SHA-256-identical copy of the baseline executable under a new path has a3.0% higher median; its paired bootstrap interval0.977–1.063 includes parity. This exposes a platform/launch confound but does not explain the whole production difference.
- Identical argv[0] still gives higher source-sort medians. Copying arms to one shared executable path before starting timers also retains the difference, including the machine-code-identical experimental rebuild.

The recursive sort body has1130 instructions before and after. Its production differences are global-root-state offsets and external-call relocations; emitter changes are in the input-fill loop. This establishes no added recursive root work, **not** a proof of runtime parity. Microarchitectural/loader causes have not been established. Do not claim a proven cache explanation or an accepted permanent cost.

One early exploratory runtime/grouped run overlapped for roughly its final seconds; both timings were discarded and replaced by the serialized isolation matrix above. The first isolation link omitted the entry wrapper from inspection IR and failed E011; corrected by capturing actual build IR, not by changing the compiler. These exploratory failures do not enter performance tables.

**Outstanding completion work:** explain or recover the non-target source-sort timing difference under independently controlled conditions. All correctness gates and Part A/B targets pass, but the full no-regression gate cannot honestly be certified. No later optimization or unrelated feature started. Production code was not changed speculatively to alter binary layout.

## Part B: inline linear source expressions

[ADR 040](../../../docs/adr/040.md): native unbounded HIR expansion before rooting, followed by HIR validation. Eligibility is structural, not a std-name special case: one flat dynamic parameter/result, other parameters i64, each parameter/intermediate exactly once, at most eight constant/constructor/concat instructions, no calls/regions/effects/aggregates. Already-evaluated SSA arguments stay in left-to-right positions; copied instructions retain original spans. The NIL source remains the semantic definition. Unused parameters, multiple dynamic parameters and more general expressions remain conservative.

Bounded native and reference execution retain original calls/ticks/depth so E009/E010 observability is unchanged. The stronger exactly-once restriction is deliberate: at-most-once alone does not establish identical root/quota lifetimes for unused values. `source_leaf_expansion_preserves_bounded_calls_and_argument_effects` checks retained bounded calls, unbounded expansion, argument effect order, an unselected effect and captures after expansion. Native root regressions run bounded/unbounded × O0/O2.

Same 16 MiB input, bytes 0..255 repeated, keep <128, byte-exact output every run. Forecast push 70–90 ms and <=1.10x concat: **hit**, 78.740 ms and **0.997x**. It remains 2.39x C++ for the same predicate; matching concat does not establish C++ parity.

| Arm | min/median/max ms |
|---|---:|
| before_concat | 78.392/78.852/80.759 |
| before_push | 131.949/132.510/133.992 |
| after_concat | 77.981/78.970/84.116 |
| after_push | 78.212/78.740/81.735 |
| cpp | 32.326/32.913/38.617 |

No syntax, std source, profiles, default, quota, failure codes or language intrinsic changes. **35 intrinsic variants / 34 executable core implementations remain unchanged.** Existing verified program sources and token counts are unchanged.

## Part C: map controls, measurement only

Five operations: insert N, three passes of successful lookup, missing lookup, insertion-order iteration, and existing-key update. Binary keys are unique little-endian indices, zero-padded to 8/64 bytes; misses set the last byte to 128. Sizes fixed before measurement: 10k/100k/250k. Both C++ runners bulk-read the same fixture; no insertion reserve. Ordered C++ uses dense entries + linear probing, FNV-1a, <=0.5 load; unordered uses libc++ std::unordered_map. Neither implements NIL's immutable aliases or 64 MiB quota. Queries materialize strings like NIL slices (C++ SSO benefits short keys); ordered updates can use views.

Insert ns is whole process/N. Other ns is each operation's latency minus its paired construction sample, divided by 3N: **a marginal estimate, not isolated kernel time**. Small/negative C++ iteration estimates expose subtraction/startup noise; do not interpret them as negative execution time or compute ratios against them. Raw whole-process ranges accompany every row below.

### Median estimated ns/operation

NIL / ordered C++ / unordered C++; E013 means no timing claim. Every successful run's independent checksum passed. Failed NIL rows fail before the requested operation, at construction.

| Key bytes | N | Operation | NIL ns | Ordered C++ ns | Unordered C++ ns |
|---:|---:|---|---:|---:|---:|
| 8 | 10000 | insert | 311.02 | 265.74 | 287.25 |
| 8 | 10000 | hit | 32.91 | 8.31 | 19.48 |
| 8 | 10000 | miss | 54.44 | 16.82 | 25.92 |
| 8 | 10000 | iterate | 29.27 | -1.39 | 2.27 |
| 8 | 10000 | update | 44.99 | 6.80 | 21.81 |
| 8 | 100000 | insert | 87.30 | 51.00 | 83.61 |
| 8 | 100000 | hit | 27.63 | 9.40 | 22.80 |
| 8 | 100000 | miss | 53.21 | 15.98 | 31.05 |
| 8 | 100000 | iterate | 26.82 | -0.14 | 5.15 |
| 8 | 100000 | update | 41.43 | 7.53 | 28.44 |
| 8 | 250000 | insert | 81.16 | 44.09 | 87.96 |
| 8 | 250000 | hit | 30.99 | 12.34 | 21.32 |
| 8 | 250000 | miss | 67.07 | 22.24 | 28.45 |
| 8 | 250000 | iterate | 29.89 | 0.91 | 5.85 |
| 8 | 250000 | update | 45.38 | 10.54 | 30.29 |
| 64 | 10000 | insert | 417.74 | 383.77 | 349.41 |
| 64 | 10000 | hit | 93.78 | 88.14 | 43.25 |
| 64 | 10000 | miss | 118.18 | 88.25 | 47.07 |
| 64 | 10000 | iterate | 90.59 | -2.34 | 2.18 |
| 64 | 10000 | update | 117.84 | 56.06 | 39.50 |
| 64 | 100000 | insert | 179.97 | 139.77 | 148.36 |
| 64 | 100000 | hit | 86.46 | 67.50 | 40.82 |
| 64 | 100000 | miss | 118.96 | 78.23 | 49.67 |
| 64 | 100000 | iterate | 81.12 | 0.58 | 5.98 |
| 64 | 100000 | update | 111.32 | 52.17 | 41.59 |
| 64 | 250000 | insert | E013 | 138.49 | 177.79 |
| 64 | 250000 | hit | E013 | 73.04 | 44.33 |
| 64 | 250000 | miss | E013 | 93.24 | 48.67 |
| 64 | 250000 | iterate | E013 | -0.01 | 6.78 |
| 64 | 250000 | update | E013 | 58.29 | 45.35 |

### Attribution: measured work, not guessed percentages

Untimed external instrumentation of an emitted runtime copy counted the following at 100k. Production C runtime was not edited for profiling; instrumented runs are not timing evidence. Allocation counter counts arena sequence allocations, excluding file-read scratch; copy bytes are the copied entry/key payload, not RSS. Query passes include construction in these totals.

| Key | Operation | Allocations | Hashed bytes | Probes | Reuses | Copies | Copied bytes |
|---:|---|---:|---:|---:|---:|---:|---:|
| 8 | insert | 100018 | 800000 | 111285 | 99984 | 16 | 7339920 |
| 8 | hit | 400018 | 3200000 | 422331 | 99984 | 16 | 7339920 |
| 8 | miss | 400018 | 3200000 | 625467 | 99984 | 16 | 7339920 |
| 8 | iterate | 400018 | 3200000 | 422331 | 99984 | 16 | 7339920 |
| 8 | update | 400018 | 3200000 | 422331 | 399984 | 16 | 7339920 |
| 64 | insert | 100020 | 6400000 | 126481 | 99982 | 18 | 14679952 |
| 64 | hit | 400020 | 25600000 | 437263 | 99982 | 18 | 14679952 |
| 64 | miss | 400020 | 25600000 | 541405 | 99982 | 18 | 14679952 |
| 64 | iterate | 400020 | 25600000 | 437263 | 99982 | 18 | 14679952 |
| 64 | update | 400020 | 25600000 | 437263 | 399982 | 18 | 14679952 |

Subtracting construction yields 300k temporary-key allocations for hit/miss/iteration/update. Updates reuse all 300k existing-key mutations; growth copies remain 16 (8 B) /18 (64 B), with **no per-update COW copies**. Lookup probes average ~1.04/hit and 1.71/miss for 8 B, 1.04/hit and 1.38/miss for 64 B. These fixtures do not demonstrate pathological collisions.

64-byte keys hash eight times as many bytes as 8-byte keys. At 100k, hit cost rises 27.63→86.46 ns and update 41.43→111.32; long-key FNV work and materialization are concrete costs. Ordered C++ also slows on long keys; unordered is faster there. These counters identify extra work, not a decomposition of wall time into exact percentages. Separate C++ hash-only micro measurements are archived, but cannot establish the percentage of NIL runtime spent hashing.

Iteration HIR/IR (`maps.ll`): `nil_map_key` at line286 followed by `nil_map_get_int` at line288. Thus !each copies every key and looks its value up again, hashing and probing; ordered C++ directly traverses dense entries. This is an implementation gap, not an intrinsic cost of stable order. No redesign this round.

Quota failure: external profile reports `quota_entries=131073 prospective=33554456 live=49554640`. Prospective reservation includes its 40-byte header, so total is **83,109,136 >67,108,864** bytes. The retained 16MB input, grown map and current temporary key are live. Prospective-copy admission occurs even when uniqueness later permits reuse. **131,073 entries work in this retained-input long-key construction; the next insertion traps.** This is workload-specific, not a new global map ceiling. No quota or copying rule was weakened.

Forecasts were conservative and mostly overestimated costs: short insert predicted 500–5000 ns, actual 81–311; lookup 100–1500, actual 28–119; iteration 50–1500, actual 27–91; update 200–4000, actual 41–118. Long insert expected 1.5–4x short, actual ~1.34x at10k (startup dominates) and 2.06x at100k. NIL 2–15x slower was not universally true: short-key 250k construction beats unordered (81.16 vs87.96 ns). It still loses many operation comparisons, especially iteration. E013 forecast **hit** for all long-key250k rows.

Recommendation only: benchmark a faster fixed, cross-platform deterministic long-key hash. A Swiss-style index is lower priority given short measured probe chains, and cannot eliminate temporary key allocation, redundant iteration lookup or prospective quota reservations. [Abseil's design](https://abseil.io/about/design/swisstables) uses control-byte fingerprints and vector candidate filtering; an insertion-ordered adaptation would retain dense entries and charge all new metadata. Such a redesign needs its own quota/determinism/alias audit. No hash, table layout or operation changed here.

Harness review found an unused query-string temporary in the first C++ update baseline. Removed in benchmark commit `ec5979d`, then **reran the entire 90-row matrix**. Final tables use `maps-final/results.json`; the initial matrix remains externally archived, not selectively combined. This correction favours C++.

### Every map row: raw and marginal ranges

Cells min/median/max; raw milliseconds and marginal nanoseconds. No truncated or omitted failed rows.

| Key | N | Operation | Runner | Raw ms | Estimated ns |
|---:|---:|---|---|---:|---:|
| 8 | 10000 | insert | nil | 2.848/3.110/3.469 | 284.81/311.02/346.86 |
| 8 | 10000 | hit | nil | 3.913/4.052/4.516 | 26.02/32.91/51.68 |
| 8 | 10000 | miss | nil | 4.572/4.761/5.318 | 46.17/54.44/75.72 |
| 8 | 10000 | iterate | nil | 3.769/3.957/4.314 | 19.43/29.27/42.86 |
| 8 | 10000 | update | nil | 4.236/4.491/4.801 | 34.69/44.99/60.01 |
| 8 | 10000 | insert | ordered | 2.356/2.657/2.922 | 235.57/265.74/292.23 |
| 8 | 10000 | hit | ordered | 2.770/2.909/3.362 | 1.92/8.31/23.93 |
| 8 | 10000 | miss | ordered | 2.920/3.117/3.804 | 6.92/16.82/34.19 |
| 8 | 10000 | iterate | ordered | 2.462/2.601/3.020 | -10.38/-1.39/12.03 |
| 8 | 10000 | update | ordered | 2.660/2.891/3.202 | -0.81/6.80/23.05 |
| 8 | 10000 | insert | unordered | 2.709/2.873/3.292 | 270.85/287.25/329.25 |
| 8 | 10000 | hit | unordered | 3.235/3.430/3.635 | 9.06/19.48/24.44 |
| 8 | 10000 | miss | unordered | 3.374/3.685/3.878 | 11.76/25.92/36.99 |
| 8 | 10000 | iterate | unordered | 2.755/2.951/3.244 | -9.93/2.27/16.82 |
| 8 | 10000 | update | unordered | 3.313/3.567/3.974 | 8.41/21.81/42.19 |
| 8 | 100000 | insert | nil | 8.289/8.730/9.279 | 82.89/87.30/92.79 |
| 8 | 100000 | hit | nil | 16.683/17.020/17.554 | 25.92/27.63/30.87 |
| 8 | 100000 | miss | nil | 23.770/24.619/26.426 | 49.88/53.21/59.91 |
| 8 | 100000 | iterate | nil | 16.031/16.796/17.555 | 24.63/26.82/29.25 |
| 8 | 100000 | update | nil | 20.388/21.093/21.990 | 38.86/41.43/44.50 |
| 8 | 100000 | insert | ordered | 4.749/5.100/5.920 | 47.49/51.00/59.20 |
| 8 | 100000 | hit | ordered | 7.452/7.876/8.179 | 7.53/9.40/10.49 |
| 8 | 100000 | miss | ordered | 9.544/9.911/10.719 | 14.01/15.98/18.85 |
| 8 | 100000 | iterate | ordered | 4.735/5.070/5.921 | -2.00/-0.14/3.34 |
| 8 | 100000 | update | ordered | 7.024/7.389/7.726 | 5.63/7.53/9.37 |
| 8 | 100000 | insert | unordered | 8.004/8.361/9.154 | 80.04/83.61/91.54 |
| 8 | 100000 | hit | unordered | 14.709/15.252/16.154 | 21.35/22.80/25.19 |
| 8 | 100000 | miss | unordered | 17.073/17.694/18.515 | 27.81/31.05/33.33 |
| 8 | 100000 | iterate | unordered | 9.483/9.843/10.772 | 2.35/5.15/7.52 |
| 8 | 100000 | update | unordered | 15.733/16.865/18.185 | 24.81/28.44/31.42 |
| 8 | 250000 | insert | nil | 19.410/20.290/22.947 | 77.64/81.16/91.79 |
| 8 | 250000 | hit | nil | 42.775/43.812/45.099 | 28.32/30.99/33.10 |
| 8 | 250000 | miss | nil | 67.536/70.869/76.901 | 62.28/67.07/73.69 |
| 8 | 250000 | iterate | nil | 41.301/42.814/44.501 | 25.91/29.89/31.81 |
| 8 | 250000 | update | nil | 52.661/54.357/61.720 | 41.73/45.38/55.92 |
| 8 | 250000 | insert | ordered | 10.335/11.022/11.907 | 41.34/44.09/47.63 |
| 8 | 250000 | hit | ordered | 19.239/20.272/22.131 | 11.27/12.34/14.31 |
| 8 | 250000 | miss | ordered | 26.192/27.674/29.055 | 19.67/22.24/23.76 |
| 8 | 250000 | iterate | ordered | 11.066/11.646/12.463 | -0.73/0.91/1.55 |
| 8 | 250000 | update | ordered | 18.407/19.033/20.245 | 8.74/10.54/12.51 |
| 8 | 250000 | insert | unordered | 20.548/21.990/25.912 | 82.19/87.96/103.65 |
| 8 | 250000 | hit | unordered | 36.583/38.634/45.543 | 18.18/21.32/28.07 |
| 8 | 250000 | miss | unordered | 40.441/43.291/47.764 | 24.55/28.45/32.77 |
| 8 | 250000 | iterate | unordered | 25.024/26.932/28.600 | 2.77/5.85/10.22 |
| 8 | 250000 | update | unordered | 42.490/44.508/48.033 | 26.47/30.29/34.28 |
| 64 | 10000 | insert | nil | 3.949/4.177/4.529 | 394.90/417.74/452.87 |
| 64 | 10000 | hit | nil | 6.793/6.999/7.371 | 86.01/93.78/103.57 |
| 64 | 10000 | miss | nil | 7.519/7.739/8.205 | 105.55/118.18/133.14 |
| 64 | 10000 | iterate | nil | 6.730/6.898/7.880 | 80.07/90.59/113.59 |
| 64 | 10000 | update | nil | 7.444/7.720/8.328 | 106.07/117.84/140.00 |
| 64 | 10000 | insert | ordered | 3.653/3.838/4.204 | 365.29/383.77/420.37 |
| 64 | 10000 | hit | ordered | 6.270/6.478/6.905 | 68.87/88.14/98.90 |
| 64 | 10000 | miss | ordered | 6.276/6.525/6.955 | 76.90/88.25/97.64 |
| 64 | 10000 | iterate | ordered | 3.609/3.810/4.167 | -10.54/-2.34/3.26 |
| 64 | 10000 | update | ordered | 5.394/5.523/5.869 | 42.38/56.06/72.17 |
| 64 | 10000 | insert | unordered | 3.275/3.494/3.849 | 327.50/349.41/384.85 |
| 64 | 10000 | hit | unordered | 4.604/4.820/5.247 | 32.32/43.25/65.72 |
| 64 | 10000 | miss | unordered | 4.735/4.918/5.204 | 32.53/47.07/64.31 |
| 64 | 10000 | iterate | unordered | 3.364/3.556/3.843 | -11.75/2.18/15.47 |
| 64 | 10000 | update | unordered | 4.485/4.702/5.285 | 21.22/39.50/61.16 |
| 64 | 100000 | insert | nil | 17.446/17.997/19.377 | 174.46/179.97/193.77 |
| 64 | 100000 | hit | nil | 43.012/43.954/50.257 | 83.88/86.46/108.34 |
| 64 | 100000 | miss | nil | 52.783/53.540/57.400 | 114.24/118.96/130.21 |
| 64 | 100000 | iterate | nil | 41.604/42.381/49.559 | 75.60/81.12/100.61 |
| 64 | 100000 | update | nil | 50.467/51.241/60.422 | 106.98/111.32/142.79 |
| 64 | 100000 | insert | ordered | 13.613/13.977/15.502 | 136.13/139.77/155.02 |
| 64 | 100000 | hit | ordered | 33.561/34.299/41.425 | 65.86/67.50/86.41 |
| 64 | 100000 | miss | ordered | 36.653/37.578/38.487 | 75.40/78.23/81.71 |
| 64 | 100000 | iterate | ordered | 13.597/14.096/14.785 | -4.68/0.58/2.81 |
| 64 | 100000 | update | ordered | 28.989/29.708/30.719 | 48.12/52.17/56.23 |
| 64 | 100000 | insert | unordered | 14.035/14.836/17.153 | 140.35/148.36/171.53 |
| 64 | 100000 | hit | unordered | 26.349/27.196/29.391 | 32.88/40.82/48.62 |
| 64 | 100000 | miss | unordered | 28.960/29.740/33.816 | 40.76/49.67/63.33 |
| 64 | 100000 | iterate | unordered | 15.781/16.717/18.817 | -3.30/5.98/15.02 |
| 64 | 100000 | update | unordered | 26.381/27.363/29.299 | 31.80/41.59/47.62 |
| 64 | 250000 | insert | nil | E013 | — |
| 64 | 250000 | hit | nil | E013 | — |
| 64 | 250000 | miss | nil | E013 | — |
| 64 | 250000 | iterate | nil | E013 | — |
| 64 | 250000 | update | nil | E013 | — |
| 64 | 250000 | insert | ordered | 33.387/34.623/35.457 | 133.55/138.49/141.83 |
| 64 | 250000 | hit | ordered | 87.085/89.168/90.841 | 70.77/73.04/74.55 |
| 64 | 250000 | miss | ordered | 101.056/104.378/111.762 | 89.03/93.24/102.27 |
| 64 | 250000 | iterate | ordered | 33.647/34.495/35.949 | -1.88/-0.01/1.66 |
| 64 | 250000 | update | ordered | 76.844/78.235/82.480 | 55.93/58.29/63.70 |
| 64 | 250000 | insert | unordered | 42.316/44.448/49.468 | 169.27/177.79/197.87 |
| 64 | 250000 | hit | unordered | 74.819/79.027/84.843 | 39.95/44.33/52.71 |
| 64 | 250000 | miss | unordered | 76.337/81.285/86.967 | 42.58/48.67/57.65 |
| 64 | 250000 | iterate | unordered | 45.109/49.062/53.828 | -0.54/6.78/11.62 |
| 64 | 250000 | update | unordered | 74.701/79.088/86.155 | 36.67/45.35/52.19 |

## Final gates and failures encountered

Reproduction commands are in [std-inline-study/README.md](../../std-inline-study/README.md). Logs below are the command output receipts, not forecasts.

| Command | Final output | Receipt |
|---|---|---|
| `./scripts/ci.sh` | 466 passed, 0 failed, zero Clippy warnings | final-ci-debug-2.log |
| `./scripts/ci.sh release` | 466 passed, 0 failed, zero Clippy warnings | final-ci-release-2.log |
| `./scripts/sanitize.sh` | 199 passed, all suites ASan/UBSan clean | final-sanitize-2.log |
| `cargo test -p nil-llvm --test roots --locked --offline` | 11 passed; bounded/unbounded native O0/O2 | expanded-roots-tests.log |
| `python3 benchmarks/corpora/application-v5/verify.py --output /tmp/nil-round18/final-corpus.json` | 2815 checks, 68 NIL programs, 11 unsupported | final-corpus.log/json |
| same command with `--group original` | exactly 610 checks | final-original.log/json |

Corpus totals: reference563 + native1126 + Python563 + C++563 =2815; original 120+240+125+125=610. Frozen tasks, oracles, goldens, baselines and verified NIL sources untouched. Earlier-profile golden suites pass. No density experiment this round; byte-for-byte unchanged corpus sources establish unchanged source token counts.

First post-change CI/sanitizer runs failed **one stale IR assertion**, expecting the old nil_set_unique helper spelling. Updated it to require the new checked observed helper/preheader and absence of unconditional nil_set copies, then reran all gates. This was not a runtime divergence or memory finding; initial failed logs are retained. No unexplained divergence, UB or sanitizer finding occurred.

Full-coverage commands: `./scripts/fuzz-v5.sh --seed SEED --out /tmp/nil-round18/final-fuzz-SEED`. Host stdout/files compared alongside values and codes, reference vs native O0/O2.

| Seed | Programs | Native builds | Family indices | Divergences |
|---:|---:|---:|---:|---:|
| 102061801 | 475 | 950 | 475/475, each once | 0 |
| 74018329 | 475 | 950 | 475/475, each once | 0 |
| 918273645 | 475 | 950 | 475/475, each once | 0 |

Per-code counts (same for each seed; seeds vary values, not the scheduled family distribution):

| Code | Per seed | All three |
|---|---:|---:|
| E009 | 3 | 9 |
| E012 | 24 | 72 |
| E013 | 34 | 102 |
| E014 | 9 | 27 |
| E015 | 8 | 24 |
| E016 | 14 | 42 |
| E017 | 10 | 30 |
| E018 | 11 | 33 |
| E019 | 3 | 9 |
| E020 | 6 | 18 |
| E021 | 5 | 15 |
| E022 | 3 | 9 |
| OK | 345 | 1035 |

There are 420 named call families, each executed once per seed; all 475 family indices execute once, including unnamed baseline generators. Total 1,425 programs and 2,850 native builds. Source-mutation/static-code counts and program hashes are retained in each receipt. New families:

| Family | Executions per seed | Observed result |
|---|---:|---|
| inline_push_argument_effects | 1 | {'OK': 1} |
| inline_push_byte_range | 1 | {'E014': 1} |
| inline_push_capture_after_expansion | 1 | {'OK': 1} |
| inline_push_empty_buffer | 1 | {'OK': 1} |
| inline_push_live_alias | 1 | {'OK': 1} |
| inline_push_nested_regions | 1 | {'OK': 1} |
| inline_push_quota | 1 | {'E013': 1} |
| inline_push_unselected_effect | 1 | {'OK': 1} |
| reconcile_callee_collection | 1 | {'OK': 1} |
| reconcile_child_growth | 1 | {'OK': 1} |
| reconcile_cross_frame_relocation | 1 | {'OK': 1} |
| reconcile_deep_pending_calls | 1 | {'OK': 1} |
| reconcile_quota_failure | 1 | {'E013': 1} |
| reconcile_quota_success | 1 | {'OK': 1} |

## Remaining accepted limits

Stable-frame proof excludes aggregate states, allocating branches, nested regions, multi-update and old-read/snapshot chains. They still reconcile normally. Linear expansion excludes unused/multiple dynamic parameters and bounded execution. No unchecked write, new language operation or stronger ownership guarantee was introduced. Conditional filters remain ~2.4–2.7x C++, updates ~1.9–2.7x, comparator source sorts much slower. Iteration copies/rehashes keys. Long-key map construction can hit the existing quota before250k; C++ baselines do not enforce it. Plain global runtime state is single-threaded only. Deferred root synchronization remains a load-bearing protocol for future changes.

## External artifact receipts

SHA-256; raw artifacts intentionally not committed. These identify the exact command outputs/samples/IR, including the failed stale assertion runs. Source and baseline commits allow reruns; temporary artifacts must be archived separately by the maintainer if permanent raw retention is required.

| Relative to /tmp/nil-round18 | SHA-256 |
|---|---|
| nil-before | `198c6a5f7a6ae3660c5f247716b67df27a7cb0870ae2cac2f5e9c3a4fdb4a35d` |
| before/results.json | `783bddb7e35e0194027b5b308b11dc0bfd6eeb23b545dc76771d13b409d1207e` |
| after/results.json | `e73852c68c83e0865bffca6619978fb8d3433c695497f0654c6f20136fd70562` |
| push/results.json | `868cee17ebacec4d647f4e67ad77d7ef357bd2db09cea262eb8d19e3cc1f1d17` |
| maps/results.json | `091a6b73672050433312759b58d7f8db20f8bb4cb5f9178ffb262788d02079c6` |
| maps-final/results.json | `dc0417a80bafa06a9d3b85460c47e5c6eb026742128107653f0469b34ab95649` |
| map-profile-2/results.json | `9a914f0bf48aedd76fb8390fb22e08a0e4ac918fef405e8170446a769c310f0f` |
| after/map_hand.ll | `cebd637158d1fdd7b09487a998a07b0cd5b65c2715501fd95a9feb41b0c36b39` |
| before/map_hand.ll | `885d9ffeba633fd7edf674696c6b00f034a0bc50a1808c03fb53ef3083b66385` |
| after/scan.asm | `df2a7266e146df24178a06f61e3835e0ea60585b2b56faf29b3d9419bc60e82d` |
| maps.ll | `ee3da23b84109b8a8dc18da3570abbda91d12dcb675079b63a4af2d41b9d424a` |
| final-ci-debug-2.log | `70dfcfc0abd660894cc6eab5cdcb5a53c30ad7ec4386aa70734177ef88be0e4f` |
| final-ci-release-2.log | `0add5e0f0496438aa37be0cf8196758f08fb6e8fded8aece56e17199894e0d30` |
| final-sanitize-2.log | `4e2feed427e38257fd80519ad6e4bcc75ca2bb9962f217c757ae6aee1f6c5840` |
| expanded-roots-tests.log | `22f024db02209bd88c7d894fd3c7ce1ea073054a298745c9020e75225c44a59a` |
| final-corpus.json | `c086d321fe9fca59fd6bc76d8cc3409ba6ea307148a6f02603568aa2b6b55119` |
| final-corpus.log | `be20bd3f928611dcc328731f47498e0d8b567c761009ec8bbb23cfa780cfda86` |
| final-original.json | `1d5ac720879b67a7529392461eb900c50177f7943f348b18619efc739a4ef3c0` |
| final-original.log | `c0d06c40cd140f16d0dd2d0d2ba1d8b70f1f9fff82e55ce51b6a8a86a0e8658a` |
| final-ci-debug.log | `82d5c7b519fb3e04aa1a9f29b809c2abc16a282866223a5ca32156b243f59369` |
| final-ci-release.log | `e5c91266a0b9bf6aa2342e44d34a305f00f0a75ff040797cd20dda50828cfc9c` |
| final-sanitize.log | `a1e2ba631c38950ff5559608c2e686357653a6ac440d5ec6df90626f322e09fb` |
| final-fuzz-102061801.log | `89a64a9a0e67dbf7d70f5e00038162b45a5e73b722e4b841a16755da07aea492` |
| final-fuzz-74018329.log | `1f188cfb3365fb740f95af8be43f7e07a0a0e37dde98b34da8ac042e1109d975` |
| final-fuzz-918273645.log | `bf11e0ec42bd38d596de5cc4f1d15a3f9323381f22507dccfe7e98126f11519f` |
| target/release/nil (outside this prefix) | `847d95e48e8a9bb002fa26b6a76bd4bbb4a681b8cdc1fe8bd56d92f358273091` |

### Follow-up receipts

| Artifact | SHA-256 |
|---|---|
| sort-repeat.json | `fac29355f857bff949e5452abf4eb8b88aec673ed409ced10a9f9ed12d524759` |
| sort-alone.json | `980ef656d43780db0e0d140c78eb377cb6c08b272370b180cd1f385bfa119d86` |
| sort-isolation-final.json | `a87ea9fdc257d5b34f3ee16fb3b67d82e667e57663e83601028e747f09882d5d` |
| sort-identical.json | `f82a227300c89fc0364ee80b53f3352cc5efc1503535c3489343947e4ccc2581` |
| sort-canonical.json | `9f86ab3b6ccf002f624abe901691f875766fca248eaba0f329e6a6fc39a4033f` |
| sort-shared-path.json | `1acd36779bf1dedbb8c0aa4f86511f75d428197b70e8d6a0113cbea2317c65e6` |
| sort-function-diff.txt | `c6a884045e8e8452cb2443916766e01cc209e160b888a942444f12109deae9f2` |
| isolate/grouped.asm | `0a84e0d9901ac55ba0e98f53dbfa336f3bcfa89d2ccf701e593f9c141c55db70` |
| isolate/runtime-only.asm | `79cf005940fcb103869059804e9d0162d036ce98a31c495d68f5a977066d7143` |
| isolate/before-build.ll | `e869804c6e22313c446492a17dcdb1199a76bc81746f77526d60e95711b07892` |
| isolate/grouped.c | `cc3ba021a5bce30e6bd26fd429668ed3eb80851871e7d34c1a82da88b1558357` |
| isolate/grouped | `f00063efe6200e88956220f13b22c3405990066b4426069b2bf7f8d2a24edeff` |
| copied-baseline/same-code | `f1334bb932d95a37828f1f5365b948d997fa53254ca0ed1006197ec937fb95d9` |
