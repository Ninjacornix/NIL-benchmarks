# Round 13: static higher-order functions

**Unfavourable results first:** the newly supported `ex_accumulate` reference costs 2.87–3.10 times Python's source tokens. Its addition widens external density to **26.9–36.4% above Python**, combined to **19.1–27.1% above**, with every previously verified source/count unchanged. These are cohort changes, not savings. Source density is not failure-inclusive model efficiency; the unfavourable generation and few-shot findings stand. The HOF insertion-sort baseline is also much slower than core sort: 1,022 versus 2.990 ms at 2,048 elements. Static callbacks do not make this algorithm or its allocating, alias-conservative updates competitive.

## Decision and surface

ADR 034 was committed as `59ec17d` before compiler implementation `d1148f2` and tests `6cf7e48`. Static specialization erases all callback parameters before HIR; existing allocation, borrow, escape, effect, alias/reuse and trap-order analyses inspect the actual direct callees. Neither function values nor indirect calls enter HIR. No C runtime, LLVM backend, HIR type or workspace dependency changed. Intrinsic count **35 → 35**.

Measured with tiktoken 0.12.0, cl100k/o200k agree: `[i:i]` costs 3 tokens (`fn(i):i` 4); `&b` costs 2 (`fn(b)`/`ref(b)` 3); `^b(a)` costs 4; `&!plugin(1,0)` costs 8. `(i):i` also costs 3 but is ambiguous with signatures/aggregates. The complete named example costs 20 versus hypothetical anonymous 21, so anonymous functions were excluded. Bare letters keep their existing meaning; caret parameters are lexically bound even inside loops/each. Captured state is passed explicitly as ordinary typed parameters.

Cache keys are template plus concrete callback labels; recursive instances are reserved before their bodies are expanded. Limits are 1,024 total/256 per-template specializations, 4,096 emitted functions and 1,048,576 copied AST instructions, with E008. Value/signature mismatch is E007, arity E006, unknown references E004/E005. Unused templates are parsed/reference-checked; value-body checking happens on instantiation. Public syntax AST parameters now use `Parameter`; embedding clients must adapt. Validated HIR remains first-order.

Ordinary modules may export HOFs and receive caller-local callbacks; exports may themselves be passed as callbacks. A runtime recursion back-edge through a callback works with acyclic imports. A separate reference/O0/O2 probe returned 10 and 126 and uniformly reported E008 at depth 128. Borrow-only `nil-plugin 1` providers reject function parameters with E024; use ordinary modules. Pure/effectful specialization summaries are separate. Unselected arms may be statically checked/specialized but never execute effects, allocations or traps. Existing sort/each and structural bulk equality run on normalized direct-call HIR.

## Tasks versus pre-registration

The frozen selection was ex_accumulate, with ex_reactive classified rather than invented as a new task. Accumulate passed all five frozen cases, including explicit captured-prefix composition: five reference, ten native O0/O2, five Python and five C++ checks. Forecast: one newly supported task; actual: one. New baseline solutions were authored only where none existed. No old task, oracle, golden or baseline source changed (266 frozen files byte-identical). The ASCII JSON/pseudocode adapter is finite and does not claim general runtime code evaluation or Unicode.

`ex_reactive` is absent from this frozen corpus. Mutable runtime subscriber registration is beyond static specialization; ex_hangman remains unsupported. The corpus has **79 tasks, 68 verified NIL programs/JSONL positives, 11 unsupported**: ex_alphametics, ex_dot_dsl, ex_anagram, ex_bob, ex_bank_account, ex_camicia, ex_diffie_hellman, ex_forth, ex_gigasecond, ex_grep, ex_hangman. Their blockers remain in GENERALITY_GAPS.json. The historical `--group original` selection retains exactly 610 checks; full-suite environment support remains enabled. A cohort-selection inconsistency discovered during audit was fixed in the shared task loader and tested, without changing any oracle.

## Performance: 25 warm rotating repeats

Apple M2 arm64, Clang 21, O2, one warm-up, whole-process wall time including file reads/start-up. Min/median/max in milliseconds, no CPU isolation or significance claim. Exact sources, samples, versions and hashes accompany this report. Map-reduce classifies every byte of the same 16 MiB fixture; all variants return 986895.

| Map-reduce form | Min | Median | Max |
|---|---:|---:|---:|
| Inline | 6.871 | 7.156 | 7.700 |
| Ordinary helper | 6.815 | 7.081 | 9.175 |
| Static HOF | 6.812 | 7.186 | 8.231 |
| Ordinary helper, noinline | 19.611 | 19.997 | 21.608 |
| HOF callback, noinline | 19.430 | 19.945 | 20.487 |

HOF +1.48% against direct/+0.42% inline, within measured spread. Noinline HOF -0.26% against direct. The benchmark-only IR hook adds noinline/disable-tail-calls to both callbacks; disassembly contains genuine `bl _nil_fn1`/`bl _nil_fn2`. This isolates retained direct-call cost from an inliner accident.

A second control actually materializes a 16 MiB byte map (255-byte), writes it, compares every byte and double-transforms back to the original:

| Materialized map | Min | Median | Max |
|---|---:|---:|---:|
| Inline | 33.385 | 35.016 | 49.221 |
| Ordinary helper | 33.322 | 34.783 | 41.093 |
| Static HOF | 33.552 | 34.679 | 45.474 |
| Ordinary helper, noinline | 42.629 | 44.305 | 50.827 |
| HOF callback, noinline | 42.415 | 44.009 | 49.537 |

IR proof: both ordinary and HOF map-reduce loops have zero root stores/frame calls, one invariant length query, one direct byte load and ordinary direct callback calls. The unchanged read-range proof establishes index 0,+1 under index<stable length; the 64 MiB limit excludes index overflow. Disassembly has `ldp q27,q26` and `cmeq.16b` for inline/direct/HOF. Noinline variants do not vectorize, as expected. Neither materialized inline nor materialized HOF mutation loop vectorizes; existing checked uniqueness/mutation semantics remain. No new bounds check was removed by this round.

| Descending insertion-sort size | HOF min/median/max | Core sort min/median/max |
|---|---:|---:|
| 256 | 6.376 / 6.655 / 11.808 | 2.081 / 2.283 / 5.041 |
| 1,024 | 151.302 / 151.940 / 155.124 | 2.428 / 2.709 / 3.196 |
| 2,048 | 1,019.111 / 1,021.736 / 1,037.287 | 2.581 / 2.990 / 3.403 |

This compares different algorithms including construction, not isolated callback overhead: insertion-sort's quadratic comparisons plus full-buffer copies through still-live old reads/allocating helper calls produce worse scaling. Library sort migration needs an appropriate algorithm and demonstrated reuse, not merely a comparator parameter.

| Historical control | Min/median/max now | Historical median |
|---|---:|---:|
| Append 1 MiB | 22.139 / 22.709 / 23.241 | 22.84 |
| Newline scan 16 MiB | 7.606 / 7.849 / 8.137 | 7.56 |
| Transform 16 MiB | 35.474 / 36.156 / 42.902 | 36.19 |

Scan is 3.8% above the historical median. An isolated alternating baseline/current audit found 6.638/6.835/12.626 versus 6.743/6.983/15.061, with **byte-identical disassembled executable text** (791 lines, SHA256 in NATIVE_TEXT.json). Six earlier-profile/application examples have byte-identical emitted IR against 07b1ee2. The measured variation therefore identifies no generated-code regression; wide tails remain an environmental limitation. Transform output was byte-exact and double-transform round-tripped. C++/Python medians were append 5.105/45.023, scan 10.418/24.336, transform 13.750/791.747 ms. Transform read-only/read-write stages were 5.222/9.902 ms.

## Source-density cuts (NIL/Python/C++ tokens)

| Cut | Gemma | Qwen | cl100k | o200k |
|---|---|---|---|---|
| Original 25 | 2161/2305/5642 | 1646/1786/4378 | 1594/1763/4360 | 1583/1770/4381 |
| External 43 | 11297/8280/17485 | 8738/6765/13954 | 8524/6684/13908 | 8514/6710/13977 |
| Combined 68 | 13458/10585/23127 | 10384/8551/18332 | 10118/8447/18268 | 10097/8480/18358 |

New accumulate only: 740/239/765, 585/201/628, 578/201/628, 579/202/630 respectively. Bytes/characters: NIL/Python/C++ original 3341/6995/17902; external 18067/25863/55403; combined 21408/32858/73305. Old 201 verified source/language rows retain their token counts. JSON/CSV contain per-task counts, source hashes, tokenizer identifiers/versions and all nonwins. Qwen cross-check has zero mismatches. No inference or training was performed. **Density cannot establish tokens until a correct program including failures/repairs.**

## Gate receipts and exact commands

Run from the main repository; benchmark Python environment is unchanged.

```text
./scripts/ci.sh                          exit 0; 422 tests; zero clippy warnings
./scripts/ci.sh release                  exit 0; 422 tests; zero clippy warnings
./scripts/sanitize.sh                    exit 0; 169 tests across nine suites; clean
./scripts/fuzz-v5.sh --cases 418 --seed 5130572 --out /tmp/nil-hof/final-fuzz-5130572
./scripts/fuzz-v5.sh --cases 418 --seed 1729 --out /tmp/nil-hof/final-fuzz-1729
./scripts/fuzz-v5.sh --cases 418 --seed 4294967295 --out /tmp/nil-hof/final-fuzz-4294967295
# Each: 418 programs, 836 native O0/O2 builds; zero divergences
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/verify.py --output /tmp/nil-hof/corpus-final.json
# 2815 checks: 563 reference, 1126 native, 563 Python, 563 C++
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/verify.py --group original --output /tmp/nil-hof/original-final.json
# exactly 610: 120 reference, 240 native, 125 Python, 125 C++
benchmarks/paired/.venv/bin/python -m unittest discover -s benchmarks/tests
# 10 passed
benchmarks/paired/.venv/bin/python benchmarks/hof-study/performance/run.py --repeats 25 --output /tmp/nil-hof/performance
benchmarks/paired/.venv/bin/python benchmarks/hof-study/performance/materialized.py --repeats 25 --output /tmp/nil-hof/materialized
./scripts/bench.sh runtime --full --workloads --workload append --workload newlines --repeats 25 --output /tmp/nil-hof/historical-controls
./scripts/bench.sh runtime --full --application --repeats 25 --output /tmp/nil-hof/historical-transform
target/debug/nil --profile expr-v5 run examples/expr-v5/higher_order.nil
# 21
```

Each fuzz seed's execution counts: OK 300; E009 3; E012 20; E013 30; E014 6; E015 8; E016 13; E017 10; E018 11; E019 3; E020 6; E021 5; E022 3. HOF malformed-source counts separately: E002 26, E004 26, E005 26, E007 52. E006/E008 specialization failures are covered by unit/native regressions rather than runtime fuzz counts. All 26 HOF families execute once per seed: buffer/byte mapping, allocation/aliasing, selected/unselected effects, ordered effects, read/write/random/env/denial, quota/bounds/trap order, recursion/mutual recursion/held sequences, degenerate zero-slot records, each/forwarding/comparator/module callbacks/lazy allocations. Host stdout and file effects are compared, not just return values. This is a finite seeded typed-family campaign, not exhaustive fuzzing. Totals: 1,254 programs, 2,508 native builds, 78 HOF cases/156 HOF builds.

One compiler defect found and fixed: enlarging the recursive expression-parser frame initially overflowed a test thread on adversarial nesting. Extracting callback parsing restored the old depth regression; a new nested-callback regression guards it. No native memory bug or differential divergence was found. Sanitizers include ASan, UBSan and float-cast checks; macOS leak detection remains unavailable, so this is not an LSan result.

Reproduce tokenizer counts without model inference:

```text
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/density.py --verification /tmp/nil-hof/corpus-final.json --output /tmp/nil-hof/density
benchmarks/paired/.venv/bin/python benchmarks/hof-study/recursion.py --output /tmp/nil-hof/recursive-module-repro
```

Inspect [lowered HOF IR](V5_HIGHER_ORDER_map.ll), [vectorized assembly](V5_HIGHER_ORDER_map.asm), [actual noinline calls](V5_HIGHER_ORDER_map_noinline.asm), [gate receipts](V5_HIGHER_ORDER_VALIDATION.json), [corpus verification](V5_HIGHER_ORDER_CORPUS.json), [original 610](V5_HIGHER_ORDER_ORIGINAL_610.json), [raw performance samples](V5_HIGHER_ORDER_PERFORMANCE.json), [materialized-map samples](V5_HIGHER_ORDER_MATERIALIZED.json), [per-task tokens](V5_HIGHER_ORDER_TOKENS.csv), [tokenizer versions and aggregate cuts](V5_HIGHER_ORDER_DENSITY.json).

## Remaining limits and next round

No runtime-selected function values, closures, callback-returning signatures or polymorphic function recursion. Compile-time bounds deliberately reject excessive specialization. Borrow-only providers cannot receive callbacks; ordinary module HOFs work. Uninstantiated template value-body errors are diagnosed when used. Static callbacks do not satisfy mutable subscription/reactive semantics. Comparator insertion sort is not production-library evidence. Existing alias-conservative/nested builder limits and commutative bulk-matcher limitation remain unchanged.

Part B modulo and local bindings are **deferred**: the earlier 39/225-token estimates are not a newly measured rewrite forecast, and neither is prerequisite to a static library. Introducing numeric remainder/conversion contracts or lexical binding/effect rules deserves its own preregistration; this round introduces neither and edits no old corpus solution. The next library/import-binding round is now unblocked by cross-module HOF, but must measure algorithmic complexity/reuse before migrating sort.

All commits are local. No main or submodule push. User-owned OVERSEER_HANDOFF.md is intentionally untracked. Raw command logs/IR/disassembly are archived locally with the path/hash in ARCHIVE.json; committed JSON receipts and samples make the measurements inspectable without generated binaries.
