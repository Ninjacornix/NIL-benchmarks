# Core 1.0 census and stratified qualification — 2026-10-07

**17 of the fixed 36 samples do not qualify today: seven fail the validation budget and ten are correct but exceed the 3× C++ bound. Only 19/150 currently meet both gates; 114 are unattempted. This does not establish that 131 problems are inexpressible.**

The worst measured correct sample is Last Stone Weight: 27,940.09 ms NIL versus 12.15 ms C++ (2,299.45×). Existing types can express a heap, but that is not evidence of usable update performance. Core 1.0 is not complete.

## Provenance, ordering and frozen assets

Only names, categories and identifier links come from the [pinned public metadata](https://github.com/neetcode-gh/leetcode/blob/5a3c1b2d59b4e5c6252006343d73849ebc75f796/.problemSiteData.json). Contracts, fixtures, Python/C++ references and new NIL sources are original MIT work. No upstream statements, examples, tests or solution code were copied. This is an independent byte-file adaptation, not the official judge or an endorsement.

Main `0e0a728` committed ADR 041 first. Benchmark `3439194` committed the 150-task census next; `7987470` froze all 150 original contracts, generators, Python/C++ sources and goldens before any NIL candidate was authored. Main `d64311b` pinned that suite. Two names per category were fixed by SHA256 of `NIL-Core-1.0\0<CATEGORY>\0<SLUG>`; no substitution by ease occurred.

All 150 have Python/C++ references and 1,063 frozen fixtures, including edge, seeded and largest inputs. All 36 selected candidates typechecked; only the 29 passing every reference/native O0/O2 fixture are admitted as `.nil` sources. Failed candidate source hashes and outcomes remain in `STATUS.json`; their code and raw logs remain outside git.

## Census versus observation

The preregistered forecast was 150 semantically feasible, 98 expected to meet the performance bound, 52 expected to miss. It was too optimistic for the sample: 22/36 expected performance passes became 19 measured passes. Four unexpected passes and seven forecast passes not delivered are shown below. The seven validation failures leave operational feasibility unproved under the fixed budget; they do not disprove the semantic forecast or establish a missing type.

| Category | Total | Forecast ≤3× (all) | Sample forecast ≤3× | Byte-correct | Meets bound | Validation blocked | Speed misses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Arrays & Hashing | 9 | 3 | 1 | 2 | 2 | 0 | 0 |
| Two Pointers | 5 | 4 | 1 | 2 | 1 | 0 | 1 |
| Sliding Window | 6 | 5 | 2 | 2 | 1 | 0 | 1 |
| Stack | 7 | 5 | 0 | 2 | 1 | 0 | 1 |
| Binary Search | 7 | 6 | 2 | 2 | 2 | 0 | 0 |
| Linked List | 11 | 8 | 1 | 1 | 1 | 1 | 0 |
| Trees | 15 | 12 | 2 | 2 | 0 | 0 | 2 |
| Tries | 3 | 0 | 0 | 0 | 0 | 2 | 0 |
| Heap / Priority Queue | 7 | 2 | 1 | 2 | 1 | 0 | 1 |
| Backtracking | 9 | 1 | 0 | 1 | 0 | 1 | 1 |
| Graphs | 13 | 10 | 1 | 1 | 0 | 1 | 1 |
| Advanced Graphs | 6 | 3 | 1 | 0 | 0 | 2 | 0 |
| 1-D Dynamic Programming | 12 | 11 | 2 | 2 | 2 | 0 | 0 |
| 2-D Dynamic Programming | 11 | 11 | 2 | 2 | 2 | 0 | 0 |
| Greedy | 8 | 7 | 2 | 2 | 2 | 0 | 0 |
| Intervals | 6 | 1 | 1 | 2 | 2 | 0 | 0 |
| Math & Geometry | 8 | 7 | 2 | 2 | 0 | 0 | 2 |
| Bit Manipulation | 7 | 2 | 1 | 2 | 2 | 0 | 0 |

| Fixed sample | Forecast ≤3× | Actual |
| --- | --- | --- |
| contains-duplicate | no | meets-bound |
| valid-sudoku | yes | meets-bound |
| valid-palindrome | yes | meets-bound |
| 3sum | no | performance-miss |
| longest-substring-without-repeating-characters | yes | meets-bound |
| longest-repeating-character-replacement | yes | performance-miss |
| generate-parentheses | no | performance-miss |
| car-fleet | no | meets-bound |
| search-in-rotated-sorted-array | yes | meets-bound |
| median-of-two-sorted-arrays | yes | meets-bound |
| reverse-linked-list | yes | meets-bound |
| lru-cache | no | validation blocked |
| balanced-binary-tree | yes | performance-miss |
| validate-binary-search-tree | yes | performance-miss |
| implement-trie-prefix-tree | no | validation blocked |
| word-search-ii | no | validation blocked |
| last-stone-weight | no | performance-miss |
| kth-largest-element-in-an-array | yes | meets-bound |
| letter-combinations-of-a-phone-number | no | performance-miss |
| n-queens | no | validation blocked |
| course-schedule | yes | performance-miss |
| course-schedule-ii | no | validation blocked |
| network-delay-time | no | validation blocked |
| cheapest-flights-within-k-stops | yes | validation blocked |
| min-cost-climbing-stairs | yes | meets-bound |
| coin-change | yes | meets-bound |
| best-time-to-buy-and-sell-stock-with-cooldown | yes | meets-bound |
| target-sum | yes | meets-bound |
| maximum-subarray | yes | meets-bound |
| gas-station | yes | meets-bound |
| insert-interval | yes | meets-bound |
| meeting-rooms | no | meets-bound |
| spiral-matrix | yes | performance-miss |
| plus-one | yes | performance-miss |
| single-number | no | meets-bound |
| reverse-integer | yes | meets-bound |

## Failures and core-gap interpretation

| Candidate | Failed largest-fixture paths | Finding |
| --- | --- | --- |
| implement-trie-prefix-tree | O0: 120 s deadline; reference: 120 s deadline | Allocates byte-map entries for prefixes; inspect indexed trie pool and evaluator overhead. Native O2 succeeds; O0/reference exceed deadline. |
| course-schedule-ii | O0: E008 step budget; O2: E008 step budget; reference: 120 s deadline | Scans all vertices for each lexicographically smallest ready vertex; replace candidate with a min heap. No core impossibility established. |
| network-delay-time | O0: E008 step budget; O2: E008 step budget; reference: 120 s deadline | Dense vertex selection and repeated edge scans instead of C++ heap Dijkstra; algorithm class differs. No core impossibility established. |
| cheapest-flights-within-k-stops | reference: 120 s deadline | Layered Bellman–Ford with snapshot buffers; both native paths succeed, reference exceeds deadline. Inspect evaluator/update cost. |
| n-queens | reference: 120 s deadline | Explicit column/diagonal flag arrays; both native paths succeed, reference exceeds deadline. No need for a depth-limit change demonstrated. |
| lru-cache | O0: E008 step budget; O2: E008 step budget; reference: 120 s deadline | Timestamp map with full-entry scans is O(operations × keys); replace candidate with indexed doubly linked list + lookup. No core impossibility established. |
| word-search-ii | reference: 120 s deadline | Per-word DFS rather than shared trie traversal; algorithm class differs. Both native paths succeed but reference exceeds deadline. |

Failed campaigns used parallel verification workers, so deadlines are operational failures of those runs, not isolated latency measurements or proofs of missing expressive power. They are not counted as passing; retrying with improved candidates or stronger isolation requires a new recorded run. The improved N-Queens candidate passes both native paths; an earlier slower candidate exhausted E008 and was superseded. No O0/O2 output disagreement or compiler defect was found in admitted programs.

The census flags direct operators as risks, not necessities: six modulo, six bitwise, four shift, nine integer-keyed lookup, 32 grid/nested storage, nine heap and eleven deep-stack concerns. Those counts come from coarse preregistration tags, not a proof that other tasks never use the operation: notably only two carried the ASCII-helper risk tag, although many need ordinary byte parsing/string operations. The separate [feature audit](../../corpora/neetcode150/FEATURE_AUDIT.json) records 34 algorithmic byte/text tasks and all 150 feature checks without rewriting the forecasts. All 150 require input parsing and/or serialization. The detailed contracts and sources supersede any interpretation of the tags as exhaustive algorithm requirements.

No sampled task establishes a need for new types, recursion-limit relaxation, `%`, logical operators, min/max/abs or math intrinsics. Single Number uses arithmetic XOR emulation and meets the bound; deep trees use explicit stacks. Byte-key maps and index pools are available. Remaining 114 need implementation before absence of a convenient spelling can be called a core blocker.

Inspection suggests read-after-update aliases and conservative callee-loop ownership inhibit reuse in the trees, grid and heap sources. Generated IR has guarded `nil_set_unique` calls, which can still copy; counting them is not allocation profiling. The very large ratios are measured; the exact allocation attribution is not. Candidate source scheduling and algorithm choice must be controlled before redesigning core proofs.

## Performance: every admitted solution

Apple Clang 21.0.0, macOS arm64; C++ `-std=c++17 -O2 -ffp-contract=off`, NIL native O2 through the same Clang. Largest frozen fixture; 15 rotating repetitions after one warmup; one worker and no other validation job during the accepted timing pass. Complete process time includes file I/O, parsing, computation and serialization. Output, returned byte count and unchanged input are checked on each repetition. Timing uses existing unbounded instrumentation; correctness uses 1 billion steps, depth 256 and 120 s, retaining 64 MiB capacity and all memory checks.

Values are milliseconds as **min / median / max**. Variance, source hashes and raw receipt hashes are in `CORE_1_0_EVIDENCE.json`. Correct sources use the same broad algorithm class as C++; failed LRU, Course II, Word Search II and Dijkstra candidates do not, and receive no parity claim. Startup dominates small cases, so these are end-to-end qualification numbers, not kernel speed ratios. A marginal pass requires another campaign before release qualification.

| Problem | NIL ms | C++ ms | Median ratio | Bound |
| --- | ---: | ---: | ---: | --- |
| contains-duplicate | 9.583 / 10.059 / 11.781 | 6.412 / 6.555 / 8.528 | 1.534× | pass |
| valid-sudoku | 2.343 / 2.586 / 3.172 | 2.368 / 2.481 / 3.210 | 1.042× | pass |
| valid-palindrome | 2.295 / 2.579 / 3.517 | 2.970 / 3.217 / 4.623 | 0.802× | pass |
| 3sum | 840.264 / 842.707 / 864.408 | 101.584 / 108.372 / 113.939 | 7.776× | miss |
| longest-substring-without-repeating-characters | 7.775 / 8.026 / 10.351 | 2.862 / 2.932 / 3.964 | 2.737× | pass |
| longest-repeating-character-replacement | 10.641 / 10.900 / 12.866 | 2.865 / 3.032 / 3.678 | 3.595× | miss |
| generate-parentheses | 26.528 / 26.978 / 27.936 | 3.201 / 3.438 / 3.736 | 7.846× | miss |
| car-fleet | 18.112 / 18.737 / 19.091 | 22.418 / 22.919 / 23.495 | 0.818× | pass |
| search-in-rotated-sorted-array | 8.691 / 8.961 / 10.631 | 5.473 / 5.745 / 7.319 | 1.560× | pass |
| median-of-two-sorted-arrays | 9.251 / 9.625 / 11.705 | 6.006 / 6.229 / 8.274 | 1.545× | pass |
| reverse-linked-list | 31.698 / 32.200 / 32.674 | 11.131 / 11.417 / 12.104 | 2.820× | pass |
| balanced-binary-tree | 1518.420 / 1522.334 / 1533.403 | 13.377 / 14.135 / 14.949 | 107.701× | miss |
| validate-binary-search-tree | 1458.154 / 1466.070 / 1516.279 | 12.866 / 13.328 / 16.136 | 110.000× | miss |
| last-stone-weight | 26285.378 / 27940.087 / 56188.684 | 10.790 / 12.151 / 19.511 | 2299.446× | miss |
| kth-largest-element-in-an-array | 13.413 / 13.575 / 15.195 | 8.312 / 8.560 / 10.610 | 1.586× | pass |
| letter-combinations-of-a-phone-number | 222.853 / 224.357 / 233.252 | 4.596 / 5.028 / 5.227 | 44.620× | miss |
| course-schedule | 7419.930 / 7511.278 / 7595.409 | 22.458 / 23.085 / 24.343 | 325.374× | miss |
| min-cost-climbing-stairs | 8.387 / 8.632 / 10.446 | 4.632 / 4.881 / 6.136 | 1.769× | pass |
| coin-change | 3.804 / 4.012 / 5.706 | 2.729 / 2.942 / 4.742 | 1.364× | pass |
| best-time-to-buy-and-sell-stock-with-cooldown | 8.659 / 8.852 / 10.552 | 4.670 / 4.819 / 6.166 | 1.837× | pass |
| target-sum | 2.309 / 2.685 / 3.827 | 2.273 / 2.530 / 3.869 | 1.061× | pass |
| maximum-subarray | 8.915 / 9.339 / 11.392 | 5.460 / 5.653 / 7.805 | 1.652× | pass |
| gas-station | 13.126 / 13.576 / 15.590 | 6.093 / 6.335 / 7.940 | 2.143× | pass |
| insert-interval | 44.240 / 44.764 / 59.207 | 17.267 / 17.803 / 18.572 | 2.514× | pass |
| meeting-rooms | 19.812 / 20.107 / 20.900 | 22.822 / 23.047 / 23.784 | 0.872× | pass |
| spiral-matrix | 1409.267 / 1418.879 / 1438.101 | 7.609 / 8.299 / 8.627 | 170.978× | miss |
| plus-one | 22.666 / 22.966 / 24.508 | 5.294 / 5.532 / 6.366 | 4.152× | miss |
| single-number | 12.344 / 12.724 / 14.644 | 5.561 / 5.767 / 7.213 | 2.206× | pass |
| reverse-integer | 29.147 / 29.754 / 31.364 | 11.998 / 12.470 / 13.388 | 2.386× | pass |

## Source tokens: verified survivors only

**Source density is not total model tokens to a correct program.** The prior generation result (NIL 0/24 versus Python 11/24) is unchanged. No model inference, failed-generation accounting or repair study was run here. Seven failed candidates and 114 unattempted problems are excluded from the paired aggregate; this is survivorship-biased, not a representative estimate for NeetCode 150.

Complete standalone sources include file adapters/helpers in all languages. Python/C++ drivers are readable reference implementations, not golfed; C++ retains a common numeric reader even for some text-only contracts. All counted sources are ASCII, so bytes equal characters. Real tiktoken 0.12.0, cl100k_base and o200k_base; vocabulary/rank hashes and all 150 baseline counts are in `CORE_1_0_DENSITY.json`.

| Language (29 programs) | Bytes | Characters | cl100k | o200k |
| --- | ---: | ---: | ---: | ---: |
| nil | 10390 | 10390 | 5508 | 5534 |
| python | 25474 | 25474 | 6795 | 6818 |
| cpp | 35044 | 35044 | 10610 | 10716 |

NIL versus python: cl100k_base: -18.94%, o200k_base: -18.83%.

NIL versus cpp: cl100k_base: -48.09%, o200k_base: -48.36%.

NIL still costs more than Python on seven of these 29 tasks with cl100k and eight
with o200k: balanced tree, heap, phone combinations, character replacement,
median, spiral traversal and palindrome, plus rotated search on o200k. The paired
aggregate does not hide these losses; the table below includes each one.

Each cell below is **bytes (=characters); cl100k / o200k tokens**. Full counts for baseline-only tasks remain available without treating missing NIL as zero.

| Problem | NIL | Python | C++ |
| --- | ---: | ---: | ---: |
| 3sum | 536; 277 / 276 | 1116; 319 / 323 | 1483; 490 / 499 |
| balanced-binary-tree | 641; 379 / 380 | 1304; 356 / 360 | 1445; 441 / 445 |
| best-time-to-buy-and-sell-stock-with-cooldown | 189; 90 / 94 | 911; 237 / 239 | 1168; 351 / 353 |
| car-fleet | 403; 213 / 213 | 958; 244 / 245 | 1220; 367 / 372 |
| coin-change | 304; 170 / 170 | 897; 241 / 241 | 1174; 355 / 357 |
| contains-duplicate | 188; 82 / 82 | 748; 182 / 182 | 1100; 313 / 316 |
| course-schedule | 801; 372 / 376 | 1407; 374 / 378 | 1275; 384 / 387 |
| gas-station | 225; 130 / 130 | 907; 240 / 240 | 1156; 345 / 349 |
| generate-parentheses | 231; 109 / 110 | 500; 136 / 135 | 1067; 314 / 316 |
| insert-interval | 426; 243 / 244 | 1033; 274 / 274 | 1524; 474 / 478 |
| kth-largest-element-in-an-array | 136; 62 / 62 | 780; 197 / 196 | 1066; 305 / 307 |
| last-stone-weight | 508; 293 / 293 | 917; 243 / 246 | 1150; 337 / 339 |
| letter-combinations-of-a-phone-number | 337; 182 / 181 | 471; 138 / 137 | 1203; 346 / 349 |
| longest-repeating-character-replacement | 628; 263 / 264 | 671; 183 / 184 | 1211; 361 / 368 |
| longest-substring-without-repeating-characters | 201; 110 / 109 | 565; 141 / 143 | 1135; 333 / 337 |
| maximum-subarray | 196; 104 / 104 | 813; 207 / 207 | 1145; 331 / 335 |
| median-of-two-sorted-arrays | 628; 366 / 366 | 1210; 357 / 358 | 1406; 457 / 459 |
| meeting-rooms | 285; 145 / 145 | 770; 200 / 200 | 1174; 347 / 351 |
| min-cost-climbing-stairs | 133; 68 / 70 | 791; 209 / 207 | 1087; 321 / 323 |
| plus-one | 321; 164 / 165 | 766; 210 / 210 | 1176; 364 / 368 |
| reverse-integer | 256; 124 / 125 | 902; 221 / 221 | 1164; 360 / 364 |
| reverse-linked-list | 226; 112 / 113 | 809; 212 / 215 | 1221; 368 / 372 |
| search-in-rotated-sorted-array | 478; 286 / 288 | 1043; 286 / 286 | 1215; 378 / 382 |
| single-number | 246; 136 / 137 | 760; 187 / 187 | 1019; 294 / 296 |
| spiral-matrix | 675; 391 / 391 | 1095; 301 / 304 | 1388; 444 / 449 |
| target-sum | 330; 185 / 185 | 989; 260 / 260 | 1236; 381 / 385 |
| valid-palindrome | 280; 144 / 152 | 472; 136 / 136 | 1080; 323 / 328 |
| valid-sudoku | 299; 155 / 155 | 688; 213 / 213 | 1124; 355 / 358 |
| validate-binary-search-tree | 283; 153 / 154 | 1181; 291 / 291 | 1232; 371 / 374 |

## Reproduction and gate receipts

Run from the compiler checkout with the benchmarks submodule initialized. Raw outputs must be outside the checkout. The accepted timing command is deliberately serial. `--verified-only` excludes failed candidates without changing the frozen 36-sample selection. Running the default sample command reports seven `not-authored` failures; it must not silently pass the entire sample.

```sh
python3 benchmarks/corpora/neetcode150/verify.py --baselines-only --all --jobs 4 --output /tmp/core-baselines.json
# TOTALS {"tasks":150,"verified_nil":0,"checks":2126,"passed_checks":2126}
python3 benchmarks/corpora/neetcode150/verify.py --verified-only --jobs 1 --timing-repeats 15 --output /tmp/core-performance.json
# TOTALS {"tasks":29,"verified_nil":29,"checks":1070,"passed_checks":1070}
benchmarks/paired/.venv/bin/python benchmarks/corpora/neetcode150/density.py --verification /tmp/core-performance.json --output /tmp/core-density.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s benchmarks/corpora/neetcode150 -p "test_*.py"
# Ran 12 tests; OK
./scripts/ci.sh
./scripts/ci.sh release
# Each: 466 passed; zero failures, zero Clippy warnings
python3 benchmarks/corpora/application-v5/verify.py --output /tmp/application-all.json
# 79 tasks, 68 NIL programs: 563 reference + 1126 native + 563 Python + 563 C++ = 2815
python3 benchmarks/corpora/application-v5/verify.py --group original --output /tmp/application-original.json
# 25 tasks, 24 NIL programs: 120 reference + 240 native + 125 Python + 125 C++ = 610
git diff --stat 31cb922..HEAD -- crates/ cli/ tools/ std/
# empty
git -C benchmarks diff --stat 5330853..HEAD -- corpora/application-v5/
# empty
```

CI and existing corpus receipts are recorded from this round, not copied from earlier rounds. Raw JSON/logs are outside git at `/tmp/nil-round19/`; committed summaries contain SHA256 receipts rather than transient executable paths. The only Rust addition is the benchmark-only `helpers/core_check.rs`, outside the workspace. It chooses evaluator limits and an in-memory Host; it does not change the compiler. No new dependencies, intrinsics or source profiles. No sanitizer/fuzz claim is made for this compiler-untouched round.

## Limits and next work

Qualification is pending on 131 tasks, comprising seven validation failures, ten timing failures and 114 unattempted programs. Preserve this denominator. Most candidate gaps are algorithm selection, serialization and ownership/reuse scheduling; implement no new core type solely from this sample. See the compiler repository’s `docs/CORE_1_0_ROADMAP.md` for ordered work with problem lists and proof hazards.

These fixtures exercise realistic declared maximum sizes, not every adversarial shape at every maximum. For example, the largest Contains Duplicate input can exit its hash loop early, while largest trees include a chain. Generic size envelopes in some contracts still need multidimensional audit (edge density, aggregate word bytes, maximum output); the suite must be versioned and preregistered before expanding that coverage, never silently altered to rescue a result. Passing this first fixture version is necessary, not evidence of formal correctness or official-judge equivalence.

All work is committed locally on `feat/core-1-0` / benchmark `exp/core-1-0`. Nothing is pushed. Core 1.0 and the default-profile switch remain unapproved and incomplete.
