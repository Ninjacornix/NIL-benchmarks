# Round 20 — scalar operators, constants, local bindings, and corrected density

[ADR 042](../../../docs/adr/042.md) preregistered this round before any compiler
change. It governs the scalar operator/constant/binding surface, the five cliff
rewrites, the three density cuts and the forecast ranges checked below. Compiler
base `851223b`, measured at `0bedd91`; suite definitions at benchmarks `44ce5bb`.
Apple clang 21.0.0, macOS arm64, Rust 1.98.1, tiktoken 0.12.0. Receipt hashes are
in `ROUND20_EVIDENCE.json`, token counts in `ROUND20_DENSITY.json`, historical
controls in `ROUND20_CONTROLS.json`. Raw logs stay outside git.

## Unfavourable results first

**On the honest density cut, NIL loses badly to Python.** Counting algorithm
kernels only — with file decoding, encoding and drivers excluded for all three
languages — NIL needs **4,348 cl100k tokens against Python's 2,609: +66.7%**
(o200k +66.7%). It also loses to C++ (3,366 tokens, +29.2%/+27.7%). NIL beats
Python on only **4 of 29** kernels. Round 19's headline "~19% below Python" was
produced by a repeated Python input adapter, not by denser algorithms. ADR 042
forecast exactly this and the measurement landed inside its 20–100% band.

**The heap cliff is not fixed.** Last Stone Weight was forecast at a 15–100 ms
median. It measures **1,951.81 ms, 168.89× C++** — 19.5× above the top of the
forecast range and still the suite's largest miss. The binding removed repeated
child-index calls and cut the time 14.3×, from 27,940 ms, but something still
keeps an alias live across the heap swap. A binding alone does not establish
unique ownership, which ADR 042 stated as a hypothesis rather than a conclusion.

**Spiral Matrix improved by 56× and still misses the bound** at 3.30×, just
outside ≤3×. Three cliff samples grew slightly in source tokens (spiral +12,
course-schedule +9, validate-BST +8 cl100k): the rewrites bought runtime, not
density.

**Seven of 29 admitted samples still miss ≤3× C++**, and 114 of 150 problems
still have no NIL attempt. Core 1.0 is not complete. Nothing here measures model
token efficiency; the NIL 0/24 versus Python 11/24 generation result stands.

## Qualification count

**22 of 150** problems meet both the correctness and ≤3× C++ gates, up from 19.
Seven blocked candidates and 114 unattempted problems are unchanged; no task was
newly validated or removed. `corpora/neetcode150/STATUS.json` totals:

| | Round 19 | Round 20 |
|---|---:|---:|
| meets-bound | 19 | **22** |
| performance-miss | 10 | **7** |
| validation-blocked | 7 | 7 |
| unattempted | 114 | 114 |
| verified NIL sources | 29 | 29 |

Newly meeting the bound: `balanced-binary-tree`, `validate-binary-search-tree`,
`course-schedule`. Nothing regressed out of the bound. Re-verification passed
**1,070 of 1,070** checks across reference, native O0 and native O2.

## The three density cuts

Every count is a complete standalone or kernel source, tokenized with real
tiktoken 0.12.0. Bytes equal characters (ASCII sources). Cuts are ordered least
to most favourable to NIL. **Source density is not total model tokens to a
correct program, and this is a selected 29-problem survivor cohort.**

| Cut | NIL cl100k / o200k | Python | C++ | NIL vs Python | NIL vs C++ |
|---|---:|---:|---:|---:|---:|
| **Kernel only** | 4,348 / 4,368 | 2,609 / 2,620 | 3,366 / 3,420 | **+66.7% / +66.7%** | +29.2% / +27.7% |
| Minimal I/O | 5,321 / 5,347 | 5,308 / 5,319 | 10,754 / 10,929 | **+0.2% / +0.5%** | −50.5% / −51.1% |
| Full program | 5,321 / 5,347 | 6,795 / 6,818 | 10,610 / 10,716 | **−21.7% / −21.6%** | −49.8% / −50.1% |

Bytes: kernel 7,761 / 8,444 / 9,589; minimal I/O 10,280 / 18,464 / 33,266;
full program 10,280 / 25,474 / 35,044 (NIL / Python / C++).

The NIL column is identical for minimal I/O and full program because NIL's file
adapters are already compact; its minimal-I/O copy is the admitted source
unchanged. Python drops 7,010 bytes and 1,487 cl100k tokens when its repeated
`Numbers` reader is replaced by an idiomatic iterator baseline. That single
adapter is the entire Round 19 "advantage".

### What each cut counts

* **Full program:** the admitted NIL sources and the historical standalone
  Python/C++ files, reproducing Round 19 including its repeated Python reader.
* **Kernel only:** typed algorithm functions, every transitive algorithm helper,
  signatures, required record/type declarations and imports. Byte decoding,
  encoding and file drivers are excluded in all three languages. NIL keeps its
  real flat-buffer layout arithmetic and metadata offsets; no free adapter hides
  them. All language-specific kernel helpers are counted.
* **Minimal I/O:** new iterator/stream-based baseline copies, written only for
  measurement.

### Representation notes (interface differences, not a cheaper algorithm)

Separating formatting changes the result representation of four NIL algorithms,
and these differences are material when reading the kernel column:

* **3sum** streams typed triples through an explicit static callback. Materializing
  the largest fixture's 1,124,250 integer triples exceeded the unchanged 64 MiB
  quota at reference, O0 and O2. The callback signature and state cost stay inside
  the kernel count; only the formatter is an adapter.
* **generate-parentheses** and **letter-combinations-of-a-phone-number** expose
  completed strings through static output callbacks. A materialized record-buffer
  parentheses copy hit the reference timeout and is **not** included as verified.
* **Interval problems** (`insert-interval`, `meeting-rooms`) produce a flat
  integer buffer rather than a list of pair objects.

The baseline kernels return materialized results. That is an interface
distinction, not evidence that one representation is cheaper under all output
conventions.

### Kernel-only, per problem (cl100k)

| Problem | NIL | Python | C++ | NIL vs Python |
|---|---:|---:|---:|---:|
| contains-duplicate | 51 | 14 | 63 | +264% |
| last-stone-weight | 257 | 83 | 87 | +210% |
| meeting-rooms | 105 | 38 | 82 | +176% |
| kth-largest-element-in-an-array | 31 | 13 | 53 | +138% |
| letter-combinations-of-a-phone-number | 161 | 73 | 159 | +121% |
| course-schedule | 350 | 162 | 162 | +116% |
| spiral-matrix | 339 | 161 | 175 | +111% |
| car-fleet | 154 | 75 | 100 | +105% |
| valid-palindrome | 120 | 60 | 110 | +100% |
| search-in-rotated-sorted-array | 255 | 128 | 125 | +99% |
| insert-interval | 225 | 118 | 144 | +91% |
| longest-repeating-character-replacement | 201 | 108 | 129 | +86% |
| balanced-binary-tree | 292 | 164 | 203 | +78% |
| coin-change | 139 | 82 | 103 | +70% |
| maximum-subarray | 73 | 43 | 82 | +70% |
| median-of-two-sorted-arrays | 323 | 219 | 208 | +47% |
| target-sum | 154 | 107 | 130 | +44% |
| 3sum | 257 | 183 | 180 | +40% |
| generate-parentheses | 113 | 82 | 124 | +38% |
| plus-one | 94 | 68 | 82 | +38% |
| validate-binary-search-tree | 130 | 95 | 133 | +37% |
| longest-substring-without-repeating-characters | 86 | 66 | 118 | +30% |
| gas-station | 99 | 82 | 93 | +21% |
| reverse-linked-list | 49 | 43 | 86 | +14% |
| single-number | 25 | 25 | 48 | 0% |
| min-cost-climbing-stairs | 37 | 40 | 71 | −7% |
| best-time-to-buy-and-sell-stock-with-cooldown | 59 | 66 | 101 | −11% |
| valid-sudoku | 112 | 134 | 137 | −16% |
| reverse-integer | 57 | 77 | 78 | −26% |

Minimal-I/O per-problem counts are in `ROUND20_DENSITY.json`.

### Verification of the measurement copies

`density-cuts/build.py` regenerates all 87 files per cut byte-identically
(`diff -ru` against the pre-run snapshot: no output). `density-cuts/verify.py`
ran every kernel-host and minimal-I/O copy against the **unchanged** frozen
oracles: **29 tasks, 1,712 of 1,712 checks passed**, zero errors. Each task is
checked at reference, native O0 and native O2 for both cuts, plus Python and
C++, with byte-exact output, returned length, unchanged input, no stray files
and matching source hashes. No kernel is counted as correct without its full
wrapper passing. Higher-order kernels have no first-order entry point and are
instantiated in their verified host wrappers; non-HOF kernels additionally get a
standalone `nil check`. No frozen task, fixture, golden, Python or C++ reference
was edited.

## The five cliff samples

Largest frozen fixture, 15 rotating repetitions after one warmup, one worker, no
competing job, whole-process wall time including startup, file I/O, parsing,
computation and serialization. Output, returned length and unchanged input are
checked every repetition. Values are **min / median / max ms**.

| Problem | R19 NIL median | R20 NIL | R20 C++ | R19 ratio | R20 ratio | ADR 042 forecast | Bound |
|---|---:|---:|---:|---:|---:|---|---|
| last-stone-weight | 27,940.09 | 1,943.29 / **1,951.81** / 2,040.81 | 11.08 / 11.56 / 12.12 | 2,299.45× | **168.89×** | 15–100 ms, may miss 3× | **miss — forecast missed** |
| balanced-binary-tree | 1,522.33 | 26.69 / **27.09** / 28.34 | 13.13 / 13.64 / 14.58 | 107.70× | **1.99×** | 15–60 ms | pass — forecast hit |
| validate-binary-search-tree | 1,466.07 | 22.97 / **23.21** / 23.45 | 12.49 / 12.62 / 13.87 | 110.00× | **1.84×** | 15–60 ms | pass — forecast hit |
| course-schedule | 7,511.28 | 41.71 / **41.98** / 42.91 | 22.48 / 22.89 / 24.19 | 325.37× | **1.83×** | 15–100 ms | pass — forecast hit |
| spiral-matrix | 1,418.88 | 25.00 / **25.21** / 26.63 | 7.40 / 7.63 / 8.82 | 170.98× | **3.30×** | 15–100 ms | **miss** — forecast hit |

Four of five forecast medians were hit; the heap forecast was missed by 19.5×.
Spiral Matrix landed inside its forecast range yet still exceeds the bound, which
shows the range was set too loosely to imply qualification. Relative standard
deviation on these five is 0.8–1.7%, so the cliff removals are far outside noise.

The three cliff samples that now qualify do so by binding old scalar, node and
field values before functional updates. No algorithm was changed, no instruction
was hand-moved, and no checked operation was skipped. Last Stone Weight and
Spiral Matrix remain CORE-201/CORE-202 work: a binding does not remove a
callee-held or genuinely live alias.

### All 29 admitted samples

| Problem | R19 NIL median | R20 NIL min / median / max | R20 C++ min / median / max | R19 ratio | R20 ratio | Bound |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| contains-duplicate | 10.059 | 9.780 / 9.973 / 12.207 | 6.358 / 6.553 / 8.685 | 1.534× | 1.522× | pass |
| valid-sudoku | 2.586 | 2.218 / 2.578 / 4.041 | 2.272 / 2.515 / 4.248 | 1.042× | 1.025× | pass |
| valid-palindrome | 2.579 | 2.404 / 2.554 / 2.909 | 2.887 / 3.069 / 3.711 | 0.802× | 0.832× | pass |
| 3sum | 842.707 | 835.068 / 837.873 / 847.052 | 102.516 / 105.577 / 232.298 | 7.776× | 7.936× | miss |
| longest-substring-without-repeating-characters | 8.026 | 7.466 / 7.893 / 10.469 | 2.640 / 2.839 / 4.132 | 2.737× | 2.780× | pass |
| longest-repeating-character-replacement | 10.900 | 10.519 / 10.925 / 12.920 | 2.855 / 2.982 / 3.954 | 3.595× | 3.664× | miss |
| generate-parentheses | 26.978 | 26.332 / 26.654 / 28.397 | 3.299 / 3.401 / 3.780 | 7.846× | 7.837× | miss |
| car-fleet | 18.737 | 18.204 / 18.509 / 18.796 | 22.515 / 22.695 / 23.632 | 0.818× | 0.816× | pass |
| search-in-rotated-sorted-array | 8.961 | 8.450 / 8.880 / 11.200 | 5.435 / 5.635 / 7.904 | 1.560× | 1.576× | pass |
| median-of-two-sorted-arrays | 9.625 | 9.185 / 9.515 / 11.526 | 6.021 / 6.231 / 8.183 | 1.545× | 1.527× | pass |
| reverse-linked-list | 32.200 | 31.619 / 31.948 / 34.095 | 10.942 / 11.246 / 12.321 | 2.820× | 2.841× | pass |
| balanced-binary-tree | 1522.334 | 26.694 / 27.088 / 28.340 | 13.127 / 13.640 / 14.576 | 107.701× | 1.986× | pass |
| validate-binary-search-tree | 1466.070 | 22.968 / 23.207 / 23.453 | 12.485 / 12.618 / 13.866 | 110.000× | 1.839× | pass |
| last-stone-weight | 27940.087 | 1943.292 / 1951.809 / 2040.814 | 11.080 / 11.557 / 12.115 | 2299.446× | 168.892× | miss |
| kth-largest-element-in-an-array | 13.575 | 13.370 / 13.586 / 15.498 | 8.368 / 8.664 / 10.914 | 1.586× | 1.568× | pass |
| letter-combinations-of-a-phone-number | 224.357 | 191.011 / 192.335 / 202.266 | 4.504 / 4.924 / 5.578 | 44.620× | 39.059× | miss |
| course-schedule | 7511.278 | 41.710 / 41.977 / 42.912 | 22.480 / 22.893 / 24.187 | 325.374× | 1.834× | pass |
| min-cost-climbing-stairs | 8.632 | 8.416 / 8.635 / 11.282 | 4.674 / 5.004 / 7.291 | 1.769× | 1.726× | pass |
| coin-change | 4.012 | 3.954 / 4.173 / 6.006 | 2.703 / 3.026 / 4.923 | 1.364× | 1.379× | pass |
| best-time-to-buy-and-sell-stock-with-cooldown | 8.852 | 8.683 / 8.898 / 11.029 | 4.688 / 5.049 / 6.775 | 1.837× | 1.762× | pass |
| target-sum | 2.685 | 2.516 / 2.839 / 4.098 | 2.435 / 2.618 / 4.302 | 1.061× | 1.084× | pass |
| maximum-subarray | 9.339 | 9.146 / 9.516 / 12.028 | 5.486 / 5.776 / 8.182 | 1.652× | 1.647× | pass |
| gas-station | 13.576 | 13.427 / 13.598 / 16.436 | 6.151 / 6.384 / 8.545 | 2.143× | 2.130× | pass |
| insert-interval | 44.764 | 44.395 / 44.759 / 54.760 | 17.445 / 17.876 / 19.477 | 2.514× | 2.504× | pass |
| meeting-rooms | 20.107 | 19.924 / 20.150 / 20.519 | 22.885 / 23.130 / 23.653 | 0.872× | 0.871× | pass |
| spiral-matrix | 1418.879 | 25.000 / 25.210 / 26.633 | 7.400 / 7.634 / 8.817 | 170.978× | 3.302× | miss |
| plus-one | 22.966 | 22.624 / 22.938 / 24.419 | 5.393 / 5.586 / 6.359 | 4.152× | 4.106× | miss |
| single-number | 12.724 | 8.898 / 9.076 / 11.272 | 5.622 / 5.865 / 8.113 | 2.206× | 1.547× | pass |
| reverse-integer | 29.754 | 28.758 / 29.098 / 29.414 | 11.948 / 12.146 / 12.762 | 2.386× | 2.396× | pass |

The 24 non-cliff samples move 0–3% in median, except `single-number`, which the
bitwise rewrite took from 12.724 to 9.076 ms (2.206× → 1.547×). The remaining
misses are the C3 serialization/builder group (`3sum`,
`generate-parentheses`, `letter-combinations-of-a-phone-number`, `plus-one`) and
`longest-repeating-character-replacement`, unchanged in character from Round 19.

## Per-source token deltas

Before = the Round 19 sources at benchmarks `6fd268d`; after = now. 13 of 29
sources were rewritten where operators, constants or bindings simplify the actual
algorithm. Net **−187 cl100k and −187 o200k tokens**; the other 16 are untouched.

| Problem | cl100k Δ | o200k Δ | after cl100k / o200k | before |
|---|---:|---:|---:|---:|
| single-number | −80 | −81 | 56 / 56 | 136 / 137 |
| balanced-binary-tree | −56 | −56 | 323 / 324 | 379 / 380 |
| car-fleet | −28 | −28 | 185 / 185 | 213 / 213 |
| median-of-two-sorted-arrays | −12 | −12 | 354 / 354 | 366 / 366 |
| valid-sudoku | −12 | −12 | 143 / 143 | 155 / 155 |
| meeting-rooms | −9 | −9 | 136 / 136 | 145 / 145 |
| plus-one | −6 | −6 | 158 / 159 | 164 / 165 |
| last-stone-weight | −5 | −4 | 288 / 289 | 293 / 293 |
| letter-combinations-of-a-phone-number | −5 | −5 | 177 / 176 | 182 / 181 |
| reverse-integer | −3 | −3 | 121 / 122 | 124 / 125 |
| validate-binary-search-tree | **+8** | **+9** | 161 / 163 | 153 / 154 |
| course-schedule | **+9** | **+8** | 381 / 384 | 372 / 376 |
| spiral-matrix | **+12** | **+12** | 403 / 403 | 391 / 391 |

`single-number` is the only large saving, from `^`/`~` replacing arithmetic
emulation. The three cliff rewrites that now qualify cost tokens. The full-program
aggregate therefore moves from Round 19's −18.9% to −21.7% versus Python, which
the kernel cut above shows is an adapter artefact, not denser algorithms.

## Gates

| Gate | Command | Result |
|---|---|---|
| Debug CI | `./scripts/ci.sh` | exit 0, **511 tests**, 0 failed, 0 Clippy warnings |
| Release CI | `./scripts/ci.sh release` | exit 0, **511 tests**, 0 failed, 0 Clippy warnings |
| Sanitizers | `./scripts/sanitize.sh` | exit 0, **223 tests**, 0 failed, no ASan/UBSan finding |
| Fuzz seed 20260707 | `./scripts/fuzz-v5.sh --seed 20260707 --out <tmp>` | 644 programs, 1,288 native builds, **0 divergences** |
| Fuzz seed 918273645 | same, seed 918273645 | 644 programs, 1,288 native builds, **0 divergences** |
| Fuzz seed 42424242 | same, seed 42424242 | 644 programs, 1,288 native builds, **0 divergences** |
| Application corpus | `corpora/application-v5/verify.py` | 79 tasks, 68 NIL programs, **2,815 checks** (563 + 1,126 + 563 + 563) |
| Original group | same, `--group original` | 25 tasks, **610 checks exactly** (120 + 240 + 125 + 125) |
| NeetCode re-verification | `corpora/neetcode150/verify.py --verified-only` | 29 tasks, **1,070 / 1,070 checks** |
| Density cuts | `density-cuts/verify.py` | 29 tasks, **1,712 / 1,712 checks** |
| Historical controls | `ownership-study/run.py --repeats 25` | 23 arms, no failures, proofs identical to Round 17/18 |

Test counts rose from 466 to 511 debug/release and 199 to 223 sanitizer tests; no
gate was weakened and no check was skipped. All three fuzz seeds produced
identical per-code counts — seeds vary constants, not program structure — with
479 OK and the expected E009/E012–E022 distribution, plus static E001 507,
E002 252, E004 252, E005 421 and E007 1,180. ADR 042 contributes **42 of the 462
call families** (10 binding, 30 operator, 2 wide-loop constant collision) and
8 new source-mutation kinds over 1,352 malformed cases per seed.

### Historical controls, 16 MiB inputs, 25 repetitions

Compared with the Round 18 final table (`ROUND18.md`), which is the correct
baseline because Round 18 already landed the map/transform recovery. Each cell is
min/median/max ms.

| Control | Round 18 final | Round 20 | R20/R18 median |
|---|---:|---:|---:|
| append | 5.343/6.020/7.114 | 4.853/5.860/7.131 | 0.973× |
| filter_hand | 75.533/76.517/80.372 | 76.054/76.625/84.822 | 1.001× |
| filter_std | 79.982/81.979/86.175 | 80.911/81.708/85.432 | 0.997× |
| map_hand | 34.877/35.737/39.450 | 34.692/35.809/37.589 | 1.002× |
| map_std | 35.034/36.187/41.370 | 34.876/35.761/36.371 | 0.988× |
| scan | 8.283/8.673/10.257 | 8.174/8.651/9.059 | 0.997× |
| insertion_hof | 48.562/49.353/52.568 | 48.453/48.887/51.153 | 0.991× |
| insertion_hand | 48.174/49.087/55.297 | 48.079/48.452/51.218 | 0.987× |
| transform | 33.905/35.801/42.247 | 34.816/36.042/38.395 | 1.007× |
| sort_core_1024 | 3.535/3.799/4.760 | 3.094/4.130/5.211 | 1.087× |
| sort_source_1024 | 3.301/3.587/4.291 | 3.447/3.696/5.053 | 1.030× |
| sort_core_65536 | 9.084/9.535/10.701 | 9.454/9.666/10.819 | 1.014× |
| sort_source_65536 | 71.277/73.151/81.111 | 71.996/72.822/91.062 | 0.995× |
| sort_core_1048576 | 127.587/130.733/138.900 | 129.544/130.409/134.762 | 0.998× |
| sort_source_1048576 | 1326.821/1437.751/1539.812 | 1394.765/1466.410/1530.703 | 1.020× |
| cpp_append | 4.914/5.198/7.891 | 4.877/5.177/6.603 | 0.996× |
| cpp_filter | 29.101/29.821/33.901 | 29.561/30.283/32.629 | 1.015× |
| cpp_map | 17.636/18.724/21.638 | 18.039/19.136/25.368 | 1.022× |
| cpp_insertion | 4.652/4.897/5.549 | 4.574/4.933/6.053 | 1.007× |
| cpp_transform | 12.074/13.057/16.622 | 12.209/13.386/16.884 | 1.025× |
| cpp_sort_1024 | 3.501/3.889/4.205 | 2.901/4.244/6.531 | 1.091× |
| cpp_sort_65536 | 8.507/8.677/10.428 | 8.509/8.780/9.861 | 1.012× |
| cpp_sort_1048576 | 94.681/96.120/160.623 | 95.672/96.147/100.548 | 1.000× |

The two largest moves are the 1,024-element sort arms: `sort_core_1024` +8.7% and
`cpp_sort_1024` +9.1%. C++ moved the same amount on the same arm, so this is
machine-level variation on the suite's smallest measurement, not a NIL change.
`sort_source_1048576` is +2.0%, inside its own observed min/max and well inside
the ±5–7% batch spread Round 18 published for that arm. All ownership/borrow
proof counts are byte-identical to Round 17/18 and there were no failures. The
performance targets Round 18 established (map/transform ≤37.9 ms, scan vectorized,
unbounded push at concat parity) all hold.

## What this round does not establish

* Operators and bindings do not fix a poor algorithm or make an update uniquely
  owned. Two cliff samples remain misses.
* Density ranking is cohort- and driver-sensitive. Three defensible cuts on the
  same 29 programs give −21.7%, +0.2% and +66.7% against Python. None of them
  measures failure-inclusive generation or repair tokens.
* The cohort is 29 survivors of 36 attempts out of 150 problems, with locally
  authored solutions and language-specific storage representations. It is not an
  unbiased estimate for NeetCode 150.
* These are whole-process medians on one macOS arm64 machine. Compare ratios
  against the published controls, not absolute milliseconds.
* The default profile remains expr-v0. Core 1.0 still requires all 150 problems,
  the CORE-601 adversarial suite audit and a frozen normative specification.
