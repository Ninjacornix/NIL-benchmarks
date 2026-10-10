# Round 24 — Part B: simultaneous update chains

**Natural qualification remains 19/150.** Tuned qualification measured 23/150,
up from 22; it is not a natural-code gain. Natural heap improved to 54.09 ms,
within the 35–60 ms forecast, but remains 5.01× C++. Balanced tree, course
schedule and BST still copy heavily. Std swap/pop still miss caller parity;
Part C has not shipped. No held-out problem or frozen source was changed.

## Semantics and implementation

ADR 048 was committed as `c914213` before implementation. The receiver and all
indices/values of a contiguous chain evaluate left-to-right before writes. Writes
then commit in source order; duplicate targets use the last value. Parentheses
are transparent. Bindings, projections, calls and control-flow results are
boundaries. Record-field chains follow the same rule. Selected lazy arms only
execute their own operands. Earlier profiles retain eager ordering. Intrinsics
remain 35; spellings and token counts are unchanged.

This deliberately changes fault/effect order for v5 chains. Write bounds/byte
checks keep their suffix spans, but a later operand trap now precedes them. Two
existing fuzz families change: `g2_byte_trap_first` E014→E012 and
`g2_quota_before_read` E013→E012, because their later `a[-1]` operand executes
before replacement validation. Reference and native O0/O2 agree exactly.

CI exposed a record-field append reuse regression: the old proof required an
adjacent field write. It now follows the concat result’s sole use across permitted
scalar operand instructions, retaining its escape/old-field/runtime-alias guards.
Grouped/binding/arithmetic variants have regression coverage. A newly constructed
intermediate record retains its child and remains conservative, explicitly tested.
No G1/path-correlation fix is claimed. Obsolete replay IR assertions now use
explicit binding boundaries, retaining actual read-after-write replay coverage.

## Isolated performance

Warm whole-process times; Apple Clang 21/O2, arm64 macOS; 15 rotating repetitions
per admitted problem, 25 for controls and std/caller updates. Correctness gates
finished before timing. Counter builds are excluded from timing/RSS. Frozen
natural sources are unchanged. Min / median / max are milliseconds.

| Natural cliff | Part A median | Part B natural min / med / max | C++ min / med / max | Ratio | Tuned median |
|---|---:|---|---|---:|---:|
| balanced-binary-tree | 1495.730 | 1480.689 / 1492.409 / 1630.331 | 12.939 / 13.834 / 15.441 | 107.88× | 27.501 |
| course-schedule | 4256.664 | 4286.587 / 4527.249 / 5350.041 | 21.860 / 22.991 / 24.936 | 196.91× | 41.831 |
| last-stone-weight | 64.268 | 52.582 / 54.093 / 55.791 | 10.589 / 10.790 / 12.225 | 5.01× | 24.989 |
| spiral-matrix | 28.873 | 27.208 / 27.611 / 28.476 | 7.312 / 7.457 / 8.046 | 3.70× | 25.129 |
| validate-binary-search-tree | 1413.920 | 1415.348 / 1429.602 / 1497.674 | 12.410 / 12.799 / 13.750 | 111.69× | 23.959 |

Natural forecast 19–20: measured 19. Tuned forecast 22: measured 23, exceeding
the forecast; no natural gain is inferred. Other cliff forecasts were broadly
unchanged, with course schedule elevated in this batch. The complete 29-problem
timing/RSS/charge table is in `ROUND24_B.json`.

| Control | Part A binary min / med / max | Part B min / med / max | C++ min / med / max |
|---|---|---|---|
| append | 4.287 / 4.450 / 5.721 | 4.304 / 4.410 / 5.311 | 3.172 / 3.400 / 4.566 |
| scan | 7.263 / 7.451 / 8.687 | 7.176 / 7.466 / 8.421 | 9.679 / 9.990 / 10.719 |
| transform | 35.279 / 48.479 / 58.706 | 35.360 / 50.519 / 57.176 | 12.971 / 27.086 / 141.933 |

Append uses 1 MiB; transform uses 16 MiB. The historical scan fixture is actually
**17 MiB**, retained for comparability rather than relabelled 16 MiB. Transform
is byte-exact and double-transform round-trips. All three emitted LLVM IR files
are byte-identical to Part A. Paired 10,000-resample bootstrap median-delta 95%
intervals (seed 24401): append [-0.105, 0.029] ms, scan [-0.054, 0.119] ms,
transform [-1.334, 11.296] ms. Every interval contains zero; the absolute transform
50.519 ms is disclosed, not dismissed or replaced with a favourable rerun. Both
NIL binaries and C++ show higher file-I/O times than historical batches.

| Type / operation | Std min / med / max | Caller min / med / max | Ratio |
|---|---|---|---:|
| bytes swap | 23.481 / 23.710 / 42.061 | 6.249 / 6.446 / 14.895 | 3.68× |
| bytes pop | 12.510 / 12.901 / 23.361 | 6.577 / 7.222 / 22.626 | 1.79× |
| buffer swap | 23.094 / 23.945 / 35.678 | 6.552 / 6.827 / 13.080 | 3.51× |
| buffer pop | 13.203 / 13.369 / 26.075 | 7.036 / 7.587 / 21.805 | 1.76× |

## Peak RSS

| Natural cliff | NIL median MiB | C++ median MiB | NIL/C++ | Observed live guard MiB |
|---|---:|---:|---:|---:|
| balanced-binary-tree | 7.062 | 11.203 | 0.630 | 3.815 |
| course-schedule | 16.281 | 13.297 | 1.224 | 9.156 |
| last-stone-weight | 3.766 | 4.516 | 0.834 | 1.526 |
| spiral-matrix | 4.625 | 6.094 | 0.759 | 2.286 |
| validate-binary-search-tree | 6.953 | 8.656 | 0.803 | 3.052 |

RSS samples are separate from timing; three samples per binary. The dedicated
stack reserves virtual address space, not a claim of 32 MiB resident overhead.
Live-guard instrumentation is separate; memory safety guard is 256 MiB.

## Copy census

Native O0 mechanisms joined to reference observations; strict classification
includes root retention. O2 surviving physical copies are not claimed. Trace
join cap and resource exclusions are reported, not silently treated as zero.
Fuzz census uses fixed host fixtures, distinct from randomized differential Hosts.

| Scope | Programs | Native copy events | Bytes | Required bytes | Avoidable bytes | Resource exclusions |
|---|---:|---:|---:|---:|---:|---:|
| application | 68 | 8,034 | 157,626 | 26,078 | 131,548 | 0 |
| neetcode-natural | 29 | 3,920,307 | 400,057,040,260 | 240,000,675,731 | 160,056,364,529 | 0 |
| neetcode-tuned | 29 | 3,420,177 | 60,208,452 | 3,060,795 | 57,147,657 | 0 |
| fuzz-24311 | 765 | 5,012 | 58,755,547 | 58,723,194 | 32,353 | 49 |
| fuzz-24312 | 765 | 5,015 | 58,754,074 | 58,723,188 | 30,886 | 49 |

| Frozen scope | Round 23 B2 bytes | Part B bytes | Delta |
|---|---:|---:|---:|
| application | 157,613 | 157,626 | +13 |
| neetcode-natural | 400,057,333,597 | 400,057,040,260 | -293,337 |
| neetcode-tuned | 60,501,789 | 60,208,452 | -293,337 |

Application payload delta is +13 bytes: first-fields CSV -18, adjacent-line dedupe
 -1, graph BFS +128, interval merge -96; circular-buffer classification changes
without a payload-byte change. These are reported, not rounded away.

The 399–400 GB forecast narrowly missed: 400.057 GB measured (decimal),
0.057 GB above the upper forecast, with only 293,337 bytes removed against
Round 23 B2. No material aggregate-copy improvement is claimed. Natural and
tuned 3sum each exceed the five-million-event native trace join cap on their
largest fixture; that fixture is excluded from native totals, as before. There
are no skipped reference programs. Each fixed-host fuzz census has 49 resource
exclusions; those are distinct from the differential campaigns’ 36 persistent
E008 comparisons. Do not conflate these denominators.

Raw per-program census, trace exclusions, reference totals and all classifications
are retained in JSON. New fuzz seeds/families are not a paired before/after estimate.

## Fuzz and resource integrity

Each seed 24311/24312: 765 programs, 1,642 native builds, all 765 indexed families,
including 32 new chain families; zero non-resource divergences and rule-3 failures.
112 comparisons escalate both paths jointly 4×; 76 resolve and match; 36 E008
remain inconclusive. No persistent E013. Host effects and input preservation are
checked before resource classification. 757 distinct program hashes per seed;
union 865, intersection 649. Each indexed family ran once.

| Reference outcome | 24311 | 24312 |
|---|---:|---:|
| E008 | 18 | 18 |
| E009 | 14 | 14 |
| E012 | 39 | 39 |
| E013 | 38 | 38 |
| E014 | 16 | 16 |
| E015 | 12 | 12 |
| E016 | 15 | 15 |
| E017 | 10 | 10 |
| E018 | 11 | 11 |
| E019 | 3 | 3 |
| E020 | 6 | 6 |
| E021 | 35 | 35 |
| E022 | 3 | 3 |
| OK | 545 | 545 |

The historical 88 E013 comparisons are attributable: ten invalid-length cases
became exact E014 in Part A; two later-operand faults become E012 under ADR 048;
the remaining 76 resolve exactly at 4×. The table lists every current resource
family/direction per seed, rather than hiding them behind a total.

| Original resource family/direction | Comparisons per seed |
|---|---:|
| `binding_live_quota:both:reference=E013:native=E013` | 2 |
| `bulk_quota_failure:both:reference=E013:native=E013` | 2 |
| `bytes_allocation_guard:both:reference=E013:native=E013` | 2 |
| `collection_live_children_quota:both:reference=E013:native=E013` | 2 |
| `collection_quota:both:reference=E013:native=E013` | 2 |
| `collection_zero_quota:both:reference=E013:native=E013` | 2 |
| `each_ignored_value_quota:both:reference=E013:native=E013` | 2 |
| `field_append_quota_alias:both:reference=E013:native=E013` | 2 |
| `g2_allocation_barrier:both:reference=E013:native=E013` | 2 |
| `hof_quota:both:reference=E013:native=E013` | 2 |
| `host_directory_quota:both:reference=E013:native=E013` | 2 |
| `host_env_quota:both:reference=E013:native=E013` | 2 |
| `inline_push_quota:reference-only:reference=E013:native=OK` | 2 |
| `io_buffer_retention:both:reference=E013:native=E013` | 2 |
| `io_callee_retention:both:reference=E013:native=E013` | 2 |
| `io_map_and_child:both:reference=E013:native=E013` | 2 |
| `io_quota_before_late_fault:both:reference=E013:native=E013` | 2 |
| `io_quota_real_read:both:reference=E013:native=E013` | 2 |
| `io_record_buffer_child:both:reference=E013:native=E013` | 2 |
| `io_record_child:both:reference=E013:native=E013` | 2 |
| `io_selected_lazy:both:reference=E013:native=E013` | 2 |
| `map_byte_constructor_quota:both:reference=E013:native=E013` | 2 |
| `map_constructor_quota:both:reference=E013:native=E013` | 2 |
| `map_key_result_quota:both:reference=E013:native=E013` | 2 |
| `map_lookup_result_quota:both:reference=E013:native=E013` | 2 |
| `map_put_quota:both:reference=E013:native=E013` | 2 |
| `map_quota_boundary:both:reference=E013:native=E013` | 2 |
| `module_live_quota:both:reference=E013:native=E013` | 2 |
| `module_quota_boundary:both:reference=E013:native=E013` | 2 |
| `nested_builder_quota:both:reference=E013:native=E013` | 2 |
| `parsebuf_quota_priority:both:reference=E013:native=E013` | 2 |
| `plugin_argument_quota_order:both:reference=E013:native=E013` | 2 |
| `plugin_live_quota:both:reference=E013:native=E013` | 2 |
| `reconcile_quota_failure:both:reference=E013:native=E013` | 2 |
| `record_live_quota:both:reference=E013:native=E013` | 2 |
| `record_map_quota:both:reference=E013:native=E013` | 2 |
| `std_callback_quota:both:reference=E013:native=E013` | 2 |
| `transfer_quota_partial:both:reference=E013:native=E013` | 2 |
| `unbounded_stack_large_record:both:reference=E008:native=E008` | 12 |
| `unbounded_stack_mutual:both:reference=E008:native=E008` | 12 |
| `unbounded_stack_sequence:both:reference=E008:native=E008` | 12 |

Persistent outcomes: large-record both E008 12; sequence both E008 12; mutual
both E008 10 and reference-only E008/native OK 2; native-only 0. E008 exact depth
is ordinary resource behaviour. Full call-family counts, hashes and diagnostic
counts are in JSON.

## Gate command receipts

Logs, raw JSON, compiler patch and IR are archived outside git at
`~/.local/share/nil/round24-chains/part-b/`; committed JSON hashes every receipt.

```text
./scripts/ci.sh                                  577 passed; zero warnings
./scripts/ci.sh release                          577 passed; zero warnings
./scripts/sanitize.sh                            265 passed; no ASan/UBSan finding
./scripts/fuzz-v5.sh --seed 24311 --out /tmp/nil-round24-b-fuzz-24311
./scripts/fuzz-v5.sh --seed 24312 --out /tmp/nil-round24-b-fuzz-24312
                                                full coverage; 0 non-resource divergences
python3 benchmarks/corpora/application-v5/verify.py --output /tmp/nil-round24-b-corpus.json
                                                2,815 checks; 68 verified NIL; 0 inconclusive
python3 benchmarks/corpora/application-v5/verify.py --group original --output /tmp/nil-round24-b-original.json
                                                exactly 610; 0 inconclusive
python3 benchmarks/corpora/neetcode150/verify.py --verified-only --jobs 1 --candidate-dir /Users/ninjacornix/NIL/benchmarks/core-generalize-study/natural --output /tmp/nil-round24-b-natural.json
python3 benchmarks/corpora/neetcode150/verify.py --verified-only --jobs 1 --output /tmp/nil-round24-b-tuned.json
                                                1,070 each; 29 programs; 0 inconclusive
python3 benchmarks/core-generalize-study/measure_controls.py --repeats 25 --baseline-compiler /tmp/nil-round24-b-baseline/target/release/nil --baseline-revision cceff2f --output /tmp/nil-round24-b-controls.json
python3 benchmarks/core-generalize-study/measure_cohort.py --repeats 15 --output /tmp/nil-round24-b-cohort.json
python3 benchmarks/core-memory-study/measure_updates.py --repeats 25 --output /tmp/nil-round24-b-updates.json
python3 benchmarks/core-generalize-study/reference_profile.py --copies --working-tree --output /tmp/nil-round24-b-overlay
python3 benchmarks/core-generalize-study/copy_census.py --overlay /tmp/nil-round24-b-overlay --scope <application|neetcode-natural|neetcode-tuned|fuzz:24311|fuzz:24312> --native --output <receipt.json>
```

## Accepted limits / next step

General path correlation and interprocedural G1 remain deferred. The 80 GB BST
retention observation is cross-region and is not solved by simultaneous chains.
Intermediate record aliases remain conservative. Std swap/pop still need Part C
inlining; no caller-parity claim is made. No syntax compression, new capability,
held-out attempt or density work. Nothing was pushed. Round 24 is not complete.
