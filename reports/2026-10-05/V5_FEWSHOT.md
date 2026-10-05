# Verified-example exposure: expr-v5 generation and repairs

**Fixed exposure improved parse-stage counts but did not improve solves. NIL solved 0/24 control and 0/24 few-shot; rerun Python solved 11/24.**

This supports a narrow exposure/imitation effect on accepted syntax, not correctness or model-efficiency improvement. Exact example copying does not demonstrate grammar generalization to a new task. The stronger claim that familiarity explains zero solves, or that fine-tuning fixes them, remains untested.

This is failure-inclusive model usage, not source density or runtime performance.
No compiler, runtime, grammar, profile, corpus, task, oracle, golden, baseline source,
or repair feedback changed. No training or additional models were used. Nothing
was pushed. The earlier study's 0/24 NIL versus 11/24 Python remains a separate
historical result; the tables below use the rerun common Python baseline.

## Preregistration and exactly what changed

[Fixed rule](../../generation/application/fewshot/experiment.json) committed as
benchmarks `3883b98` and main `710331e` before inference. Runner committed as
benchmarks `4cde3c2`, main `76278ad`; these revisions precede all model requests.
The frozen control was byte-tested against the pre-study runner. **It already had
a generic copy-file example.** Treatment adds four verified task/program pairs
before the evaluated task; the reference and copy example are retained. This is
added exposure, not a no-example-versus-example experiment.

Eligible original authored tasks: supported, adaptation_overlap=false, excluding
reverse-case `ascii_lower` and already-shown `copy_file`, with only intrinsic names
present in the frozen reference. In fixed byte-transform/numeric-buffer/line/
format categories, choose first lexical ID: invert_bytes, histogram_digits,
count_newlines, hex_encode. Same four in same order for every task/model/seed.
No test inputs/goldens shown, no evaluated solutions or per-task reselection.
The selected sources pass 20 reference and 40 native O0/O2 checks, including their
unchanged corpus goldens; hashes are in the definition and config.

Frozen four tasks: ascii_upper, nonempty_lines, sum_pairs, running_report.
Two exact quantized model digests, seeds 17/29/43, temperature 0.2, context 8192,
three attempts, 512 output/request, 1536 output/trial; same generic repair feedback,
source extraction, bounded reference (100000 steps/256 frames), native O0/O2 and
byte-exact file/effect oracle. Native output must match reference and all four
frozen oracle inputs, not merely output length. All fixture preflights passed.

Fixed schedule per model: original NIL/Python control, then NIL-only few-shot.
Python is rerun once as the common baseline because its prompt is unchanged.
No smoke inference, automatic retry, model substitution or prompt tuning. Both
conditions ran in this session on this machine; serial order/cache state remains
a possible nuisance factor. Missing usage stays unknown; zero solves means TCR
undefined, not zero. All repairs and full repeated prompt histories are charged.


## Aggregate solves and failure-inclusive token usage

| Model / arm | Solved / trials | Input | Output | Repair output | Output TCR | Total TCR |
|---|---|---|---|---|---|---|
| gemma3 / control | 0/12 | 40,056 | 9,855 | 6,570 | undefined | undefined |
| gemma3 / Python common baseline | 4/12 | 17,496 | 5,996 | 3,610 | 1,499.0 | 5,873.0 |
| qwen2.5 / control | 0/12 | 32,353 | 3,287 | 2,193 | undefined | undefined |
| qwen2.5 / Python common baseline | 7/12 | 11,251 | 3,009 | 1,494 | 429.9 | 2,037.1 |
| gemma3 / fewshot | 0/12 | 52,047 | 2,286 | 1,524 | undefined | undefined |
| qwen2.5 / fewshot | 0/12 | 54,162 | 8,606 | 5,592 | undefined | undefined |

Input is the sum of provider `prompt_eval_count` across every request; output is `eval_count`, including fences/prose/truncated or incorrect answers. Examples and history cost input on repairs too. Repair output is a subset of output, not added twice. Source bytes are not substituted for model tokens. Separately exposed reasoning outside provider usage remains unknown; no thinking-token estimate is invented. Python is a common rerun baseline, not a second treatment condition.

Across both models (descriptive pooling only):

| Arm | Solves /24 | Input | Output | Repair output | Output TCR | Total TCR |
|---|---|---|---|---|---|---|
| NIL control | 0 | 72,409 | 13,142 | 8,763 | undefined | undefined |
| NIL few-shot | 0 | 106,209 | 10,892 | 7,116 | undefined | undefined |
| Python baseline | 11 | 28,747 | 9,005 | 5,104 | 818.6 | 3,432.0 |

Failure-inclusive total input+output rises **85,551 → 117,101 (+36.9%)**.
Per model: Gemma **49,911 → 54,333 (+8.9%)**; Qwen **35,640 → 62,768 (+76.1%)**.
All 18 compiled few-shot attempts exactly copy count_newlines for the wrong task;
there is no correctness transfer. Both NIL output/total TCRs remain undefined.
The control rerun reproduces the historical solve counts and token totals exactly.

## Primary measurement: validity and failure modes

The frozen oracle combines wrong bytes/return values, unexpected effects and execution failures as semantic_or_execution; these counts cannot separate runtime exceptions from wrong answers. No such distinction is invented.

Stage passes are cumulative, not exclusive. Type/backend stage may be unreached after parsing fails; unknown is not a failed typecheck. Python has no static typecheck. Outcomes are exclusive last-stage categories per attempted candidate.

| Model / arm | Attempts | Parse pass | Typecheck pass | Compile pass | Terminal outcomes |
|---|---|---|---|---|---|
| gemma3 / control | 36 | 0 | 0 | 0 | {"parse": 36} |
| gemma3 / Python common baseline | 28 | 28 | N/A | 28 | {"correct": 4, "semantic_or_execution": 24} |
| qwen2.5 / control | 36 | 0 | 0 | 0 | {"parse": 36} |
| qwen2.5 / Python common baseline | 22 | 22 | N/A | 22 | {"correct": 7, "semantic_or_execution": 15} |
| gemma3 / fewshot | 36 | 36 | 18 | 18 | {"semantic_or_execution": 18, "type": 18} |
| qwen2.5 / fewshot | 36 | 17 | 0 | 0 | {"parse": 19, "type": 17} |

First-attempt stages (same 12-trial denominator per model/arm):

| Model / arm | Trials | Parse pass | Typecheck pass | Compile pass | Solved |
|---|---|---|---|---|---|
| gemma3 / control | 12 | 0 | 0 | 0 | 0 |
| gemma3 / Python common baseline | 12 | 12 | N/A | 12 | 4 |
| qwen2.5 / control | 12 | 0 | 0 | 0 | 0 |
| qwen2.5 / Python common baseline | 12 | 12 | N/A | 12 | 7 |
| gemma3 / fewshot | 12 | 12 | 6 | 6 | 0 |
| qwen2.5 / fewshot | 12 | 7 | 0 | 0 | 0 |

Final trial outcomes after repair budget:

| Model / arm | Final outcomes |
|---|---|
| gemma3 / control | {"parse": 12} |
| gemma3 / Python common baseline | {"correct": 4, "semantic_or_execution": 8} |
| qwen2.5 / control | {"parse": 12} |
| qwen2.5 / Python common baseline | {"correct": 7, "semantic_or_execution": 5} |
| gemma3 / fewshot | {"semantic_or_execution": 6, "type": 6} |
| qwen2.5 / fewshot | {"parse": 6, "type": 6} |

### Frozen presentation-policy limitation

| Model / arm | Complete fences with unsupported labels | Labels |
|---|---|---|
| gemma3 / control | 18 | {"expr-v5": 18} |
| gemma3 / Python common baseline | 0 | {} |
| qwen2.5 / control | 0 | {} |
| qwen2.5 / Python common baseline | 0 | {} |
| gemma3 / fewshot | 0 | {} |
| qwen2.5 / fewshot | 0 | {} |

The extractor accepts plain source or one fence labelled nil/python/text/empty.
It does not strip expr-v5 or other labels. These complete unsupported-label fences
remain in candidate source and fail Parse. Counts above are descriptive surface
inspection, **not regraded correctness**: no fence removal, extra execution,
post-hoc successful answer or corrected-token claim enters the result. This can
obscure grammar competence, so “failed to parse” alone cannot prove unfamiliarity
is or is not the cause. Truncated/multiple fences are not included in this count.


### Exact example copying (descriptive, not a correctness regrade)

| Model / arm | Exact selected-source copies | Example IDs |
|---|---|---|
| gemma3 / control | 0 | {} |
| gemma3 / Python common baseline | 0 | {} |
| qwen2.5 / control | 0 | {} |
| qwen2.5 / Python common baseline | 0 | {} |
| gemma3 / fewshot | 18 | {"count_newlines": 18} |
| qwen2.5 / fewshot | 0 | {} |

Only leading/trailing whitespace is ignored. Other rewrites are not labelled copies. Copying a valid example for the wrong task can pass every static stage without demonstrating task transfer. These counts were inspected after the fixed run; they changed no prompts, selection, repairs or acceptance.

## Per-task usage, solves and stages

| Task | Model / arm | Solves /3 | Input | Output | Repair output | Output TCR | Total TCR | Attempts / parse / type / compile | Outcomes |
|---|---|---|---|---|---|---|---|---|---|
| ascii_upper | gemma3 / control | 0 | 7,677 | 207 | 138 | undefined | undefined | 9/0/0/0 | {"parse": 9} |
| ascii_upper | gemma3 / Python common baseline | 3 | 1,164 | 411 | 0 | 137.0 | 525.0 | 3/3/0/3 | {"correct": 3} |
| ascii_upper | qwen2.5 / control | 0 | 7,845 | 690 | 460 | undefined | undefined | 9/0/0/0 | {"parse": 9} |
| ascii_upper | qwen2.5 / Python common baseline | 3 | 1,140 | 362 | 0 | 120.7 | 500.7 | 3/3/0/3 | {"correct": 3} |
| nonempty_lines | gemma3 / control | 0 | 12,030 | 4,608 | 3,072 | undefined | undefined | 9/0/0/0 | {"parse": 9} |
| nonempty_lines | gemma3 / Python common baseline | 0 | 5,904 | 1,998 | 1,332 | undefined | undefined | 9/9/0/9 | {"semantic_or_execution": 9} |
| nonempty_lines | qwen2.5 / control | 0 | 8,269 | 1,017 | 682 | undefined | undefined | 9/0/0/0 | {"parse": 9} |
| nonempty_lines | qwen2.5 / Python common baseline | 0 | 4,946 | 1,186 | 840 | undefined | undefined | 9/9/0/9 | {"semantic_or_execution": 9} |
| sum_pairs | gemma3 / control | 0 | 12,321 | 4,608 | 3,072 | undefined | undefined | 9/0/0/0 | {"parse": 9} |
| sum_pairs | gemma3 / Python common baseline | 1 | 4,343 | 1,437 | 846 | 1,437.0 | 5,780.0 | 7/7/0/7 | {"correct": 1, "semantic_or_execution": 6} |
| sum_pairs | qwen2.5 / control | 0 | 8,244 | 875 | 584 | undefined | undefined | 9/0/0/0 | {"parse": 9} |
| sum_pairs | qwen2.5 / Python common baseline | 3 | 1,212 | 369 | 0 | 123.0 | 527.0 | 3/3/0/3 | {"correct": 3} |
| running_report | gemma3 / control | 0 | 8,028 | 432 | 288 | undefined | undefined | 9/0/0/0 | {"parse": 9} |
| running_report | gemma3 / Python common baseline | 0 | 6,085 | 2,150 | 1,432 | undefined | undefined | 9/9/0/9 | {"semantic_or_execution": 9} |
| running_report | qwen2.5 / control | 0 | 7,995 | 705 | 467 | undefined | undefined | 9/0/0/0 | {"parse": 9} |
| running_report | qwen2.5 / Python common baseline | 1 | 3,953 | 1,092 | 654 | 1,092.0 | 5,045.0 | 7/7/0/7 | {"correct": 1, "semantic_or_execution": 6} |
| ascii_upper | gemma3 / fewshot | 0 | 12,915 | 612 | 408 | undefined | undefined | 9/9/9/9 | {"semantic_or_execution": 9} |
| ascii_upper | qwen2.5 / fewshot | 0 | 11,699 | 588 | 402 | undefined | undefined | 9/3/0/0 | {"parse": 6, "type": 3} |
| nonempty_lines | gemma3 / fewshot | 0 | 12,978 | 531 | 354 | undefined | undefined | 9/9/0/0 | {"type": 9} |
| nonempty_lines | qwen2.5 / fewshot | 0 | 12,231 | 1,008 | 668 | undefined | undefined | 9/4/0/0 | {"parse": 5, "type": 4} |
| sum_pairs | gemma3 / fewshot | 0 | 13,113 | 531 | 354 | undefined | undefined | 9/9/0/0 | {"type": 9} |
| sum_pairs | qwen2.5 / fewshot | 0 | 14,670 | 2,559 | 1,450 | undefined | undefined | 9/7/0/0 | {"parse": 2, "type": 7} |
| running_report | gemma3 / fewshot | 0 | 13,041 | 612 | 408 | undefined | undefined | 9/9/9/9 | {"semantic_or_execution": 9} |
| running_report | qwen2.5 / fewshot | 0 | 15,562 | 4,451 | 3,072 | undefined | undefined | 9/3/0/0 | {"parse": 6, "type": 3} |

## Repeat variation and confidence limits

| Model / arm | Seed | Solves /4 | Input | Output | Repair output |
|---|---|---|---|---|---|
| gemma3 / control | 17 | 0 | 13,352 | 3,285 | 2,190 |
| gemma3 / Python common baseline | 17 | 2 | 4,859 | 1,761 | 960 |
| qwen2.5 / control | 17 | 0 | 10,649 | 965 | 644 |
| qwen2.5 / Python common baseline | 17 | 2 | 4,335 | 1,260 | 704 |
| gemma3 / control | 29 | 0 | 13,352 | 3,285 | 2,190 |
| gemma3 / Python common baseline | 29 | 1 | 6,348 | 2,151 | 1,356 |
| qwen2.5 / control | 29 | 0 | 10,789 | 1,102 | 738 |
| qwen2.5 / Python common baseline | 29 | 3 | 2,810 | 708 | 236 |
| gemma3 / control | 43 | 0 | 13,352 | 3,285 | 2,190 |
| gemma3 / Python common baseline | 43 | 1 | 6,289 | 2,084 | 1,294 |
| qwen2.5 / control | 43 | 0 | 10,915 | 1,220 | 811 |
| qwen2.5 / Python common baseline | 43 | 2 | 4,106 | 1,041 | 554 |
| gemma3 / fewshot | 17 | 0 | 17,349 | 762 | 508 |
| qwen2.5 / fewshot | 17 | 0 | 18,558 | 3,276 | 2,080 |
| gemma3 / fewshot | 29 | 0 | 17,349 | 762 | 508 |
| qwen2.5 / fewshot | 29 | 0 | 18,527 | 3,085 | 1,912 |
| gemma3 / fewshot | 43 | 0 | 17,349 | 762 | 508 |
| qwen2.5 / fewshot | 43 | 0 | 17,077 | 2,245 | 1,600 |

Across-seed range and sample standard deviation (three repeats of four tasks):

| Model / arm | Metric | Min–max | Sample SD |
|---|---|---|---|
| gemma3 / control | solved | 0–0 | 0.00 |
| gemma3 / control | input_tokens | 13352–13352 | 0.00 |
| gemma3 / control | output_tokens | 3285–3285 | 0.00 |
| gemma3 / Python common baseline | solved | 1–2 | 0.58 |
| gemma3 / Python common baseline | input_tokens | 4859–6348 | 843.16 |
| gemma3 / Python common baseline | output_tokens | 1761–2151 | 208.53 |
| qwen2.5 / control | solved | 0–0 | 0.00 |
| qwen2.5 / control | input_tokens | 10649–10915 | 133.06 |
| qwen2.5 / control | output_tokens | 965–1220 | 127.62 |
| qwen2.5 / Python common baseline | solved | 2–3 | 0.58 |
| qwen2.5 / Python common baseline | input_tokens | 2810–4335 | 822.36 |
| qwen2.5 / Python common baseline | output_tokens | 708–1260 | 277.96 |
| gemma3 / fewshot | solved | 0–0 | 0.00 |
| gemma3 / fewshot | input_tokens | 17349–17349 | 0.00 |
| gemma3 / fewshot | output_tokens | 762–762 | 0.00 |
| qwen2.5 / fewshot | solved | 0–0 | 0.00 |
| qwen2.5 / fewshot | input_tokens | 17077–18558 | 846.25 |
| qwen2.5 / fewshot | output_tokens | 2245–3276 | 548.49 |

Paired bootstrap resamples four whole tasks, retaining paired seeds (2000 samples):

| Model | Solve-rate difference 95% | Output TCR ratio 95% | Total TCR ratio 95% | Undefined output/total TCR resamples |
|---|---|---|---|---|
| qwen2.5:7b-instruct | [0.0, 0.0] | None | None | 2000/2000 |
| gemma3:4b | [0.0, 0.0] | None | None | 2000/2000 |

Four authored tasks, three seeds, two small quantized models and one nonrandom
example-selection rule are not an independent representative language benchmark.
The four examples are drawn from related application tasks, though not evaluated
answers; contamination/familiarity with conventional tasks is uncontrolled.
Serial condition order and cached prefixes, short generation budget, quantization,
fixed repair/extraction policy and prompt content/length jointly constrain inference.
No training, grammar-constrained decoding, other models or other example counts
were tested. The all-zero solve-difference bootstrap [0,0] is degenerate; it does not prove
zero population effect or success probability. Bootstrap bounds with four clusters are descriptive and weak;
undefined TCR samples cannot select an efficiency winner. Even improved parse/solve
rates would not establish a general token-efficiency advantage. A null result
would only reject the adequacy of this exposure rule, not all adaptation.


## Reproduction, environment and receipts

| Model | Pinned digest | Quantization |
|---|---|---|
| gemma3:4b | a2af6cc3eb7fa8be8504abaf9b04e88f17a119ec3f04a3addf55f92841195f5a | Q4_K_M |
| qwen2.5:7b-instruct | 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e | Q4_K_M |

Apple M2 arm64 / macOS 27, Ollama 0.9.0, benchmark Python 3.12.11. Model/templates
and complete request options are in [configs](V5_FEWSHOT_CONFIGS.json).
[Analysis](V5_FEWSHOT_ANALYSIS.json), [all attempts](V5_FEWSHOT_ATTEMPTS.jsonl),
[all trials](V5_FEWSHOT_TRIALS.jsonl), [example preflight](V5_FEWSHOT_EXAMPLE_PREFLIGHT.json)
and [command receipts](V5_FEWSHOT_RECEIPTS.txt) retain failures and usage.
Raw prompts/responses/candidates are archived at `/Users/ninjacornix/.local/share/nil/benchmarks/archive/v5-fewshot-2026-10-05.tar.gz`, SHA-256 `4970425f8ea649ca0e483f8d2bdfda88dd2be5bc6909d503e28277330e4a91de`.
No model blobs or executables are archived. Preserve the frozen source checkout
when rerunning the hash audit; current measured source files are unchanged.

```sh
OLLAMA_HOST=127.0.0.1:11434 ollama serve
benchmarks/paired/.venv/bin/python benchmarks/generation/application/fewshot/run.py --output /external/path/nil-exposure-NEW
benchmarks/paired/.venv/bin/python benchmarks/generation/application/fewshot/run.py --report-only --output /external/path/nil-exposure-NEW
./scripts/ci.sh
```

The stub run completed 72 synthetic trials /162 attempts through real oracles;
its usage is never pooled with model data. Its first dry run exposed an existing
report assumption that every arm contains Python; NIL-only arms now skip that
within-arm bootstrap, with condition pairing in the adapter. No model run was
discarded or rerun because of that dry-run-only reporting correction.
Six existing application-harness tests and three new exposure tests passed.
CI passes 368 tests, zero warnings, with compiler/runtime/corpus unchanged.

