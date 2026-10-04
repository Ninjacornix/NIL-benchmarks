# Expr-v5 structured collections: capability, density and scaling

**Capability expands, but source density worsens on the harder cohort.** External
NIL references cost **21.9–31.3% more tokens than Python**, combined **15.6–23.7%
more**. The four new algorithms alone cost **66.6–67.6% more** and lose to C++
on three vocabularies. Every old source/count is unchanged. This is cohort movement,
not a fixed-task saving or an irreducible language lower bound.

**There are material performance limits:** nested builders are quadratic even with
a shared child; ordinary byte append
initially regressed **59%**, now restored by validated runtime specialization. Single-use scalar-record growth and scalar/nested replacement scale
linearly in the measured range. Correctness and immutable aliases were preserved;
no root/byte/bounds/quota check was removed to conceal these costs.

Density is NOT tokens until correctness. The historical generation result remains
NIL 0/24 versus Python 11/24 including failed attempts and repairs. No inference
or training occurred. References, prompts and task domains differ from complete
standard-library APIs; neither this study nor 66 seeds establish adaptation readiness.

[Command receipts](V5_COLLECTION_RECEIPTS.txt), [all token counts](V5_COLLECTION_TOKENS.csv),
[verification](V5_COLLECTION_VERIFICATION.json), [fuzz families/codes](V5_COLLECTION_FUZZ.json)
and [native scaling](V5_COLLECTION_SCALING.json) provide the underlying output.

## Decision and implemented boundary

Main ADR 030 commits 6eb11b6 and 2b67d31 precede implementation. Add nominal
`v[Record]`, typed `!buffer[Record](length,fill)` and generalized existing storage
operations. The DAG refers only to earlier record definitions; integer links
represent lists/trees/graphs without recursive types or pointer exposure.
Records may contain earlier record buffers, ordinary sequences and maps.
Sequence-bearing record map values, generic buffer-valued maps and nested map
values remain deferred: packed keyed values need a separate managed-layout contract.
Record sorting is deferred (E018 for valid modes, E012 for invalid modes); intervals
use insertion sort, not invented record ordering. No new library algorithms entered HIR.

Intrinsic variants **32 → 32**, executable core implementations 31 plus the existing
equality compatibility adapter. One typed storage-constructor HIR opcode is added.
Constructor, checked access, functional replacement, concat/slice and snapshot each
participate in type/lifetime/quota/reuse proofs and pass ADR 026's core criterion.
Algorithm/comparator/serializer conveniences were rejected as library surface.
Plugin manifests optionally declare `types record-buffer`; old-type bundles remain
compatible, while using the new type without capability fails E024.

Packed slots are 8 bytes (u128 two). The unchanged 40-byte header plus one metadata
row makes charge **40+(capacity+1)*W**, W=8*max(1, logical slots), with children charged once per identity.
Existing arena root counters include transitive child-edge multiplicity; collection
remains at allocation boundaries. This is count-based liveness bookkeeping, not a
new ownership API, free-on-drop collector, RC library or cycle collector. Acyclic
validated type depth (≤32) bounds traversal; cached layouts (≤4096 slots) are checked.
Static last-use plus actual root uniqueness guard mutation; replacement retains
new children before dropping old ones. Transfer gaps contain no allocation/collection.
Extracted/parent-held child aliases prevent false uniqueness. All old types keep
their charges and semantics; 64 MiB, earlier profiles and the expr-v0 default are unchanged.

## Corpus and provenance

79 tasks, **66 verified NIL programs/JSONL positives**, 13 unsupported (12 external).
The four new task intents derive from pinned MIT TheAlgorithms/Python revision
ef2ecc4d34d17ce6249ba5d3f3c17822dfd7bd50; each manifest records source SHA,
licence, rationale and adaptations. Task wording/protocols/fixtures/references are
original MIT contributions. The cohort/oracles were committed (5e2ae6c) before
reference authoring/counting. No upstream solution was copied. These are newly
supported native typed representations, not algorithms that were uncomputable with
flat encodings before this change. No frozen old task, oracle, golden or existing
baseline source was modified; 185 old verified source hashes/token tables match exactly.

| New reference | Capability | cl100k NIL / Python / C++ |
|---|---|---:|
| Indexed linked-list traversal | Record nodes, checked next indices | 161 / 122 / 179 |
| BST insert + in-order | Functional node updates, integer children | 281 / 209 / 312 |
| Graph BFS | Nested adjacency, visited/queue state | 307 / 166 / 268 |
| Interval merge | Record intervals, insertion sort, snapshot each | 315 / 138 / 252 |
| Frozen external BST | Indexed string nodes, nested JSON output | 411 / 144 / 304 |

The four algorithm programs pass 25 frozen cases per execution path in aggregate;
independent random valid-domain tests add 30 cases per task (seed 30030): 120
reference, 240 native and 120 each Python/C++ checks. BST oracle uses sorted
multisets; interval oracle uses endpoint sweep. Graphs include logical cycles and
repeated edges, while linked-list inputs have acyclic reachable paths. Supplemental
random sizes are ≤32; no arbitrary-depth recursion guarantee is inferred.

The frozen external BST passes its five unchanged fixtures on all paths. Its string
JSON adapter covers canonical unescaped fixture strings, not complete JSON/Unicode.
Four type-layout probes (12 reference/native checks) demonstrate candidate storage
for graph attributes, deck-state histories, word/instruction dictionaries and search
frames. These are NOT complete Dot DSL/Camicia/Forth/Alphametics references and are
excluded from density/JSONL. Their verified parsers/interpreters/simulators/search
adapters remain undelivered; providing storage is not solving the task.

BFS deliberately uses Edge wrapper records to exercise two levels of record buffers;
i64-neighbor rows could be more compact. References were not rewritten after token
counts. NIL also manually formats JSON; interval sorting is O(n²), and recursive
BST updates may copy across conservative allocating calls. Baselines are readable
Python/C++ with actual algorithmic structures, not golfed sources. Shared baseline
file drivers are uncounted; standalone NIL includes file entry wrappers, as in the
unchanged protocol. These choices limit any optimal-density claim.

## Density: four pinned vocabularies

No special tokens. Gemma/Qwen GGUF vocab-only via llama-cpp-python 0.3.16; cl100k
and o200k via tiktoken 0.12.0. Official Qwen tokenizer 0.22.1 cross-checks all 200
verified language sources with zero count mismatches. Exact asset/revision/hash
metadata, every task, bytes and characters are in V5_COLLECTION_DENSITY.json and
V5_COLLECTION_TOKENS.csv. Unsupported NIL rows remain present and unpaired.

| Cut | Pairs / unsupported | Tokenizer | NIL | Python | C++ | NIL vs Python | NIL vs C++ |
|---|---:|---|---:|---:|---:|---:|---:|
| original | 24 / 1 | gemma3_4b | 2144 | 2227 | 5454 | -3.73% | -60.69% |
| original | 24 / 1 | qwen2.5_7b_instruct | 1634 | 1728 | 4235 | -5.44% | -61.42% |
| original | 24 / 1 | cl100k_base | 1582 | 1705 | 4217 | -7.21% | -62.49% |
| original | 24 / 1 | o200k_base | 1571 | 1712 | 4238 | -8.24% | -62.93% |
| new_external | 42 / 12 | gemma3_4b | 10557 | 8041 | 16720 | +31.29% | -36.86% |
| new_external | 42 / 12 | qwen2.5_7b_instruct | 8153 | 6564 | 13326 | +24.21% | -38.82% |
| new_external | 42 / 12 | cl100k_base | 7946 | 6483 | 13280 | +22.57% | -40.17% |
| new_external | 42 / 12 | o200k_base | 7935 | 6508 | 13347 | +21.93% | -40.55% |
| combined | 66 / 13 | gemma3_4b | 12701 | 10268 | 22174 | +23.69% | -42.72% |
| combined | 66 / 13 | qwen2.5_7b_instruct | 9787 | 8292 | 17561 | +18.03% | -44.27% |
| combined | 66 / 13 | cl100k_base | 9528 | 8188 | 17497 | +16.37% | -45.54% |
| combined | 66 / 13 | o200k_base | 9506 | 8220 | 17585 | +15.64% | -45.94% |
| preexisting_external | 38 / 12 | gemma3_4b | 9251 | 7257 | 15401 | +27.48% | -39.93% |
| preexisting_external | 38 / 12 | qwen2.5_7b_instruct | 7089 | 5929 | 12315 | +19.56% | -42.44% |
| preexisting_external | 38 / 12 | cl100k_base | 6882 | 5848 | 12269 | +17.68% | -43.91% |
| preexisting_external | 38 / 12 | o200k_base | 6874 | 5871 | 12317 | +17.08% | -44.19% |
| algorithm_new | 4 / 0 | gemma3_4b | 1306 | 784 | 1319 | +66.58% | -0.99% |
| algorithm_new | 4 / 0 | qwen2.5_7b_instruct | 1064 | 635 | 1011 | +67.56% | +5.24% |
| algorithm_new | 4 / 0 | cl100k_base | 1064 | 635 | 1011 | +67.56% | +5.24% |
| algorithm_new | 4 / 0 | o200k_base | 1061 | 637 | 1030 | +66.56% | +3.01% |

`new_external` means all 54 external tasks (42 paired), including the four new
algorithms. `preexisting_external` is the original 50 external tasks, now 38 paired
with BST added. `algorithm_new` isolates the new four. On the unchanged previously
paired 37 external tasks, counts still reproduce the prior +12.9–23.3% Python gap;
the extra 411 cl100k BST tokens plus 1,064 new algorithm tokens cause the movement.

The net external NIL-minus-Python surplus is attributable exactly by cohort:

| Tokenizer | Unchanged old 37 | Newly supported old BST | Four new algorithms | Current external 42 |
|---|---:|---:|---:|---:|
| Gemma | 1651 | 343 | 522 | 2516 |
| Qwen | 888 | 272 | 429 | 1589 |
| cl100k | 767 | 267 | 429 | 1463 |
| o200k | 738 | 265 | 424 | 1427 |

Columns sum exactly. No old paired solution grew; widening reflects added hard
solutions, not compiler fixes or edits to the old corpus. This does not establish
that these particular reference algorithms are optimally compact.

| Cut | NIL bytes / chars | Python bytes / chars | C++ bytes / chars |
|---|---:|---:|---:|
| original | 3310 / 3310 | 6746 / 6746 | 17283 / 17283 |
| new_external | 16822 / 16822 | 25088 / 25088 | 52943 / 52943 |
| combined | 20132 / 20132 | 31834 / 31834 | 70226 / 70226 |
| preexisting_external | 14327 / 14327 | 22593 / 22593 | 48923 / 48923 |
| algorithm_new | 2495 / 2495 | 2495 / 2495 | 4020 / 4020 |

These are nonrandom, same-author, adapted/partial-API references, not an unbiased
estimate of every algorithm or best possible spelling. 66 examples are reusable
seed positives, not a credible fine-tuning set; hundreds/thousands of independently
varied full-contract examples plus held-out families/repairs would be a starting
experiment, with no guaranteed sample threshold. JSONL retains provenance/licence,
source/verification hashes and frozen prompts; unsupported tasks are not positives.

## Remaining unsupported tasks

| Task | Current blocker |
|---|---|
| env_lookup | Environment capability |
| ex_accumulate | Higher-order callback contract |
| ex_alphametics | Verified search/carry/JSON adapter; assignment storage exists |
| ex_anagram | Unicode case/normalization semantics |
| ex_bank_account | Synchronized shared-state/concurrency contract |
| ex_bob | Unicode classification |
| ex_camicia | Verified cycle simulation/JSON adapter; typed state storage exists |
| ex_diffie_hellman | Entropy contract/adapter |
| ex_dot_dsl | Verified DSL/serialization adapter; generic keyed nesting deferred, wrappers feasible |
| ex_forth | Verified interpreter/definitions/parser adapter; typed word storage exists |
| ex_gigasecond | Calendar/date adapter |
| ex_grep | Multi-file fixture/adapter |
| ex_hangman | Reactive contract/adapter |

Historical missing-capability labels in frozen manifests are not rewritten;
SUPPORT.json and GENERALITY_GAPS.json describe current status. No theoretical
unexpressibility claim is made for the unimplemented adapters.

## Native structure scaling

Apple M2 arm64, macOS 27.0, Apple Clang 21, Rust 1.98.1. O2/LTO, whole-process
wall time, one discarded warmup, medians of 25, verified all-row checksum, no CPU
isolation. Compilation is excluded. Each workload is measured sequentially without
CI/fuzz/sanitizers running. These are native primitive measurements, not reference
evaluator timings or a cross-language algorithm speed claim. Raw samples/source
hashes are committed; startup dominates small cases.

| Shape | Elements | Before ms | Final ms |
|---|---:|---:|---:|
| build | 1000 | 2.310 | 2.651 |
| build | 4000 | 2.488 | 2.486 |
| build | 16000 | 3.180 | 3.216 |
| build | 64000 | 5.926 | 5.666 |
| build | 256000 | 16.018 | 15.748 |
| build | 1048576 | 56.877 | 56.659 |
| update | 1000 | 2.353 | 2.478 |
| update | 4000 | 2.250 | 2.257 |
| update | 16000 | 2.351 | 2.377 |
| update | 64000 | 2.860 | 3.124 |
| update | 256000 | 4.743 | 4.903 |
| update | 1048576 | 13.015 | 12.880 |
| nested-build | 1000 | 8.203 | 8.312 |
| nested-build | 4000 | 107.513 | 107.222 |
| nested-build | 16000 | 1635.808 | 1663.409 |
| nested-build-shared | 1000 | 6.550 | 6.329 |
| nested-build-shared | 4000 | 65.664 | 65.535 |
| nested-build-shared | 16000 | 1008.405 | 1008.033 |
| nested-update | 1000 | 2.616 | 2.540 |
| nested-update | 4000 | 2.461 | 2.353 |
| nested-update | 16000 | 2.761 | 2.839 |
| nested-update | 64000 | 4.632 | 4.706 |
| nested-update | 256000 | 12.615 | 12.473 |
| nested-update | 1048576 | 44.446 | 44.356 |
| alias-build | 1000 | 2.725 | 2.694 |
| alias-build | 4000 | 4.520 | 4.678 |
| alias-build | 16000 | 49.157 | 53.996 |

Scalar build/update are consistent with linear growth after startup. Nested
nonallocating replacement remains linear through 1 Mi rows (44.36 ms), reusing
children and outer storage. Nested fresh-child build is quadratic (8.31 → 107.22
→ 1,663.41 ms); shared-child build is also quadratic (6.33 → 65.54 → 1,008.03).
The shared control removes growing child-allocation count, exposing conservative
transitive root transfers; fresh-child allocation additionally makes arena collection
walk an increasing live allocation list. Outer concat reuse still happens: this
is root/arena bookkeeping, not permission to mutate an alias. A proposed oversized
64k/256k shared control was stopped after the quadratic lower-size evidence; final
three sizes each have 25 samples. No large-size timings were fabricated/extrapolated.
Aliased scalar build copies and is quadratic. Record-field append remains
conservative/superlinear (see controls below); no field-sensitive proof changed.

Standalone scalar Pair(i,i), W=16: constructor **4,194,300** records; replacement
workload **2,097,148**; append **2,097,146**. Each next value traps E013. With one
shared 41-byte child, constructor max is **4,194,297**, replacement **2,097,147**,
again next value E013. These are workload-specific peaks, not universal application
limits: files, other roots, child identities and geometric capacity affect admission.
The conservative copy/growth reservation remains even on unique reuse, so quota
semantics do not depend on optimization success. No 64 MiB increase.

## Existing performance controls and continuation

All final timings use compiler 27a8c9c, O2/LTO, 25 repeats after one warmup,
whole-process wall time, warm cached files and verified output. NIL/C++/Python
order rotates; runtime A/B order alternates. Runs were sequential after all
functional jobs ended, with no CPU isolation. Startup dominates small cases.
Before columns are the initial collections measurements; six-round historical
byte append was 23.91–24.69 ms, scan about 7.58–7.98 ms, transform 34.77–41.24 ms.
The overseer reproduced pre-fix byte append 38.81 ms and transform 44.53 ms.

**Ordinary byte append is restored, not accepted as a permanent 59% tax.**
The root selector scans all validated signatures, nested regions, callees and
plugin providers, recursively following reachable record fields. With no record
buffers, transitive child roots and tagged-record quota sizing compile out.
A record-buffer allocation is the only source of tagged sequence storage; the
closed-world validated NIL-provider boundary cannot manufacture one invisibly.
All record-buffer programs keep the original child-aware path and all quota,
alias, trap/effect checks. Unused type declarations do not activate it. Mixed
programs that actually use record buffers remain conservative; this is not a
per-value specialization within those programs.

The first fix removed recursive helpers but left a 3.3% residual size-check cost
(24.58→25.39 ms against historical runtime on identical IR). The second fix
also compiles out impossible tagged sizes. Final historical A/B is
**24.463→24.545 ms (+0.34%)**; immediate pre-fix A/B is
**39.158→24.540 ms (-37.3%)**. No root or quota guarantee was weakened.

| Workload | Size | Before NIL ms | Final NIL ms | Final C++ ms | Final Python ms |
|---|---:|---:|---:|---:|---:|
| append | 10000 | 2.927 | 2.853 | 2.454 | 14.803 |
| append | 40000 | 3.901 | 3.519 | 2.601 | 15.733 |
| append | 160000 | 8.096 | 6.071 | 2.900 | 19.170 |
| append | 640000 | 24.522 | 16.157 | 4.053 | 32.940 |
| append | 1048576 | 38.538 | 24.764 | 4.999 | 44.776 |
| newlines | 4096 | 2.438 | 2.551 | 2.489 | 14.427 |
| newlines | 1048576 | 2.783 | 2.890 | 2.973 | 15.131 |
| newlines | 16777216 | 7.577 | 7.836 | 10.447 | 24.476 |
| transform | 4096 | 2.560 | 2.651 | 2.507 | 14.751 |
| transform | 1048576 | 4.809 | 5.143 | 3.441 | 63.833 |
| transform | 16777216 | 38.030 | 37.922 | 13.828 | 810.024 |

Transform output is byte-exact and a double transform round-trips. The final
16 MiB standard median is **37.922 ms**, inside the historical range. A same-IR
runtime A/B is **40.289→39.878 ms (-1.0%)**: these data do not attribute the
overseer's transform elevation to a compulsory child-root cost. They do not
explain every cross-session fluctuation; warm I/O, scheduling and compiler-code
layout remain uncontrolled. The scan A/B is 7.745→7.624 ms. Every raw sample is
retained; no faster run replaces a slower result or changes the timed protocol.

Read-only/read-write stage profiles are retained in V5_COLLECTION_TRANSFORM_CONTROL.json.

| Input bytes | Read-only ms | Read+write ms | Full transform ms |
|---|---:|---:|---:|
| 4096 | 2.359 | 2.437 | 2.651 |
| 1048576 | 2.552 | 2.866 | 5.143 |
| 16777216 | 5.157 | 11.403 | 37.922 |


| Keyed path | Iterations / held bytes | Before ms | Final ms |
|---|---:|---:|---:|
| insert | 1000 | 2.789 | 2.520 |
| insert | 4000 | 2.698 | 2.723 |
| insert | 16000 | 4.422 | 4.352 |
| insert | 64000 | 11.084 | 10.633 |
| repack | 1000 | 2.906 | 2.666 |
| repack | 4000 | 2.974 | 2.856 |
| repack | 16000 | 7.146 | 7.063 |
| repack | 64000 | 73.204 | 74.495 |
| repack-held | 4096 | 2.597 | 2.508 |
| repack-held | 65536 | 3.838 | 3.922 |
| repack-held | 1048576 | 21.117 | 22.191 |
| record-insert | 1000 | 2.719 | 2.535 |
| record-insert | 4000 | 2.756 | 2.836 |
| record-insert | 16000 | 4.551 | 4.547 |
| record-insert | 64000 | 11.761 | 11.469 |
| record-append | 10000 | 3.720 | 3.609 |
| record-append | 40000 | 16.888 | 16.948 |
| record-append | 160000 | 322.691 | 409.224 |

**Record-field append remains superlinear and unresolved.** Its 160k standard
median rises 322.691→409.224 ms. A same-IR comparison against pre-fix collections
is 337.367→402.060 ms (+19.2%), while against the historical pre-collection runtime
it is 381.623→379.299 ms (-0.6%). Both controls are retained. The additional
revision/code-shape-dependent difference is not isolated further or declared
noise/unavoidable. Field-sensitive reuse remains deferred; old field aliases still
force payload copies. This does not undo the restored ordinary append path or
establish C++-class performance for field builders.

Accepted limits: fresh/shared nested builders remain quadratic; aliased builders
copy; record-field append is superlinear; keyed payload repacking remains
superlinear. The reference evaluator traverses live graphs and is not a fast
execution backend. Mixed record-buffer programs keep conservative child-aware
root operations. Record sorting/comparators, sequence-bearing record map values,
generic nested maps and complete JSON/domain adapters remain deferred. Bulk
equality's **~16.96 ms** plugin-round regression is outstanding and unchanged.
No equality lowering was modified or new corpus task added in the continuation.
Map ceilings stay 262,145 integer entries / 262,144 scalar-record entries for the
measured workloads; each next value traps E013. Nonzero record-buffer boundaries
above are rechecked unchanged. 64 MiB still includes conservative copy/growth peaks.

## Zero-slot proof and reproduced failure

`record Z(x:0)` with `=#!buffer[Z](2,Z([]))` now returns **2** in the reference,
O0, O2, sanitized O0 and sanitized O2, all exit 0 with empty stderr. The retained
pre-fix binary still produces UBSan division-by-zero and aborts; the overseer's
uninstrumented O2 reproduction exits 133. See V5_COLLECTION_ZERO_LAYOUT.json
for source, reference driver, commands and outputs. Initial 353-test/131-sanitizer/
864-program campaigns did not cover this class and are superseded, not completion
evidence. All listed final gates were repeated after the last C change.

Logical slots remain zero. Physical rows/metadata use at least one initialized
word, so division denominators are ≥8 and the descriptor pointer fits. A zero-slot
product cannot contain a dynamic child, since every dynamic handle contributes
one slot. Embedding its buffer in an outer record contributes a handle and uses
the unchanged transitive-edge proof. Mixed products keep their unpadded logical
field offsets; scalar-record maps retain zero-byte value encodings. Quota charging
matches native/reference physical width, including metadata and reserved capacity.
No valid empty-field type was rejected to narrow coverage.

## Validation and findings

- `./scripts/ci.sh` and `./scripts/ci.sh release`: **358 tests**, no warnings.
- `./scripts/sanitize.sh`: **135 native tests**, all six suites, ASan/UBSan/float-cast
  checks clean; macOS LeakSanitizer unavailable, no leak claim. Includes strengthened
  record snapshot updates, packed scalar bits, nested aliases and quota reclamation.
- Three final seeds 1729/8675309/5130572: **924 programs / 1,848 O0/O2 builds**,
  zero divergences. All 44 collection families run once per seed, including
  nested lifetime, child/old aliases, growth, calls/loops, lazy effects, provider
  transfer, nested each/sort/maps and quota. This is bounded template coverage,
  not exhaustive arbitrary type/schema fuzzing. The 20 degenerate families cover
  single/all-zero fields, mixed fields, nested zero products, maps, buffers,
  aliasing, construction/update/growth, calls/loop state, lazy arms and failures.
- Per seed: OK222, E0092, E01218, E01322, E0145, E0154, E01610, E0173, E0185,
  E0193, E0206, E0215, E0223. Aggregate counts are triple; frontend source-mutation
  counts are separate, including 540 collection mutations. Some substitutions
  leave a template unchanged; those counts are not a claim of 540 rejected programs.
- **2,775 frozen corpus checks pass**, original **610 separately**; supplemental
  random algorithms **600** and type-layout probes **12** pass. Corpus unittest
  suite passes 23, including untouched source/oracle/baseline hash locks.
- IR regression test asserts `nil_record_set(... i1 true ...)` in a proven
  single-use loop and `i1 false` with a live alias. Runtime roots==1 still guards
  the fast path. See V5_COLLECTION_STORAGE_IR.txt.

A real compiler/runtime defect was found after the first clean campaigns:
zero-slot record-buffer rows caused division by zero, a process crash at O2,
and O0/O2 divergence. The overseer reproduced exit 133; local UBSan identified
the division. This was a generator coverage gap, not merely an instrumented UB
warning. The continuation pads rows/metadata to one initialized word, preserves
logical empty fields, and adds 20 degenerate-layout families covering all-zero,
nested-zero and mixed records in buffers, maps, aliases and loop state.
Development fixtures had incorrect function labels/return types, noncanonical
`(i)` arity and unsupported &&/||; they were corrected rather than adding syntax.
Two earlier sanitizer/fuzz campaigns overlapped a plugin-manifest capability edit
and old binaries rejected its directive E024. Those runs were invalidated/discarded,
then all final gates were repeated against stable code. Harness tests caught stale
75-task assumptions and JSONL's missing overlap metadata; only integration code/
tests changed, never frozen oracles/goldens. Timing exposes real remaining costs
and the repaired ordinary append regression plus unresolved field-builder costs; clean correctness runs are not evidence of fast
nested builders or complete general-purpose library coverage.

## Reproduce (repository root)

```sh
./scripts/ci.sh
./scripts/ci.sh release
./scripts/sanitize.sh
./scripts/fuzz-v5.sh --seed 1729 --cases 308 --out /tmp/nil-v5-1729
./scripts/fuzz-v5.sh --seed 8675309 --cases 308 --out /tmp/nil-v5-8675309
./scripts/fuzz-v5.sh --seed 5130572 --cases 308 --out /tmp/nil-v5-5130572
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/verify.py --output /tmp/nil-verify.json
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/verify.py --group original --output /tmp/nil-original.json
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/algorithms/check_random.py --seed 30030 --cases 30 --output /tmp/nil-random.json
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/density.py --verification /tmp/nil-verify.json --output /tmp/nil-density
benchmarks/paired/.venv/bin/python -m unittest discover -s benchmarks/corpora/application-v5/tests
benchmarks/paired/.venv/bin/python benchmarks/application/collections/probes.py --output /tmp/nil-probes.json
benchmarks/paired/.venv/bin/python benchmarks/application/collections/run.py --repeats 25 --output /tmp/nil-scaling
./scripts/bench.sh runtime --full --workloads --workload newlines --workload append --repeats 25 --output /tmp/nil-controls
./scripts/bench.sh runtime --full --application --repeats 25 --output /tmp/nil-transform
benchmarks/paired/.venv/bin/python benchmarks/application/keyed/run.py --records --repeats 25 --output /tmp/nil-keyed
benchmarks/paired/.venv/bin/python benchmarks/application/collections/legacy_control.py --before d72a23d --repeats 25 --output /tmp/nil-root-ab
benchmarks/paired/.venv/bin/python benchmarks/application/collections/legacy_control.py --before d72a23d --workload newlines --repeats 25 --output /tmp/nil-scan-ab
benchmarks/paired/.venv/bin/python benchmarks/application/collections/legacy_control.py --before d72a23d --workload transform --repeats 25 --output /tmp/nil-transform-ab
benchmarks/paired/.venv/bin/python benchmarks/application/collections/legacy_control.py --before 1689ffe --repeats 25 --output /tmp/nil-historical-root-ab
benchmarks/paired/.venv/bin/python benchmarks/application/collections/legacy_control.py --before d72a23d --workload record-append --repeats 25 --output /tmp/nil-field-ab
benchmarks/paired/.venv/bin/python benchmarks/application/collections/legacy_control.py --before 1689ffe --workload record-append --repeats 25 --output /tmp/nil-historical-field-ab
./target/release/nil --profile expr-v5 build benchmarks/application/collections/boundary-nested.nil -O2 -o /tmp/nil-nested-boundary
/tmp/nil-nested-boundary 4194297
/tmp/nil-nested-boundary 4194298 # E013 expected
```

Run timing commands sequentially after functional campaigns, not concurrently.
Environment/pinned vocabulary setup is the existing paired environment; density
requires local pinned assets but no inference service. Commands/results are in
V5_COLLECTION_RECEIPTS.txt; measured JSON/CSV/JSONL and source hashes sit beside it.
All commits are local on feat/application-core and the benchmark submodule branch.
Nothing was pushed; no further optimization/library work is automatically started.
