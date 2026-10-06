# Round 16 — Guarded ownership: results and remaining gaps

**Filter, insertion sort and transform miss the C++ targets.** Source comparator
merge sort also remains much slower than core sort at large sizes and is not
migrated. This is a sound partial speed improvement, not C++ parity for builders
and updates generally. No compiler work beyond the measured proof boundary is
claimed. No model/density measurement was performed.

## Decision, history and proof census

Main baseline `80afb64`, benchmarks baseline `3c29173`. ADR 036 was accepted in
`73d694a` before compiler changes. `5285afd` adds the source sort prototype;
`24dbb69` adds guarded ordinary-callee replacement, old-scalar snapshots,
stack singleton temporaries and activation-local root frames; `94a5f9b` retains
proved canonical readonly loop inputs across allocations. Source spellings,
profiles, immutable semantics, quota and trap/effect ordering are unchanged.
35 intrinsic variants / 34 executable core bodies remain: **delta zero**.

Of 52 existing update-return sites in 18/68 programs, 41 have a caller semantic
last use and **7** have a closed fresh allocation call-entry uniqueness proof.
Neither number proves uniqueness throughout a callee. The actual update uses
semantic final use **and** the runtime exactly-one-root guard; aliases and child
edges force copies. This reuses the existing root handoff rather than introducing
an ownership ABI. A callee may create aliases after entry. Arguments remain
left-to-right; no allocation occurs in the zero-root handoff gap. Recursive frames
have distinct stack storage. Quota reservations remain even on reused updates.

Singleton RHS lowering saves zero source tokens. The preregistered push alternative
would save four cl100k/o200k tokens per call (9 to 5), but was rejected in favor of
speeding existing programs without another primitive.

## Method

macOS arm64, Apple Clang 21.0.0, Rust 1.98.1. Same Clang for NIL/C++, O2, C++17;
C++ controls use `-O2 -lc++`. Whole-process wall time includes startup, applicable
read/write, initialization and stdout capture. 25 rotating warm repetitions,
one discarded warm-up, no CPU isolation. Every result is checked byte-exact.
16 MiB paired input repeats bytes 0..255; filter keeps even bytes (exactly half).
Insertion uses reversed 2048 elements and the **same insertion algorithm** in
C++; comparator merge sort uses deterministic LCG values. Sort timings include
fill and full-array output. The fixed-bound append control and historical
runtime-bound append are separately reported. The scan fixtures also differ;
only the historical table is directly compared with historical medians.

This measures these implementations on one machine, not general workload parity.
Min/max expose scheduler noise; no confidence interval or isolated-kernel claim.
Raw binaries, logs, samples, IR and disassembly stay outside git under
`/tmp/nil-ownership/`. Commands are in [the study README](../../ownership-study/README.md).

## Paired controls (milliseconds, min / median / max)

| Control | NIL before | NIL after | C++ after | After median / C++ |
|---|---:|---:|---:|---:|
| append | 22.807 / 23.423 / 24.477 | 5.030 / 5.737 / 6.199 | 4.717 / 5.008 / 6.068 | 1.15x |
| filter_hand | 574.170 / 576.537 / 580.007 | 537.573 / 538.919 / 543.143 | 29.069 / 30.104 / 30.622 | 17.90x |
| filter_std | 358.351 / 413.389 / 422.838 | 273.383 / 274.521 / 418.937 | 29.069 / 30.104 / 30.622 | 9.12x |
| map_hand | 45.417 / 45.942 / 46.250 | 35.092 / 35.652 / 73.888 | 18.022 / 18.658 / 20.044 | 1.91x |
| map_std | 45.231 / 45.670 / 46.153 | 35.109 / 35.551 / 38.617 | 18.022 / 18.658 / 20.044 | 1.91x |
| scan | 8.162 / 8.590 / 9.015 | 8.105 / 8.482 / 10.982 | — | — |
| insertion_hof | 1017.357 / 1019.821 / 1067.886 | 60.180 / 60.755 / 64.145 | 4.474 / 4.748 / 5.034 | 12.80x |
| insertion_hand | 1016.395 / 1019.537 / 1101.430 | 60.381 / 60.651 / 64.977 | 4.474 / 4.748 / 5.034 | 12.77x |
| transform | 34.699 / 35.402 / 36.950 | 34.346 / 35.030 / 39.779 | 11.640 / 12.157 / 13.541 | 2.88x |
| sort_core_1024 | 3.571 / 3.968 / 4.298 | 3.223 / 3.974 / 8.793 | 2.894 / 4.018 / 4.183 | 0.99x |
| sort_source_1024 | 3.875 / 4.104 / 5.188 | 3.511 / 3.683 / 7.151 | 2.894 / 4.018 / 4.183 | 0.92x |
| sort_core_65536 | 9.327 / 9.644 / 9.966 | 9.465 / 9.559 / 12.712 | 8.520 / 8.788 / 13.926 | 1.09x |
| sort_source_65536 | 112.270 / 116.481 / 124.465 | 68.313 / 72.123 / 93.806 | 8.520 / 8.788 / 13.926 | 8.21x |
| sort_core_1048576 | 130.188 / 131.194 / 131.955 | 130.185 / 131.151 / 150.044 | 96.027 / 96.414 / 98.499 | 1.36x |
| sort_source_1048576 | 2427.959 / 2477.817 / 2538.790 | 1321.810 / 1360.087 / 1512.337 | 96.027 / 96.414 / 98.499 | 14.11x |

Filter handwritten form repeats the checked index in its predicate; std passes a
single scalar argument to the callback. Both are retained unchanged in this study;
this is not evidence that arbitrary handwritten forms match std.

## Exact historical controls

| Control | Historical median | Same-session before | Same-session after | C++ | After / C++ |
|---|---:|---:|---:|---:|---:|
| append | 22.534 | 21.630 / 22.090 / 30.984 | 4.170 / 4.475 / 10.129 | 3.306 / 3.530 / 6.219 | 1.27x |
| scan | 7.507 | 7.096 / 7.470 / 8.707 | 7.064 / 7.497 / 10.534 | 9.719 / 10.216 / 12.855 | 0.73x |
| transform | 35.047 | 35.106 / 36.499 / 40.088 | 35.182 / 36.568 / 39.637 | 12.486 / 13.739 / 17.405 | 2.66x |

Scan is unchanged within noise. Transform is unchanged versus the paired baseline;
the variation against older 35.047 ms is also present in this session's baseline.
Exact transform output and double-transform round trip pass. Append meets the
1.5x C++ target with reserve-free vector growth. The other targets do not.

## Forecast versus actual (NIL median milliseconds)

| Candidate | Preregistered forecast | Actual | Finding |
|---|---|---|---|
| Append fixed-bound | 6–12 | 5.737 | Better than forecast; historical control also meets target |
| Std filter | 40–120 | 274.521 | Under-delivers; allocating lazy-region root traffic remains |
| Transform | 25–40 without vectorization | 35.030 | In range, target missed; no write vectorization |
| Insertion callback | 8–60 | 60.755 | Slightly outside forecast; far from 2x C++ target |
| Source sort 1k | 2–8 | 3.683 | In range |
| Source sort 64k | 10–100 | 72.123 | In range |
| Source sort 1M | 150–1000 | 1360.087 | Under-delivers; keep core sort |

## IR and vectorization evidence

Old swap callee emitted two copying `nil_set` calls. New lowered swap:

```llvm
%old = alloca i64
%rhs = call i64 @nil_get(ptr %input, i64 %j, ...)
%first = call ptr @nil_set_unique_capture(ptr %input, i64 %j_minus_1, i64 %rhs, ptr %old, ...)
%saved = load i64, ptr %old
%second = call ptr @nil_set_unique(ptr %first, i64 %j, i64 %saved, ...)
```

The snapshot is only admitted for the structurally identical already-checked
index with a nontrapping, nonallocating, effect-free scalar interval. No source
step/tick moves; original replacement bounds → byte → prospective quota order
and spans remain. Any other old reads, effects or live aliases retain copying.
Regression tests cover both paths, bounds failure and observable host effects.

Singleton builder IR has `nil_make_temporary` followed by concat and
`nil_temporary_release`, rather than an arena allocation for the RHS. Its virtual
root and full header/capacity charge remain, preventing a quota advantage.
Root frame IR allocates 24-byte activation-local storage and passes it to
`nil_roots_enter`; links and sequence slots remain conservative.

`paired-after/scan.asm` contains `cmeq.16b` in the scan loop (addresses
0x100000844 and 0x1000008b4). **Readonly scan vectorization survives.** Neither
materialized map form nor transform has vector byte subtraction in its loop.
Readonly canonical identity-carried input access can cache its data pointer
across allocations while its root stays retained; modified/shifted indices stay
checked. Writable updates can copy/reallocate, and runtime physical uniqueness is
not a compile-time whole-loop fact. No unchecked store/noalias assertion was
introduced. This round does not discharge the stronger proof needed to vectorize
writes.

## Remaining cost boundaries

* Filter allocates inside a sequence-valued lazy arm. Existing retention excludes
  that shape: root transfers and live-charge updates still run per iteration.
  Singleton heap allocation is removed, but this root protocol is not. These are
  visible IR costs; no profiler percentage is asserted.
* Insertion avoids whole-buffer copies when the guard succeeds, but each swap
  still links root frames, transfers argument/result roots and performs two checked
  guarded updates. Reversed 2048 elements perform 2,096,128 swaps. Root-slot
  recycling across arbitrary callee bodies is not implemented here.
* Source merge sort copies slices and evaluates its comparator three times per
  merged element. Recursive allocating calls remain conservatively rooted. It is
  stable for a consistent strict ordering; effectful comparators retain those
  source-ordered calls. It stays an explicit module prototype, not core migration.
* Aliased replacements/concat still copy. Arbitrary old-read scheduling, aggregate
  snapshots, allocating lazy-arm retention and whole-loop unique write versioning
  remain out of the proof. Bounds, byte, quota, effect and alias checks are intact.

## Frozen corpus runtime changes

68 supported programs, one unchanged golden each, O2 bounded native, 25 rotating
paired repetitions; every output and input preservation checked. These tiny
fixtures largely measure startup, so no algorithmic speedup is inferred.
Median task after/before ratio: **0.9931**. Sum of task medians: 163.934 → 162.974 ms.

| Task | Before min / median / max | After min / median / max |
|---|---:|---:|
| ascii_upper | 2.119 / 2.330 / 4.657 | 2.068 / 2.308 / 5.033 |
| ascii_lower | 2.132 / 2.358 / 4.492 | 2.162 / 2.364 / 4.808 |
| rot13 | 2.131 / 2.526 / 5.600 | 2.158 / 2.499 / 6.444 |
| invert_bytes | 2.170 / 2.475 / 3.563 | 2.172 / 2.438 / 6.557 |
| reverse_bytes | 2.114 / 2.427 / 5.167 | 2.184 / 2.401 / 5.826 |
| hex_encode | 2.196 / 2.374 / 4.843 | 2.098 / 2.412 / 5.585 |
| count_newlines | 2.116 / 2.350 / 5.071 | 2.031 / 2.398 / 5.957 |
| nonempty_lines | 2.097 / 2.446 / 4.452 | 2.147 / 2.392 / 5.354 |
| normalize_crlf | 2.116 / 2.442 / 4.966 | 2.093 / 2.350 / 5.432 |
| prefix_lines | 2.224 / 2.378 / 5.086 | 2.150 / 2.442 / 6.032 |
| first_fields_csv | 2.112 / 2.379 / 5.126 | 2.111 / 2.340 / 5.774 |
| sum_pairs | 2.105 / 2.322 / 4.642 | 2.199 / 2.340 / 5.326 |
| sum_integers | 2.226 / 2.507 / 4.802 | 2.132 / 2.373 / 6.283 |
| min_max | 2.099 / 2.366 / 5.110 | 2.169 / 2.319 / 5.980 |
| dedupe_adjacent_lines | 2.093 / 2.392 / 5.497 | 2.025 / 2.412 / 6.484 |
| running_report | 2.212 / 2.372 / 4.917 | 2.169 / 2.465 / 6.402 |
| number_lines | 2.081 / 2.373 / 4.131 | 2.131 / 2.343 / 5.683 |
| histogram_digits | 2.151 / 2.457 / 4.891 | 2.169 / 2.385 / 5.984 |
| buffer_sum | 2.203 / 2.359 / 4.219 | 2.083 / 2.394 / 4.785 |
| buffer_dot | 2.107 / 2.363 / 4.423 | 2.148 / 2.427 / 4.964 |
| prefix_sums | 2.161 / 2.405 / 5.010 | 2.197 / 2.374 / 5.629 |
| copy_file | 2.163 / 2.442 / 5.218 | 2.136 / 2.354 / 6.005 |
| slice_file | 2.121 / 2.383 / 4.305 | 2.151 / 2.352 / 5.210 |
| expand_tabs | 2.176 / 2.316 / 4.732 | 2.127 / 2.339 / 6.144 |
| env_lookup | 2.146 / 2.414 / 2.992 | 2.138 / 2.436 / 3.182 |
| ex_accumulate | 2.193 / 2.461 / 5.425 | 2.258 / 2.463 / 6.249 |
| ex_acronym | 2.140 / 2.352 / 4.809 | 2.178 / 2.376 / 5.527 |
| ex_affine_cipher | 2.034 / 2.381 / 5.071 | 2.158 / 2.364 / 6.104 |
| ex_all_your_base | 2.158 / 2.397 / 4.379 | 2.057 / 2.432 / 4.968 |
| ex_allergies | 2.132 / 2.395 / 4.692 | 2.121 / 2.337 / 5.087 |
| ex_armstrong_numbers | 2.097 / 2.329 / 4.820 | 2.018 / 2.332 / 5.670 |
| ex_atbash_cipher | 2.196 / 2.422 / 5.237 | 2.152 / 2.329 / 6.247 |
| ex_baffling_birthdays | 2.201 / 2.500 / 9.543 | 2.199 / 2.483 / 28.163 |
| ex_beer_song | 2.429 / 2.624 / 5.260 | 2.321 / 2.583 / 6.181 |
| ex_binary | 2.069 / 2.370 / 4.863 | 2.214 / 2.396 / 5.879 |
| ex_binary_search | 2.079 / 2.429 / 5.339 | 2.080 / 2.491 / 6.572 |
| ex_binary_search_tree | 2.190 / 2.450 / 5.093 | 2.194 / 2.438 / 6.960 |
| ex_book_store | 2.131 / 2.363 / 4.585 | 2.189 / 2.355 / 5.353 |
| ex_bottle_song | 2.139 / 2.441 / 4.960 | 2.113 / 2.449 / 6.369 |
| ex_bowling | 2.192 / 2.439 / 4.711 | 2.066 / 2.415 / 5.958 |
| ex_change | 2.074 / 2.445 / 4.816 | 2.098 / 2.361 / 5.554 |
| ex_circular_buffer | 2.183 / 2.431 / 5.015 | 2.203 / 2.416 / 6.033 |
| ex_clock | 2.159 / 2.424 / 4.867 | 2.087 / 2.334 / 5.893 |
| ex_collatz_conjecture | 2.192 / 2.441 / 4.930 | 2.133 / 2.406 / 5.588 |
| ex_complex_numbers | 2.044 / 2.294 / 4.845 | 2.073 / 2.360 / 5.352 |
| ex_connect | 2.095 / 2.417 / 5.411 | 2.242 / 2.440 / 5.712 |
| ex_crypto_square | 2.201 / 2.413 / 4.824 | 2.177 / 2.392 / 6.084 |
| ex_custom_set | 2.133 / 2.368 / 4.330 | 2.123 / 2.380 / 5.243 |
| ex_darts | 2.072 / 2.367 / 4.281 | 2.104 / 2.348 / 5.078 |
| ex_diamond | 2.170 / 2.405 / 4.619 | 2.110 / 2.312 / 5.947 |
| ex_difference_of_squares | 2.109 / 2.354 / 4.951 | 2.045 / 2.408 / 6.026 |
| ex_dnd_character | 2.134 / 2.399 / 4.441 | 2.160 / 2.404 / 4.743 |
| ex_dominoes | 2.092 / 2.443 / 4.366 | 2.076 / 2.399 / 5.490 |
| ex_eliuds_eggs | 2.127 / 2.478 / 5.113 | 2.067 / 2.490 / 6.320 |
| ex_etl | 2.311 / 2.493 / 2.996 | 2.278 / 2.444 / 4.940 |
| ex_flatten_array | 2.089 / 2.422 / 39.442 | 2.117 / 2.362 / 16.279 |
| ex_flower_field | 2.228 / 2.425 / 3.258 | 2.247 / 2.383 / 10.148 |
| ex_food_chain | 2.208 / 2.381 / 4.452 | 2.147 / 2.411 / 5.487 |
| ex_game_of_life | 2.199 / 2.370 / 4.771 | 2.222 / 2.344 / 5.878 |
| ex_go_counting | 2.187 / 2.389 / 5.456 | 2.109 / 2.437 / 6.710 |
| ex_grade_school | 2.130 / 2.424 / 4.236 | 2.152 / 2.380 / 4.747 |
| ex_grains | 2.190 / 2.414 / 5.050 | 2.209 / 2.397 / 6.528 |
| ex_hamming | 2.114 / 2.381 / 4.326 | 2.084 / 2.407 / 5.423 |
| ex_hello_world | 2.230 / 2.431 / 4.752 | 2.198 / 2.426 / 6.314 |
| ex_algo_linked_list | 2.120 / 2.404 / 4.603 | 2.112 / 2.408 / 10.110 |
| ex_algo_bst_walk | 2.173 / 2.512 / 5.029 | 2.148 / 2.487 / 5.790 |
| ex_algo_graph_bfs | 2.104 / 2.481 / 4.935 | 2.227 / 2.370 / 6.108 |
| ex_algo_interval_merge | 2.173 / 2.423 / 5.431 | 2.139 / 2.368 / 6.495 |

## Validation receipts

All compiler gates ran after the final backend change. A final corpus run is also
repeated after that change rather than relying on a run started during editing.

| Command | Result | External receipt |
|---|---|---|
| `./scripts/ci.sh` | 455 passed; strict Clippy clean | gates-ci-debug.log |
| `./scripts/ci.sh release` | 455 passed; strict Clippy clean | gates-ci-release.log |
| `./scripts/sanitize.sh` | 188 passed, all suites; no ASan/UBSan finding | gates-sanitize.log |
| `python -m unittest discover -s benchmarks/generation/standing/tests` | 46 passed; reports only temporary storage | final-harness.log |
| `verify.py --output /tmp/nil-ownership/post-change-corpus.json` | 2,815 checks | post-change-corpus.log/json |
| `verify.py --group original --output /tmp/nil-ownership/post-change-original.json` | Exactly 610 checks | post-change-original.log/json |

Fuzz commands: `./scripts/fuzz-v5.sh --seed <seed> --out /tmp/nil-ownership/gates-fuzz-<seed>`.
Every campaign uses default full coverage.

| Seed | Programs | Native O0/O2 builds | Family indices hit | Divergences |
|---|---:|---:|---:|---:|
| 5130572 | 461 | 922 | 461 | 0 |
| 907221 | 461 | 922 | 461 | 0 |
| 160016 | 461 | 922 | 461 | 0 |

Per-code counts **per seed**, identical across all three:

| Code | Count |
|---|---:|
| E009 | 3 |
| E012 | 24 |
| E013 | 32 |
| E014 | 8 |
| E015 | 8 |
| E016 | 14 |
| E017 | 10 |
| E018 | 11 |
| E019 | 3 |
| E020 | 6 |
| E021 | 5 |
| E022 | 3 |
| OK | 334 |

Every one of 461 family indices executes once per seed. Every new named family
below executes once per seed (3 total each), comparing host stdout/files as well
as values and diagnostic codes. Fixed family shapes mean this is seeded structured
coverage, not exhaustive alias exploration; equal code counts are expected. Across these seeds, 574 distinct program hashes occur; each seed has 453 distinct hashes.

`retained_read_alias`, `retained_read_shifted`, `singleton_alias_rhs`, `singleton_buffer_builder`, `singleton_byte_range`, `singleton_bytes_builder`, `singleton_literal_builder`, `transfer_bounds_partial`, `transfer_effect_order`, `transfer_empty_bounds`, `transfer_lazy_selected`, `transfer_lazy_unselected`, `transfer_live_alias`, `transfer_loop_builder`, `transfer_mutual_recursion`, `transfer_quota_partial`, `transfer_record_child_alias`, `transfer_recursion`, `transfer_return_alias`, `transfer_swap_alias`, `transfer_swap_bounds`, `transfer_swap_effect_barrier`, `transfer_zero_slot_records`.

No runtime divergence or sanitizer finding was found in this round. A malformed
new generator case referenced an unknown function and was corrected before the
campaign. An old IR test assumed a single later old read must copy; the proved
snapshot now admits it, so the test retains two old reads to exercise copying.
These are generator/test changes, not hidden oracle changes. Existing corpus,
parser/HIR semantics, default/earlier profiles and goldens remain unchanged.

## Raw evidence hashes

Files are external local artifacts, not committed results or credentials. The
hashes below identify measured JSON and command logs; they do not make temporary
paths durable. Archive the external directory before removing it.

| Artifact under /tmp/nil-ownership | SHA-256 |
|---|---|
| paired-before/results.json | `bacea4dbf788378d08ddc9ee31a50c459cf2e369f760b61d8cfeec005d0334da` |
| paired-after/results.json | `f5ccbaf79f4e01e4d984d409626abecb40b45399a7d1796ecc5413983a91be4b` |
| historical/results.json | `676a1ceb1aacb0468344ad4a90c6c71c7dcb9373d95b736eed2276907ae9d33f` |
| corpus-runtime/results.json | `d3804236dba7b139fd19309e86191dce3ec1723f69f3c03045aa7e79f763abe9` |
| census-final/results.json | `30e8f044d39265f5c497a76396f945e6b2cfa3450aa5fd3f01b8600dec8f90d5` |
| gates-ci-debug.log | `8985f9b64a129841bd7248a5f37fe120ccd5461167bbce49913cc4e33d97de0c` |
| gates-ci-release.log | `820fe92f075bcb17166167b8fba4f7794f6e5c4a55572879b7438851d7296b0d` |
| gates-sanitize.log | `ef77f81ad3d7d9ebebb89d54423e171f5eb9f0f6687a62b24db407cd001ae7c3` |
| final-harness.log | `79e506002d021b707144a9a40c13cce294a4239a821d8360272ed01da9f99263` |
| gates-fuzz-5130572.log | `f7866f7522425ab9d229d090a0cf01ef7c87c86751b5ba673950d9edb6a7f10e` |
| gates-fuzz-907221.log | `e14b052d2df49b0dd289a01b63393df609a1acd7d8c810cdef3553f991978b94` |
| gates-fuzz-160016.log | `03a5dea42a4e623a2dab3f703a5ea476b104a6a723d887bd46c82a18309cd46e` |
| post-change-corpus.log | `968238ea81da6ba9a40080cea550dae8eebc6b8cbad85a8c0cc7e2188577d6b4` |
| post-change-corpus.json | `b290703d10bcef58f03a1061572771f4786f1e787c376bc55f7ae6a2b25f3491` |
| post-change-original.log | `cc2b35df8397799273b7a689cb46586b0c4175f4921b1098f60b62d809a0fd06` |
| post-change-original.json | `f6ef6ad9146571918226b69deec10971dc23762cd32877587875c261557e3013` |
