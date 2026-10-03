# expr-v5 application generation and repair: unfavourable result

## Finding

**expr-v5 did not reduce total tokens to correct programs in this frozen study.**
It solved **0/24 trials**, versus Python's **11/24**, and spent more input-plus-output
tokens under both models. Gemma spent **49,911** tokens on v5 versus **23,492** on
Python; Qwen spent **35,640** versus **14,260**. These totals include every failed
attempt and repair. They are not successful-source-length comparisons.

V5 TCR is **undefined because there are zero correct programs**, not zero or a
fabricated finite ratio. Python failure-inclusive output TCR is **1,499.0 / 429.9**;
input-plus-output TCR is **5,873.0 / 2,037.1** for Gemma/Qwen respectively.
No repair succeeded in either language: all eleven solves occurred on attempt zero.
Both languages failed the nonempty-line task on every seed. This is an unfavourable
result for the tested pretrained models and fixed prompt, not evidence of a
fundamental limit for every model or possible NIL adaptation.

## Frozen definition and execution

Four tasks: ASCII byte transformation, filtering nonempty LF-delimited segments,
parsing comma-separated signed integer pairs, and accumulating a formatted running
report. Each has four executable, byte-exact inputs, including the applicable
empty/binary/CR/unterminated/negative cases. Task contracts were fixed before
inference, not selected after results. The [definition and reproduction guide](../../generation/application/README.md)
links versioned tasks, budgets, language references and oracles.

Two frozen local models, three seeds (17/29/43), two languages: **48 trials / 122
attempts**. Temperature 0.2, context 8192, maximum three attempts, 512 output tokens
per request and 1536 per trial. Languages rotate by task/seed; models run sequentially.
Both receive a fixed language reference and generic copy-file example, then the
same task/effect contract. NIL's longer onboarding reference is charged as input;
Python's pretrained familiarity/standard library is a real part of this comparison.
No fine-tuning, custom tokenizer, grammar-constrained decoding or syntax change.

Repair prompts preserve the full conversation and add actual parse/type/compiler
errors or generic semantic feedback. Hidden vectors, expected bytes and solutions
are never included. All returned provider `eval_count` and `prompt_eval_count`
are retained: **zero missing usage counts**, zero infrastructure errors in the
valid run. Output includes prose/fences/truncated code; input includes repeated
context. Thinking cost is not invented or double-counted. Source characters and
UTF-8 bytes are separate; raw source tokenizer counts were not collected here.

Correctness requires unchanged input, exact output bytes, exact returned byte
length and no extra stdout. NIL's in-memory Host reference and bounded native
O0/O2 paths must all pass; Python runs the same file contract in Python 3.12.
Native/Python processes use the validated macOS sandbox with fixture-only writes,
no network/user-data reads, and deadlines. The compiler/runtime/profiles remain
unchanged from `7455d34`. All handwritten language/task fixtures pass, establishing
that the adapter and supported language can solve these contracts.

Compiler revision: `91e3d6058bb0a3ec2d8009cb73fbbc035e367fca` (documentation only).
Frozen corrected benchmark revision: `eea0995549c86239efad6a391d271e2d60f35c85`.
macOS 27 arm64 / Apple M2, Python **3.12.11**, Rust **1.98.1**, Ollama **0.9.0**.
Model/template/server metadata and 57 measured-source hashes are retained.

| Model | Model digest | Quantization |
|---|---|---|
| gemma3:4b | a2af6cc3eb7fa8be8504abaf9b04e88f17a119ec3f04a3addf55f92841195f5a | Q4_K_M |
| qwen2.5:7b-instruct | 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e | Q4_K_M |

These are the original pilot's exact local model digests. They were available on
disk; Ollama was started temporarily, no model substituted/downloaded, and the
owned server/runner were stopped after inference. Neither interrupted pilot nor
synthetic stub is pooled with these results.

## Aggregate failure-inclusive usage

Input/output/repair columns are total spent tokens across **all** trials in that
row. Repair is a subset of output, not an additional charge. TCR denominators are
solved trials; first pass is a count. Do not pool different model vocabularies into
a headline token-saving percentage.

| Model | Language | Solved | First pass | Input | Output | Repair output | TCR-out | TCR input+output |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Gemma 3 4B | expr-v5 | 0/12 | 0 | 40,056 | 9,855 | 6,570 | undefined | undefined |
| Gemma 3 4B | python | 4/12 | 4 | 17,496 | 5,996 | 3,610 | 1,499.0 | 5,873.0 |
| Qwen 2.5 7B | expr-v5 | 0/12 | 0 | 32,353 | 3,287 | 2,193 | undefined | undefined |
| Qwen 2.5 7B | python | 7/12 | 7 | 11,251 | 3,009 | 1,494 | 429.9 | 2,037.1 |

## Every task

Each row contains all three seeds, including unsolved trials. “undefined” also
applies to Python tasks with no solves; it is never interpreted as free work.

| Task | Model | Language | Solved | First pass | Input | Output | Repair output | TCR-out | TCR input+output |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| ascii_upper | Gemma 3 4B | expr-v5 | 0/3 | 0 | 7,677 | 207 | 138 | undefined | undefined |
| ascii_upper | Gemma 3 4B | python | 3/3 | 3 | 1,164 | 411 | 0 | 137.0 | 525.0 |
| ascii_upper | Qwen 2.5 7B | expr-v5 | 0/3 | 0 | 7,845 | 690 | 460 | undefined | undefined |
| ascii_upper | Qwen 2.5 7B | python | 3/3 | 3 | 1,140 | 362 | 0 | 120.7 | 500.7 |
| nonempty_lines | Gemma 3 4B | expr-v5 | 0/3 | 0 | 12,030 | 4,608 | 3,072 | undefined | undefined |
| nonempty_lines | Gemma 3 4B | python | 0/3 | 0 | 5,904 | 1,998 | 1,332 | undefined | undefined |
| nonempty_lines | Qwen 2.5 7B | expr-v5 | 0/3 | 0 | 8,269 | 1,017 | 682 | undefined | undefined |
| nonempty_lines | Qwen 2.5 7B | python | 0/3 | 0 | 4,946 | 1,186 | 840 | undefined | undefined |
| sum_pairs | Gemma 3 4B | expr-v5 | 0/3 | 0 | 12,321 | 4,608 | 3,072 | undefined | undefined |
| sum_pairs | Gemma 3 4B | python | 1/3 | 1 | 4,343 | 1,437 | 846 | 1,437.0 | 5,780.0 |
| sum_pairs | Qwen 2.5 7B | expr-v5 | 0/3 | 0 | 8,244 | 875 | 584 | undefined | undefined |
| sum_pairs | Qwen 2.5 7B | python | 3/3 | 3 | 1,212 | 369 | 0 | 123.0 | 527.0 |
| running_report | Gemma 3 4B | expr-v5 | 0/3 | 0 | 8,028 | 432 | 288 | undefined | undefined |
| running_report | Gemma 3 4B | python | 0/3 | 0 | 6,085 | 2,150 | 1,432 | undefined | undefined |
| running_report | Qwen 2.5 7B | expr-v5 | 0/3 | 0 | 7,995 | 705 | 467 | undefined | undefined |
| running_report | Qwen 2.5 7B | python | 1/3 | 1 | 3,953 | 1,092 | 654 | 1,092.0 | 5,045.0 |

## Variation across repeats

Exact input-plus-output cost per trial, in seed order **17 / 29 / 43**, followed
by sample standard deviation across those three values. These costs retain failed
trials; this is not solved-only TTCP. Identical repeats do not create independent
task diversity or justify narrow generalization intervals.

| Task | Model | Language | Total costs by seed | Sample SD |
|---|---|---|---|---:|
| ascii_upper | Gemma 3 4B | expr-v5 | 2,628 / 2,628 / 2,628 | 0.0 |
| ascii_upper | Gemma 3 4B | python | 522 / 522 / 531 | 5.2 |
| ascii_upper | Qwen 2.5 7B | expr-v5 | 2,865 / 2,739 / 2,931 | 97.5 |
| ascii_upper | Qwen 2.5 7B | python | 500 / 500 / 502 | 1.2 |
| nonempty_lines | Gemma 3 4B | expr-v5 | 5,546 / 5,546 / 5,546 | 0.0 |
| nonempty_lines | Gemma 3 4B | python | 2,634 / 2,634 / 2,634 | 0.0 |
| nonempty_lines | Qwen 2.5 7B | expr-v5 | 2,852 / 3,302 / 3,132 | 227.2 |
| nonempty_lines | Qwen 2.5 7B | python | 2,073 / 1,986 / 2,073 | 50.2 |
| sum_pairs | Gemma 3 4B | expr-v5 | 5,643 / 5,643 / 5,643 | 0.0 |
| sum_pairs | Gemma 3 4B | python | 599 / 2,658 / 2,523 | 1151.8 |
| sum_pairs | Qwen 2.5 7B | expr-v5 | 2,993 / 2,973 / 3,153 | 98.7 |
| sum_pairs | Qwen 2.5 7B | python | 523 / 529 / 529 | 3.5 |
| running_report | Gemma 3 4B | expr-v5 | 2,820 / 2,820 / 2,820 | 0.0 |
| running_report | Gemma 3 4B | python | 2,865 / 2,685 / 2,685 | 103.9 |
| running_report | Qwen 2.5 7B | expr-v5 | 2,904 / 2,877 / 2,919 | 21.3 |
| running_report | Qwen 2.5 7B | python | 2,499 / 503 / 2,043 | 1045.9 |

Aggregate seed breakdown keeps input, output and repair separate:

| Model | Language | Seed | Solved | Input | Output | Repair output |
|---|---|---:|---:|---:|---:|---:|
| Gemma 3 4B | expr-v5 | 17 | 0/4 | 13352 | 3285 | 2190 |
| Gemma 3 4B | python | 17 | 2/4 | 4859 | 1761 | 960 |
| Gemma 3 4B | expr-v5 | 29 | 0/4 | 13352 | 3285 | 2190 |
| Gemma 3 4B | python | 29 | 1/4 | 6348 | 2151 | 1356 |
| Gemma 3 4B | expr-v5 | 43 | 0/4 | 13352 | 3285 | 2190 |
| Gemma 3 4B | python | 43 | 1/4 | 6289 | 2084 | 1294 |
| Qwen 2.5 7B | expr-v5 | 17 | 0/4 | 10649 | 965 | 644 |
| Qwen 2.5 7B | python | 17 | 2/4 | 4335 | 1260 | 704 |
| Qwen 2.5 7B | expr-v5 | 29 | 0/4 | 10789 | 1102 | 738 |
| Qwen 2.5 7B | python | 29 | 3/4 | 2810 | 708 | 236 |
| Qwen 2.5 7B | expr-v5 | 43 | 0/4 | 10915 | 1220 | 811 |
| Qwen 2.5 7B | python | 43 | 2/4 | 4106 | 1041 | 554 |

The existing paired bootstrap resamples whole tasks, retaining language/seed
pairing (2000 resamples, deterministic analysis seed). The input-plus-output
metric uses the exact sum of actual provider counts, not retokenization. Output-only
TCR intervals are also undefined for every resample.

| Model | v5/Python TCR-total ratio 95% interval | Undefined resamples | Solve-rate difference 95% interval |
|---|---|---:|---|
| Gemma 3 4B | undefined | 2000 | [-0.75, 0.0] |
| Qwen 2.5 7B | undefined | 2000 | [-1.0, -0.16666666666666666] |

**Confidence boundary:** four authored task clusters, three seeds and two small
quantized pretrained models do not support a universal language ranking. NIL has
no trained prior here; the fixed in-context guide is the only adaptation. Familiar
application patterns are not contamination-proof holdouts. Low-temperature repeats
sometimes reproduce identical failures. All 2000 TCR ratio resamples are undefined
per model, so there is no finite savings estimate or confidence gate to pass.
The observed budget failure is clear; its magnitude outside these exact models,
prompts, task domains and budget is unknown. The two model vocabularies are separate.

## Failures and presentation sensitivity

| Model | Language | Attempts | Correct | Parse failures | Semantic/execution failures | Output-limit truncations |
|---|---|---:|---:|---:|---:|---:|
| Gemma 3 4B | expr-v5 | 36 | 0 | 36 | 0 | 18 |
| Gemma 3 4B | python | 28 | 4 | 0 | 24 | 0 |
| Qwen 2.5 7B | expr-v5 | 36 | 0 | 36 | 0 | 0 |
| Qwen 2.5 7B | python | 22 | 7 | 0 | 15 | 0 |

All 72 v5 attempts fail parsing, so their type/backend stages are skipped, not
compiler bugs. Gemma repeats unsupported `expr-v5`-labelled fences; 18 long replies
truncate at 512 tokens, often repeating invented helper signatures. Qwen also emits
plain malformed code: value names in typed signatures, assignment-like syntax,
`len`, `&` and unsupported result annotations. Compiler diagnostics are charged
through subsequent model requests; no formatting/syntax rule was tuned mid-run.

Python failures are genuine contract/runtime failures, including NUL instead of
LF, losing an unterminated last segment, returning input length rather than output
length, binary decoding of decimal text, str/bytes TypeErrors, binary integer output
rather than decimal lines, and wrong report accumulation/formatting. Generic repairs
often repeat the same mistakes. All Python sources parse; 39 attempts fail later.

The frozen extractor permits one unlabelled/nil/python/text code fence, but does
not strip `expr-v5`. This asymmetry in likely model presentation limits conclusions
about the grammar itself. A **post-hoc presentation-only screen** removed just that
label from 18 complete recorded blocks and reran the same reference/native oracles:
**zero became correct**. Some bodies parse but copy the input or emit the wrong
report. No requests, repair feedback, trials or TCR were retroactively changed.
This is not a counterfactual trajectory: different feedback might lead to different
later output, and missing/truncated fences were not repaired. The raw script and
results are archived so this limitation remains visible.

## Audit, corrections and commands

The earlier numerical pilot is incomplete: 119/144 trials, 351 attempts, six solves;
its complete-cell audit rejects it. It says nothing about this v5/Python comparison.
The first application live run was stopped after **14 completed attempts** because
sandbox policy blocked uv's libpython3.12.dylib; a correct Python program was marked
failed. This is an instrumentation defect, not a model error. That entire run is
excluded and archived. The fix grants only the exact pinned interpreter installation
and requires all eight task/language fixtures to pass using it before inference.
Tasks, prompts, seeds and budgets were unchanged; the corrected full run started afresh.
No compiler or runtime bug was found or fixed. The [audit](../../../docs/experiments/V5_GENERATION_AUDIT.md)
and [validation record](../../../docs/validation/V5_GENERATION.md) give scope and test detail.

```text
benchmarks/paired/.venv/bin/python benchmarks/generation/application/run.py --output /tmp/nil-v5-generation-measured
exit 0; preflight passed; audit passed: 48 trials, 122 attempts, REAL MODEL USAGE

benchmarks/paired/.venv/bin/python benchmarks/generation/application/run.py --report-only --output /tmp/nil-v5-generation-measured
exit 0; audit passed: complete paired cells, source hashes, usage arithmetic,
request/response/source integrity, budget limits and nonempty success vectors

benchmarks/paired/.venv/bin/python /tmp/nil-v5-fence-sensitivity.py
exit 0; 18 recorded blocks; 0 correct after label removal; no inference

./scripts/ci.sh
exit 0; 208 tests; zero warnings

benchmarks/paired/.venv/bin/python -m unittest discover -s benchmarks/generation/tests -v
exit 0; 9 numerical harness tests

benchmarks/paired/.venv/bin/python -m unittest discover -s benchmarks/generation/application/tests -v
exit 0; 6 application tests, including evaluator/native O0/O2 and Python

benchmarks/paired/.venv/bin/python benchmarks/generation/application/run.py --mock --output /tmp/nil-v5-generation-stub-final312
exit 0; 24 trials, 54 attempts, STUB ONLY; not model-efficiency data
```

Fresh output directories are required for reproduction. Install exactly the pinned
models, start Ollama separately, and use the guide's command with the committed
definition. No syntax winner, tokenizer/model training, runtime optimization or
next milestone follows automatically from this finding.

## Raw evidence

Valid requests/responses/source, attempt/trial JSONL, configuration, complete analysis,
logs and the presentation screen are retained outside both repositories. The excluded
infrastructure run and synthetic stub occupy separate labelled directories. No binaries
or large machine-specific artifact dump is committed. Archive:
`/Users/ninjacornix/.local/share/nil/benchmarks/archive/v5-generation-2026-10-03.zip`.
SHA-256: `af6cac6da4f2e5740f14681bd2badae3c459fb232703c3695d11b98fdb856b6d`.
All compiler and benchmark commits are local; nothing was pushed or uploaded.
