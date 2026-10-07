# Core 1.0 preregistered census

## Unfavourable forecast

**52/150 are forecast to miss the 3x native performance bound**, not to be semantically inexpressible. All 150 are forecast expressible using current types, index graphs, flat grids, explicit stacks and arithmetic emulation. None is verified by this census. Unselected problems remain unvalidated, not automatically blocked or passed.

This prediction deliberately distinguishes missing direct primitives from missing expressive power. Integer-keyed hash collections, bit operations and bulk serializers have credible speed risks; absence of `%`, `&&`, `break` or a heap intrinsic alone is not proof of impossibility. Every problem's feature checks and risks are in tasks.json, including quota fit at the declared maximum. Quota predictions require verification of real peak capacity, not payload alone.

## Category forecasts

| Category | Total | Semantically feasible | Expected <=3x | Fixed sample |
| --- | ---: | ---: | ---: | --- |
| Arrays & Hashing | 9 | 9 | 3 | contains-duplicate, valid-sudoku |
| Two Pointers | 5 | 5 | 4 | valid-palindrome, 3sum |
| Sliding Window | 6 | 6 | 5 | longest-substring-without-repeating-characters, longest-repeating-character-replacement |
| Stack | 7 | 7 | 5 | generate-parentheses, car-fleet |
| Binary Search | 7 | 7 | 6 | search-in-rotated-sorted-array, median-of-two-sorted-arrays |
| Linked List | 11 | 11 | 8 | reverse-linked-list, lru-cache |
| Trees | 15 | 15 | 12 | balanced-binary-tree, validate-binary-search-tree |
| Tries | 3 | 3 | 0 | implement-trie-prefix-tree, word-search-ii |
| Heap / Priority Queue | 7 | 7 | 2 | last-stone-weight, kth-largest-element-in-an-array |
| Backtracking | 9 | 9 | 1 | letter-combinations-of-a-phone-number, n-queens |
| Graphs | 13 | 13 | 10 | course-schedule, course-schedule-ii |
| Advanced Graphs | 6 | 6 | 3 | network-delay-time, cheapest-flights-within-k-stops |
| 1-D Dynamic Programming | 12 | 12 | 11 | min-cost-climbing-stairs, coin-change |
| 2-D Dynamic Programming | 11 | 11 | 11 | best-time-to-buy-and-sell-stock-with-cooldown, target-sum |
| Greedy | 8 | 8 | 7 | maximum-subarray, gas-station |
| Intervals | 6 | 6 | 1 | insert-interval, meeting-rooms |
| Math & Geometry | 8 | 8 | 7 | spiral-matrix, plus-one |
| Bit Manipulation | 7 | 7 | 2 | single-number, reverse-integer |

## Fixed protocol

ADR 041 was committed before this census. The 36 names are selected solely by its hash rule; no replacements. Freeze fixture generators, reference oracles and goldens before NIL authoring. Report semantic errors, authoring failures, step/depth/time limits, quota failures and performance misses separately. Output order and ASCII/byte semantics are explicit; no Unicode requirement is smuggled into an algorithm exercise. No unsupported task may disappear.

## Ranked follow-up hypotheses (not approved features)

1. Checked integer-key maps/sets: avoid decimal formatting and temporary keys in hash-heavy tasks; indexing/ownership/quota proofs need extension. Existing byte maps can implement these tasks today.
2. Scalar modulo/bitwise/shift primitives: remove 32-step arithmetic emulation; checked signed edges require parity tests, but no arena changes. Logical/min/max/abs convenience belongs to later density work unless measured speed demands it.
3. General callee/loop ownership proofs for indexed heaps, trie pools and DP: lower repeated checked-update overhead; this changes load-bearing root/alias proofs and must be separately validated.
4. Efficient bulk numeric/text serialization and indexed record sorting: algorithm/library work first; do not add problem-specific operations.
5. Reference execution scaling and explicit stack libraries: inspect real limits before changing the 256-frame policy. Deep input trees need not imply deep runtime recursion.

The final roadmap is conditioned on the selected experiments; it must not turn these forecasts into claimed findings. No compiler changes in this round.
