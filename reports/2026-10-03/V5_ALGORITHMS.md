# expr-v5 algorithmic operations — measured result

**Sorting and snapshot iteration remove 398 of the 650 external cl100k surplus
(61.2%). The Python gap persists: 4.3–12.3% more tokens externally and 1.2–8.1%
more combined.** Counts match the preregistered whole-source forecasts exactly;
there are no shortfalls in these rewrites. This is source density, **not total
tokens until a correct program**. Generation remains unfavourable: [NIL 0/24,
Python 11/24](V5_GENERATION.md). No inference occurred.

## Preregistration and implementation

Main commit `c7048ee` records ADR 025 before `7917834` implements sort/each.
Benchmark `4864396` freezes prototypes against `920e510`; `6d36b83` commits
oracle-verified sort-only references and `81e602e` the combined rewrites.
[Forecast ledger](V5_ALGORITHMS_FORECAST.json), [actual recount and per-task
movement](V5_ALGORITHMS_BEFORE_AFTER.json), [spec](../../../docs/language/EXPR_V5.md).
Only sort and each were implemented. Comparison is subsumed by sort; classification
ranks lower. No identifier/punctuation compression or other language feature.

| Change | Gemma predicted / actual | Qwen | cl100k | o200k |
|---|---:|---:|---:|---:|
| Sort | 299 / 299 | 208 / 208 | 205 / 205 | 203 / 203 |
| Each, marginal after sort | 254 / 254 | 193 / 193 | 193 / 193 | 185 / 185 |
| Joint | 553 / 553 | 401 / 401 | 398 / 398 | 388 / 388 |

The standalone each forecast was 211/159/159/151. Its marginal saving after sort
is 254/193/193/185: sorted map iteration also eliminates owned-key repetition and
lookup scaffolding. Do not add overlapping standalone forecasts.

## Three unchanged cohorts

Cells show NIL before → after; baselines are unchanged. Positive percentages
mean NIL is larger. Unsupported tasks stay in the manifest, outside paired totals.
[Per-task/per-language/per-tokenizer CSV including bytes/characters](V5_ALGORITHMS_TOKENS.csv),
[JSON with pinned tokenizer/library versions and every loss](V5_ALGORITHMS_DENSITY.json).

| Cut | Tokenizer | NIL | Python | C++ | NIL vs Python | NIL vs C++ |
|---|---|---:|---:|---:|---:|---:|
| original (24 pairs) | Gemma 3 4B | 2144 → 2144 | 2227 | 5454 | -3.73% | -60.69% |
| original (24 pairs) | Qwen 2.5 7B | 1634 → 1634 | 1728 | 4235 | -5.44% | -61.42% |
| original (24 pairs) | cl100k | 1582 → 1582 | 1705 | 4217 | -7.21% | -62.49% |
| original (24 pairs) | o200k | 1571 → 1571 | 1712 | 4238 | -8.24% | -62.93% |
| new_external (32 pairs) | Gemma 3 4B | 7586 → 7033 | 6262 | 13128 | +12.31% | -46.43% |
| new_external (32 pairs) | Qwen 2.5 7B | 5828 → 5427 | 5112 | 10493 | +6.16% | -48.28% |
| new_external (32 pairs) | cl100k | 5686 → 5288 | 5036 | 10458 | +5.00% | -49.44% |
| new_external (32 pairs) | o200k | 5667 → 5279 | 5059 | 10498 | +4.35% | -49.71% |
| combined (56 pairs) | Gemma 3 4B | 9730 → 9177 | 8489 | 18582 | +8.10% | -50.61% |
| combined (56 pairs) | Qwen 2.5 7B | 7462 → 7061 | 6840 | 14728 | +3.23% | -52.06% |
| combined (56 pairs) | cl100k | 7268 → 6870 | 6741 | 14675 | +1.91% | -53.19% |
| combined (56 pairs) | o200k | 7238 → 6850 | 6771 | 14736 | +1.17% | -53.52% |

| Cut | NIL bytes / characters | Python | C++ |
|---|---:|---:|---:|
| original | 3310 / 3310 | 6746 / 6746 | 17283 / 17283 |
| new_external | 10668 / 10668 | 19423 / 19423 | 42130 / 42130 |
| combined | 13978 / 13978 | 26169 / 26169 | 59413 / 59413 |

All counted sources are ASCII, so bytes and characters coincide. Gemma and Qwen
use the pinned GGUF vocabularies, vocabulary-only, without BOS/EOS or inference;
Qwen is cross-checked against its official JSON tokenizer (170 streams, zero
mismatches). tiktoken 0.12.0 supplies cl100k/o200k; full hashes/versions are in JSON.
Counts are deterministic, not sampled model-use estimates.

## Per-task savings and non-improvements

| External task | Gemma | Qwen | cl100k | o200k |
|---|---:|---:|---:|---:|
| ex_acronym | 22 | 16 | 16 | 16 |
| ex_affine_cipher | 13 | 12 | 12 | 11 |
| ex_all_your_base | 0 | 0 | 0 | 0 |
| ex_allergies | 0 | 0 | 0 | 0 |
| ex_atbash_cipher | 29 | 23 | 23 | 22 |
| ex_baffling_birthdays | 0 | 0 | 0 | 0 |
| ex_beer_song | 0 | 0 | 0 | 0 |
| ex_binary | 20 | 13 | 13 | 13 |
| ex_binary_search | 0 | 0 | 0 | 0 |
| ex_book_store | 29 | 22 | 22 | 20 |
| ex_bottle_song | 0 | 0 | 0 | 0 |
| ex_bowling | 18 | 12 | 12 | 11 |
| ex_change | 0 | 0 | 0 | 0 |
| ex_circular_buffer | 0 | 0 | 0 | 0 |
| ex_clock | 0 | 0 | 0 | 0 |
| ex_collatz_conjecture | 0 | 0 | 0 | 0 |
| ex_connect | 32 | 24 | 24 | 24 |
| ex_crypto_square | 16 | 11 | 11 | 11 |
| ex_custom_set | 0 | 0 | 0 | 0 |
| ex_diamond | 0 | 0 | 0 | 0 |
| ex_difference_of_squares | 0 | 0 | 0 | 0 |
| ex_dnd_character | 0 | 0 | 0 | 0 |
| ex_dominoes | 32 | 26 | 26 | 23 |
| ex_eliuds_eggs | 0 | 0 | 0 | 0 |
| ex_etl | 36 | 29 | 26 | 27 |
| ex_flatten_array | 0 | 0 | 0 | 0 |
| ex_flower_field | 0 | 0 | 0 | 0 |
| ex_food_chain | 0 | 0 | 0 | 0 |
| ex_game_of_life | 0 | 0 | 0 | 0 |
| ex_grade_school | 306 | 213 | 213 | 210 |
| ex_hamming | 0 | 0 | 0 | 0 |
| ex_hello_world | 0 | 0 | 0 | 0 |

Eleven external tasks improve; 21 do not. No original task changes and no counted
reference gets larger. C++ remains larger on every supported task/tokenizer.
Python still wins/ties on many tasks: every non-win is enumerated in the density
JSON, including Connect, ETL and Grade School even after their improvements.
Grade School saves 213 cl100k tokens, ETL 26 and Connect 24; Connect still requires
explicit graph traversal, while ETL still parses a constrained JSON transport.

## Attribution movement

The ledger classifies each's delimiters alongside existing loop delimiters, its
name alongside intrinsics, and no implicit index/bounds as source bytes. This
extension leaves baseline categories unchanged. Primary rational byte-overlap and
secondary whole-token accounting both sum exactly to the gap and its reduction.
The integer ledger is shown to match the overseer's 650-token reproduction;
[exact fractions and all four tokenizers](V5_ALGORITHMS_BEFORE_AFTER.json) preserve
mixed-token sensitivity. A category change is bookkeeping, not an independent
causal estimate of another removable feature.

| cl100k category | Integer gap before | After | Movement | Rational movement |
|---|---:|---:|---:|---:|
| separator | 928 | 754 | -174 | -112.667 |
| loop_index_bound | 124 | 38 | -86 | -96.500 |
| identifier | -614 | -651 | -37 | -72.000 |
| loop_delimiters | 181 | 155 | -26 | -28.000 |
| operator | 375 | 348 | -27 | -27.667 |
| signature | 398 | 370 | -28 | -26.000 |
| numeric_literal | 394 | 371 | -23 | -23.000 |
| unchanged_state | 3 | 3 | +0 | -10.500 |
| call_identifier | 17 | 14 | -3 | -9.000 |
| boolean_literal | 47 | 42 | -5 | -5.000 |
| text_literal | -40 | -40 | +0 | -0.167 |
| comment | 0 | 0 | +0 | +0.000 |
| keyword | -388 | -388 | +0 | +0.000 |
| whitespace | -639 | -639 | +0 | +0.000 |
| intrinsic_name | -136 | -125 | +11 | +12.500 |
| **Total** | **650** | **252** | **−398** | **−398** |

Separators and index/bound scaffolding move most. Numeric literal surplus only
falls from 394 to 371: adding algorithms did not automatically remove ASCII
classification, coordinate arithmetic or format parsing. The remaining gap is not
shown to require mutation or a different evaluation model. More capability needs
its own justified forecast; names/punctuation are still not the answer.

## Verification, unsupported work and adaptation

**2400 checks pass**: reference 478; native 956 (478 each O0/O2); Python 483; C++
483. [Full verification](V5_ALGORITHMS_VERIFICATION.json). The original **610**
pass separately: 120/240/125/125. [Original receipt](V5_ALGORITHMS_ORIGINAL_VERIFICATION.json).
Sort-only external references passed **1790** checks before each rewrites.
[Intermediate receipt](V5_ALGORITHMS_SORT_VERIFICATION.json).
Tasks, fixtures, goldens, all Python/C++ sources and the original 24 NIL sources
are byte-identical to the locked cohort. Only eleven external NIL references change.
No existing valid source's language meaning changes; earlier profiles/default
remain unchanged. Hash-lock and attribution regression tests pass (22 Python tests).

**56 verified NIL programs / 56 JSONL exports; 19 unsupported, 18 external.**
Neither operation alone supplies any remaining task's missing capability/adapter.
[Retained task review](../../corpora/application-v5/ALGORITHMS_ATTEMPTS.md).
This is still a small adaptation seed, not a fine-tuning-scale or held-out corpus.
The external sample is the first 50 alphabetical Exercism first properties, not
random general-purpose coverage. Solutions are locally authored and finite fixture
oracles are not exhaustive equivalence proof. Density gains do not reverse the
failure-inclusive model result.

## Performance and storage limits

Same Apple M2/macOS27, Apple Clang21 O2, warm files, whole processes, one warmup,
nine samples, verified output. Compiles/verification excluded; no CPU isolation or
fsync. Controls rotate NIL/C++/Python order. Raw samples, source hashes, baseline
IR comparison and quota output are in [performance JSON](V5_ALGORITHMS_PERFORMANCE.json).
Prior medians are from V5_ATTRIBUTION_PERFORMANCE.json, not extrapolations.

| Control | Prior NIL ms | Current NIL | C++ | Python |
|---|---:|---:|---:|---:|
| newlines 16777216 | 7.755 | 7.644 | 10.256 | 24.700 |
| append 1048576 | 24.018 | 26.101 | 5.614 | 48.846 |
| transform 16 MiB | 37.832 | 38.252 | 15.478 | 809.424 |

Append's median is **8.7% higher**, transform's 1.1% higher; scan is 1.4% lower.
Retain those results rather than asserting no numerical regression. The four old
controls emit identical executable LLVM IR against `a839574`, except two unused
sort declarations. Runtime changes only add unreachable sort helpers on these
paths. Startup/OS variability and code layout are not isolated here; this evidence
shows no new root/loop work, not statistical proof of equal latency. Append still
loses to C++; transform does too; scan wins on this run. Double transformation
round-trips byte-exactly and append's full content is checked.

| Map insert count | Prior ms | Current ms |
|---|---:|---:|
| 1000 | 3.247 | 3.952 |
| 4000 | 2.915 | 2.963 |
| 16000 | 4.098 | 4.606 |
| 64000 | 10.232 | 11.297 |

The noisy startup floor remains visible; no sample is omitted. Different-length
map byte replacement still repacks linearly in owned payload; it is unchanged.
The insert ceiling remains 262145 entries; 262146 traps E013.

### New operation scaling

Whole-process setup is included: construct reverse-valued buffers/maps, sort and
verify sorted order through each; iteration-only cases construct inputs and reduce.
Map each materializes every owned key even if unused. This is not a kernel-only
sort benchmark or a C++ comparison, and no linear-time claim is made for sorting.
Heapsort guarantees O(n log n); sequence each is O(n), map each additionally pays
owned key/value byte-copy and lookup costs. Copy fallback preserves aliases.

| Workload | 1k ms | 4k | 16k | 64k | 1 Mi elements |
|---|---:|---:|---:|---:|---:|
| sort-buffer | 4.263 | 2.634 | 2.598 | 3.941 | 40.641 |
| sort-buffer-alias | 3.801 | 2.704 | 2.741 | 4.125 | — |
| sort-map | 3.959 | 3.203 | 5.664 | 16.432 | — |
| each-buffer | 3.414 | 2.545 | 2.281 | 2.283 | 3.347 |
| each-map | 3.906 | 3.173 | 5.248 | 13.616 | — |

Standalone sorting successfully reserves input plus output at 33554392 byte
elements or 4194299 i64 elements; the next element traps E013. In this decimal-key
map builder, sort+each passes 262144 entries and fails at 262145, because sorting
reserves full capacity twice. This is an operation-specific limit, not a change
to the insert ceiling or 64 MiB quota. Large keys/other live values lower limits.
Each map keys/byte values are owned copies, not free views. Re-sorting on each
iteration repeats O(n log n) work; alias retention can force copies. These costs
are specified, not silently optimized by weakening immutability.

Reproduce with the commands in the main repository's
[validation receipt](../../../docs/validation/V5_ALGORITHMS.md), including CI,
both sanitizer suites, three fuzz seeds and exact report-generation commands.
