# Ordered maps: capability, density and cost

Maps add capability, **not a reversal of the Python density gap**. After this
round NIL costs **12.0–21.1% more source tokens than Python externally and
6.9–14.6% more combined**. It still costs 42.2–46.0% fewer than C++ externally
and 47.6–50.9% fewer combined. The original 24 counts are unchanged.

**Density is not model efficiency.** Total generated/repair tokens until a correct
program remain the thesis. The frozen generation study measured NIL 0/24 versus
Python 11/24. No model inference, adaptation, syntax compression or tokenizer
change occurred here. [Generation evidence](V5_GENERATION.md).

## Decision and implementation

[ADR 023](../../../docs/adr/023.md) was committed as `95db914` before implementation
`9cf1f43`/`d10ed11`. Dynamic keys address ETL/assignments/dictionaries/visited sets;
records chiefly package go_counting's product and existing positional state.
The minimal winner is Bytes->I64 and Bytes->Bytes maps, not records or recursive
maps. Iteration is insertion order, replacing retains index, hashing cannot
change order. Owned key/value bytes keep the existing flat arena/root accounting.
Missing key E019 and duplicate E020 precede result quota; index E012, signature
E007 and absent dot syntax E001. Single-use plus live-root uniqueness admit
in-place writes; every alias or resize copies. Entry/hash and byte arenas grow
geometrically; different-length byte replacement repacks the entire owned payload.

The initial ADR estimate selected the wrong helper lines (wrapper + one mask
helper). The preserved forecast was 13 o200k tokens. Correct lines 9–10 cost 79,
not 49; verified grade_school drops 409->367 (42 tokens, 10.3%). This is a disclosed
analysis indexing error, not a changed corpus contract or retrospectively edited
forecast. No fuzzer divergence or sanitizer defect was found.

## Verified support and limits

All 75 tasks retained: **56 verified NIL programs / 19 unsupported**, including
32 supported / 18 unsupported external tasks. ETL alone moves to supported;
its compact JSON Latin-letter score adapter passes the same expected bytes. It
is not a general JSON parser. Grade_school uses maps for duplicate enrollment,
retaining its existing sorting algorithm. Existing baseline sources, tasks,
oracles, goldens and original NIL references are hash-locked and unchanged.
New ETL baselines were added, not substituted for existing baselines.

2,400 checks pass: 478 reference, 956 native (478 each O0/O2), 483 Python, 483 C++.
The original 610 separately pass: 120 reference, 240 native, 125 each baseline.
The support-only overlay does not change inputs/prompts/expected outputs.
[Verification](V5_KEYED_VERIFICATION.json), [original](V5_KEYED_ORIGINAL_VERIFICATION.json),
[attempts and remaining adapters](../../corpora/application-v5/KEYED_ATTEMPTS.md).

Alphametic search, Forth parsing/definition interpretation and Camicia simulation
remain unimplemented adapters even though maps can encode assignments, definitions
and visited states. dot_dsl still needs nested graph attributes; go_counting needs
an owner/coordinate-pair product or an explicit serialized flood-fill adapter.
Unsupported is verification status, not theoretical unexpressibility. No fixture
lookup solution, dropped task or reduced oracle was used.

## Three cuts, four real tokenizers

Whole reference sources including I/O/imports/comments; no special tokens.
Pinned Gemma/Qwen vocabularies and cl100k/o200k versions match the preceding study.
[Full provenance and versions](V5_KEYED_DENSITY.json). Qwen JSON cross-check passes
all 170 verified source comparisons. Every per-task language/tokenizer count and
bytes/characters appears in [before/after CSV](V5_KEYED_BEFORE_AFTER.csv) and
[after CSV](V5_KEYED_TOKENS.csv); unsupported rows remain explicit.

Positive gaps mean NIL is larger. Before external had 31 paired tasks; after has
32, so its aggregate change combines a rewrite and newly supported ETL.

| Cut | Tokenizer | Before NIL/Python/C++ | After NIL/Python/C++ | Before Py gap | After Py gap | After C++ gap |
| --- | --- | --- | --- | ---: | ---: | ---: |
| original | gemma3_4b | 2144/2227/5454 | 2144/2227/5454 | -3.73% | -3.73% | -60.69% |
| original | qwen2.5_7b_instruct | 1634/1728/4235 | 1634/1728/4235 | -5.44% | -5.44% | -61.42% |
| original | cl100k_base | 1582/1705/4217 | 1582/1705/4217 | -7.21% | -7.21% | -62.49% |
| original | o200k_base | 1571/1712/4238 | 1571/1712/4238 | -8.24% | -8.24% | -62.93% |
| new_external | gemma3_4b | 7372/6147/12712 | 7586/6262/13128 | +19.93% | +21.14% | -42.22% |
| new_external | qwen2.5_7b_instruct | 5650/5025/10148 | 5828/5112/10493 | +12.44% | +14.01% | -44.46% |
| new_external | cl100k_base | 5520/4949/10113 | 5686/5036/10458 | +11.54% | +12.91% | -45.63% |
| new_external | o200k_base | 5498/4972/10153 | 5667/5059/10498 | +10.58% | +12.02% | -46.02% |
| combined | gemma3_4b | 9516/8374/18166 | 9730/8489/18582 | +13.64% | +14.62% | -47.64% |
| combined | qwen2.5_7b_instruct | 7284/6753/14383 | 7462/6840/14728 | +7.86% | +9.09% | -49.33% |
| combined | cl100k_base | 7102/6654/14330 | 7268/6741/14675 | +6.73% | +7.82% | -50.47% |
| combined | o200k_base | 7069/6684/14391 | 7238/6771/14736 | +5.76% | +6.90% | -50.88% |

On the **same 31 external tasks**, only grade_school changes: its reduction is
64/44/44/42 Gemma/Qwen/cl100k/o200k tokens. The corresponding external Py gaps
become 18.89/11.56/10.65/9.73%, a modest improvement, not parity. Adding ETL then
widens the gap again. All other previously supported tasks are unchanged; none
gets worse on the same source cohort. Every prior density loss remains listed
in the JSON; grade_school still loses to both baselines on every tokenizer.

| Changed/new task | Tokenizer | Before NIL | After NIL | Python | C++ |
| --- | --- | ---: | ---: | ---: | ---: |
| ex_grade_school | gemma3_4b | 593 | 529 | 154 | 377 |
| ex_grade_school | qwen2.5_7b_instruct | 416 | 372 | 120 | 292 |
| ex_grade_school | cl100k_base | 413 | 369 | 120 | 292 |
| ex_grade_school | o200k_base | 409 | 367 | 121 | 294 |
| ex_etl | gemma3_4b | unsupported | 278 | 115 | 416 |
| ex_etl | qwen2.5_7b_instruct | unsupported | 222 | 87 | 345 |
| ex_etl | cl100k_base | unsupported | 210 | 87 | 345 |
| ex_etl | o200k_base | unsupported | 211 | 87 | 345 |

| Cut | NIL bytes/chars | Python bytes/chars | C++ bytes/chars |
| --- | ---: | ---: | ---: |
| original | 3310/3310 | 6746/6746 | 17283/17283 |
| new_external | 11303/11303 | 19423/19423 | 42130/42130 |
| combined | 14613/14613 | 26169/26169 | 59413/59413 |

All source files are ASCII, so source bytes equal characters; fixtures include
binary/Unicode bytes. Density measurements do not test LLM parsing familiarity.
Only one newly supported task and one rewrite: no population-level inference.
Externally originated tasks were mechanically selected, but solutions remain
locally authored, first-property transports are partial APIs, and finite fixture
oracles/unsupported exclusions limit generalization. The JSONL export has 56
verified positives: still about 9–36x below the heuristic 500–2,000 independent-task
pilot, with related families and no demonstrated fine-tuning success.

## Insertion, update and quota measurements

Whole-process wall time, one warmup, nine repeats, exact scalar outputs verified;
Clang O2/LTO, decimal keys, no CPU isolation or startup subtraction. Keys/hashes,
growth and roots are included. No matched C++ map-performance claim is made.
[Raw samples, hashes and boundary outputs](V5_KEYED_PERFORMANCE.json).

| Program | Iterations | Retained unrelated bytes | Median ms |
| --- | ---: | ---: | ---: |
| insert | 1000 | — | 2.497 |
| insert | 4000 | — | 2.924 |
| insert | 16000 | — | 4.195 |
| insert | 64000 | — | 10.219 |
| repack | 1000 | — | 2.630 |
| repack | 4000 | — | 2.845 |
| repack | 16000 | — | 6.786 |
| repack | 64000 | — | 72.768 |
| repack-held | 1000 | 4096 | 3.772 |
| repack-held | 1000 | 65536 | 4.109 |
| repack-held | 1000 | 1048576 | 21.431 |

Unique insert has the expected linear growth above startup, not full-map copying
per update; hash collisions can still worsen lookup. `repack` deliberately grows
a fresh byte argument by one byte each iteration: its quadratic whole-workload
cost includes argument construction **and** map replacement. `repack-held`
alternates one/two-byte replacements for 1,000 iterations while retaining a large
unrelated value; it isolates whole-map repacking from constructing a large new
argument each time. This limitation is retained and specified, not hidden.

The decimal-key integer builder succeeds at **262,145 entries**, then E013 at
262,146: the first 524,288-entry-capacity growth fits old+result, but the next full
result reservation no longer fits two such capacities under 64 MiB. Reference and
native agree at 262,144/262,145/262,146. It is not a universal map maximum: key/value
lengths and other roots change the boundary. Aliases also force copying, so retained
historical maps can make insertion quadratic. No limit was raised.

## Existing performance controls

Same existing harness/method: nine repeats, one warmup, rotating language order,
cached files, output verification, no fsync/CPU isolation; whole processes. Scan
also verifies arbitrary bytes, append verifies content, transform verifies byte-exact
output and double-transform roundtrip. Previous medians are the last completed
V5_GENERALITY study, not a concurrently rerun before binary.

| Control | Prior NIL ms | Current NIL ms | C++ ms | Python ms |
| --- | ---: | ---: | ---: | ---: |
| newlines 16777216 | 7.371 | 7.476 | 9.959 | 23.681 |
| append 1048576 | 24.153 | 24.088 | 4.805 | 43.189 |
| transform 16777216 | 37.855 | 38.117 | 14.666 | 771.726 |

Small 0.3–1.4% shifts are not evidence of a systematic regression in this unisolated
sample. NIL still loses to C++ on append and transform, wins the measured scan, and
wins all three against Python; this is workload evidence, not universal parity.
All measured sizes and samples (including 4 KiB/1 MiB/16 MiB transform and append
scaling) remain in the JSON.

## Correctness and reproduction

239 debug/release tests, strict Clippy without warnings, 55 ASan/UBSan tests.
Three seeds, 268 programs/536 native O0/O2 builds each: **804 programs / 1,608
native builds, zero divergences**. Each executes two instances of 30 map families,
including constructor/lookup/key/result quota, duplicate-before-quota, aliases,
calls, recursion, nesting byte values, loops and lazy effect order. Corpus map
seeds are retained. [Per-code and call-family counts](V5_KEYED_FUZZ.json).
Template-based generation varies keys/payloads/growth sizes; it is not exhaustive
arbitrary-map-IR fuzzing. Sanitizers disable leak detection on macOS and check
memory accesses/UB, including the large quota failures. No production defect was
found by these runs. [Exact commands and cited output](../../../docs/validation/V5_KEYED_DATA.md).

```sh
./scripts/ci.sh
./scripts/ci.sh release
./scripts/sanitize.sh
./scripts/fuzz-v5.sh --seed 5130572 --cases 268 --out /tmp/nil-map-fuzz-5130572
# Repeat seeds 1729 and 8675309 with different output directories.
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/verify.py --output /tmp/nil-map-verify.json
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/density.py --verification /tmp/nil-map-verify.json --output /tmp/nil-map-density
benchmarks/paired/.venv/bin/python benchmarks/application/keyed/run.py --output /tmp/nil-map-scaling --repeats 9
./scripts/bench.sh runtime --full --workloads --workload newlines --workload append --repeats 9 --output /tmp/nil-map-controls
./scripts/bench.sh runtime --full --application --repeats 9 --output /tmp/nil-map-transform
```

All implementation and benchmark commits are local. Nothing was pushed.
