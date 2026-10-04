# Expr-v5 records: capability, density and lifetime evidence

**The Python density gap widens, rather than closes.** The 37 external paired
references cost NIL **12.9–23.3% more tokens than Python** across four tokenizers;
the combined 61 cost **8.0–16.8% more**. NIL remains 41.8–46.2% below C++ externally
and 46.9–50.5% below combined. The old 60 solutions and counts are unchanged;
newly supported Go counting contributes all the change. This is a cohort expansion,
not evidence that records made an existing program longer or shorter.

**Source density is not tokens-to-correct-program.** The earlier
[generation study](../2026-10-03/V5_GENERATION.md) solved NIL 0/24 versus Python
11/24, including failures/repairs. Nothing here overturns that unfavourable result.
No inference, training, compiler performance tuning or tokenizer substitution occurred.

## Decision and bounded capability

[ADR 028](../../../docs/adr/028.md) was committed as `95db106` before implementation.
It preregistered zero automatic savings on the old 60 programs: actual **zero**.
Construction, projection and functional update are core product/lifetime primitives;
the typed record-map constructor validates homogeneous storage. There are four new
HIR operations, **zero new Intrinsic variants: 32 before and after** (33 under the
historical convention including `each` lowering). Record equality/order, reflection,
serialization, formatting, defaults and bulk transforms were rejected as future
library surface. Destructuring remains a possible projection lowering. Shortest
float formatting is deferred; ADR 027's fixed format is unchanged.

Records are immutable inline SSA products with individually rooted dynamic leaves.
Nested records and sequence/map fields work. Map values support scalar/fixed-array
records; sequence-bearing record map values, record buffers and recursive types do
not. Product updates do not allocate. Whole-record liveness stays conservative when
a child may allocate: it does **not** silently extend the single-use mutation proof.
No existing program changes meaning; default and earlier profiles stay unchanged.

## Frozen-corpus verification and gaps

Commands from the NIL root (results outside both checkouts):

```sh
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/verify.py --output /tmp/nil-records/verification.json
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/verify.py --group original --output /tmp/nil-records/original-verification.json
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/density.py --verification /tmp/nil-records/verification.json --output /tmp/nil-records/density
```

[Full verification](V5_RECORD_VERIFICATION.json): **2,625 checks** = reference 523,
native O0/O2 1,046, Python 528, C++ 528. [Original group](V5_RECORD_ORIGINAL.json):
**610 checks**, separately reconfirmed. All pass against unchanged tasks, oracles,
goldens and existing baseline sources. Added baseline sources only fill Go's
previously absent paths. Frozen-contract hash tests pass (22 harness tests).
Verification metadata records the then-HEAD `a64473f` while the compiler work was
uncommitted; subsequent local commits contain that implementation plus validation
hardening. Final CI, sanitizer and fuzz runs cover the committed compiler.

**75 tasks, 61 verified NIL positives, 14 unsupported** (13 external). Go counting
moves to supported, with eight pinned upstream fixtures and MIT provenance. Its
reference uses records across calls, nested loop state and `each`, and a fixed-point
flood-fill mask; Python/C++ use queue/set traversal. JSON adapters cover the frozen
compact contract, not arbitrary JSON. The NIL source is not an optimality claim.

Remaining blockers, retained in [the catalogue](../../corpora/application-v5/GENERALITY_GAPS.json):

| Task | Remaining blocker |
|---|---|
| env_lookup | Environment access |
| ex_accumulate | Higher-order callback contract |
| ex_alphametics | Verified constraint search and JSON adapter |
| ex_dot_dsl | Structured collections / sequence-bearing record maps and parser adapter |
| ex_camicia | Game/cycle simulation and JSON adapter; two decks now fit a record |
| ex_binary_search_tree | Recursive/optional child types; encoded adapter absent |
| ex_anagram, ex_bob | Unicode operations |
| ex_bank_account | Concurrency contract |
| ex_diffie_hellman | Entropy |
| ex_forth | Verified dictionary/stack interpreter and JSON adapter |
| ex_gigasecond | Calendar arithmetic |
| ex_grep | Multi-file fixture/runner contract |
| ex_hangman | Reactive integration |

This is **one verified unblock of five record candidates**, not five delivered
solutions. Encodable search/game adapters are implementation gaps, not claims of
inexpressibility. Existing references were deliberately left untouched; no record
refactoring benefit was demonstrated on them. JSONL exports **61 positives** with
provenance; a small, nonrandom partial-API seed, far short of a credible adaptation
training set. Licence status and export format remain in the corpus README.

## Density: every tokenizer and cut

Cells are **NIL / Python / C++ tokens**. Exact per-task counts, bytes, characters,
versions, vocabulary hashes and every NIL loss appear in
[V5_RECORD_DENSITY.json](V5_RECORD_DENSITY.json) and [CSV](V5_RECORD_TOKENS.csv).
Gemma/Qwen use frozen real GGUF vocabularies via llama-cpp-python 0.3.16;
cl100k/o200k use tiktoken 0.12.0. No special tokens are added.

| Cut | Gemma | Qwen | cl100k | o200k |
|---|---:|---:|---:|---:|
| Original 24, unchanged | 2144 / 2227 / 5454 | 1634 / 1728 / 4235 | 1582 / 1705 / 4217 | 1571 / 1712 / 4238 |
| External before, 36 | 7541 / 6711 / 14256 | 5826 / 5468 / 11381 | 5647 / 5387 / 11335 | 5640 / 5411 / 11378 |
| External after, 37 | 8734 / 7083 / 15016 | 6673 / 5785 / 12011 | 6471 / 5704 / 11965 | 6466 / 5728 / 12012 |
| Combined before, 60 | 9685 / 8938 / 19710 | 7460 / 7196 / 15616 | 7229 / 7092 / 15552 | 7211 / 7123 / 15616 |
| Combined after, 61 | 10878 / 9310 / 20470 | 8307 / 7513 / 16246 | 8053 / 7409 / 16182 | 8037 / 7440 / 16250 |
| New Go task alone | 1193 / 372 / 760 | 847 / 317 / 630 | 824 / 317 / 630 | 826 / 317 / 634 |

Go loses to **both** baselines under every tokenizer. External bytes/characters
(ASCII) are 13,403 / 21,999 / 47,824; combined 16,713 / 28,745 / 65,107. The new
algorithm and output scaffolding overwhelm the product's grouping benefit. No
forecast promised a density win on this new task. Per-task nonwins are retained,
not removed from aggregates; absence of unsupported solutions is a selection
limitation. These finite, locally authored implementations do not estimate a
universal language ranking or adaptation effectiveness.

## Attribution movement

Re-run both snapshots with the **same updated classifier**, which recognizes record
declarations and numeric-type syntax. Do not compare to the previous classifier's
category labels. Before: 72 files / 288 streams / 47,631 tokens; after: 74 / 296 /
52,644. Both reconstruct every token and pass exact-sum checks.

```sh
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/attribution.py --density benchmarks/reports/2026-10-04/V5_NUMERIC_DENSITY.json --output /tmp/nil-records/attribution-before
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/attribution.py --density /tmp/nil-records/density/density.json --output /tmp/nil-records/attribution-after
```

[Before](V5_RECORD_ATTRIBUTION_BEFORE.json), [after](V5_RECORD_ATTRIBUTION_AFTER.json).
The cl100k NIL-minus-Python category ledger sums **260 → 767**, exactly **+507**
(Go's 824 − 317). This byte-overlap classification is exhaustive accounting, not a
causal separation of record syntax from algorithm choice.

| Category | Before | After | Change |
|---|---:|---:|---:|
| Numeric literals | 405 | 477 | +72 |
| Operators | 356 | 481 | +125 |
| Signatures | 384 | 455 | +71 |
| Separators | 813 | 982 | +169 |
| Loop delimiters | 169 | 184 | +15 |
| Call identifiers | 11 | 24 | +13 |
| Loop index/bound | 49 | 51 | +2 |
| Boolean literals | 45 | 51 | +6 |
| Intrinsic names | -117 | -81 | +36 |
| Unchanged state | 3 | 4 | +1 |
| Record definitions | 0 | 30 | +30 |
| Comments | 0 | 0 | 0 |
| Text literals | -45 | -53 | -8 |
| Identifiers | -706 | -674 | +32 |
| Keywords | -419 | -444 | -25 |
| Whitespace | -688 | -720 | -32 |
| **Total** | **260** | **767** | **+507** |

## Correctness gates and findings

[Command receipts](V5_RECORD_VALIDATION.txt) and [fuzz JSON](V5_RECORD_FUZZ.json):

- `./scripts/ci.sh` and `./scripts/ci.sh release`: **311 tests each**, zero warnings.
- `./scripts/sanitize.sh`: **105 native tests** (37 application, 32 keyed,
  19 numeric, 17 record), clean ASan/UBSan/float-cast-overflow. Existing macOS
  LeakSanitizer exclusion still applies.
- `./scripts/fuzz-v5.sh --seed SEED --cases 240 --out /tmp/nil-records/fuzz-SEED`:
  seeds **5130572, 1729, 8675309**, **720 programs / 1,440 O0/O2 native builds**,
  zero reference/native divergences. All 32 record families run once per seed,
  with construction, updates, duplicate leaf aliases, nested/called lifetimes,
  loops, recursion, lazy/effect order, map ordering/failures/quotas and each snapshots.
  Static E023 and malformed record syntax are covered by mutation and unit tests.

Per seed: `OK:171 E009:1 E012:14 E013:14 E014:5 E015:3 E016:10 E017:3
E018:4 E019:2 E020:5 E021:5 E022:3`. The JSON retains all call-family and source
mutation counts. This is a bounded seeded template campaign, not arbitrary-program
coverage or a proof. Every new record operation also has named O0/O2 native tests.

Two implementation defects were fixed before the final gates: expanding parser
helpers overflowed the debug stack in an existing excessive-nesting regression;
small helper splits restored the unchanged 128-level limit. Code review caught a
record-map sort guard returning E018 for mode 2 instead of the existing E012;
validation now checks invalid mode first. Regression tests cover both. Initial Go
reference adapters had comma-offset and runner-wrapper mistakes, fixed before
admission. Sanitizers and differential campaigns found no further runtime defect.

## Performance and explicit conservative boundary

Serial runs on Apple M2/macOS 27, Apple Clang 21, **25 repetitions**, warmup,
whole-process wall time including startup/I/O, verified output, no CPU isolation:

```sh
./scripts/bench.sh runtime --full --workloads --workload newlines --workload append --repeats 25 --output /tmp/nil-records/controls-workloads
./scripts/bench.sh runtime --full --application --repeats 25 --output /tmp/nil-records/controls-transform
benchmarks/paired/.venv/bin/python benchmarks/application/keyed/run.py --records --repeats 25 --output /tmp/nil-records/controls-keyed
```

Raw samples/provenance: [workloads](V5_RECORD_WORKLOADS_CONTROL.json),
[transform](V5_RECORD_TRANSFORM_CONTROL.json), [keyed](V5_RECORD_KEYED_CONTROL.json).
The existing methodology and sources are unchanged for old controls. This is a
regression control, not a new claim of general C++ parity.

| Control | NIL before, 9 repeats (ms) | NIL now, 25 (ms) | C++ now | Python now |
|---|---:|---:|---:|---:|
| Scan 16 MiB | 7.908 | 7.573 | 10.202 | 24.173 |
| Append 1 MiB | 24.153 | 24.626 | 5.042 | 44.255 |
| Transform 16 MiB | 45.846 | 34.991 | 13.973 | 797.588 |

Current NIL interquartile ranges: scan **7.456–7.634**, append **24.485–24.738**,
transform **34.357–38.656** ms. Append's median is 2.0% above the earlier snapshot;
that small difference across nonisolated runs does not establish a compiler
regression. Transform also varies in C++ and I/O; its lower median is not attributed
to records. No clear regression is established. Byte-exact outputs and all double
transform round trips pass.

| Input | Transform NIL / C++ / Python (ms) |
|---|---:|
| 4 KiB | 2.630 / 2.531 / 14.321 |
| 1 MiB | 5.073 / 3.445 / 63.240 |
| 16 MiB | 34.991 / 13.973 / 797.588 |

Append loop NIL at 10k / 40k / 160k / 640k / 1MiB:
**2.849 / 3.554 / 5.982 / 16.131 / 24.626 ms**, still linear above startup.

| Inserts | Existing integer map (ms) | Scalar-record map (ms) |
|---|---:|---:|
| 1,000 | 2.614 | 2.759 |
| 4,000 | 2.686 | 2.751 |
| 16,000 | 4.333 | 4.496 |
| 64,000 | 10.692 | 11.247 |

Record-map growth uses the existing unique proof and is not quadratic. Tested
ceiling for `Pair(i,i)` decimal-key insert workload: **262,144 succeeds;
262,145 traps E013**. Integer map's unchanged ceiling is 262,145 (262,146 E013).
These are workload-specific capacities/transient results, not a general map limit.

**Sequence-field appends inside an updated record remain superlinear:**
10k **3.653 ms**, 40k **16.955 ms**, 160k **396.285 ms**. Whole-record liveness
retains the old sequence alias while evaluating the functional update, so the
existing append proof keeps copying. No alias exemption was added to improve a
number. Product construction/update itself does not allocate; this cost is the
contained sequence operation. Resolving field-sensitive reuse needs a separate
proof/design goal, not a weakened lifetime guarantee. Byte-map repack also remains
quadratic; its measured controls are retained in the keyed JSON.

All commits are local; neither repository was pushed.
