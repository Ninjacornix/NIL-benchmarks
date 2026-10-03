# expr-v5 / Python application generation

This extends the existing generation harness: it reuses its Ollama transport,
failure-inclusive summaries, paired task bootstrap and helper/provenance utilities.
The scalar-only original oracle cannot accept byte paths or check file effects;
this adapter adds those operations without changing the compiler or experiment
metric. See the [audit](../../../docs/experiments/V5_GENERATION_AUDIT.md).

## Frozen experiment

`experiment.json`, `tasks.json` and the two `*-reference.txt` files are committed
before any model-generation request. Four contracts cover ASCII transformation,
nonempty-line filtering, comma-separated integer parsing and report accumulation.
Each has four byte-exact oracle inputs, including empty files, CR/unterminated
lines, negative integers and binary data where the contract allows it. These are
small authored application tasks, not a random or contamination-proof holdout.
No tasks, prompts, budgets or syntax are tuned after partial results.

Two frozen local models (Gemma 3 4B / Qwen 2.5 7B Instruct), three seeds (17/29/43),
two languages: **48 trials**. Temperature 0.2, context 8192, three attempts,
512 generated tokens/request, 1536 cumulative output tokens/trial. Languages
rotate by task/seed; models run sequentially. The larger budget than the old
numerical pilot is fixed before inference and common to both languages.

Both prompts use a language reference and one generic copy-file example, followed
by the identical task and entry/effect contract. Different reference lengths are
charged as input, not padded away. No solutions or hidden inputs enter requests.
Python may use its standard library; NIL uses its existing core/intrinsics. This
measures the available pretrained models with fixed in-context NIL instruction,
not a NIL-trained model or syntax under a hypothetical tokenizer.

Initial and repair requests/responses are retained. Repairs include actual parse/
type/compiler diagnostics (capped at 800 characters) or generic semantic feedback,
never failing inputs, expected bytes or task solutions. Full conversation history
is charged again via provider input usage. Stop at first correctness or the common
budget; no infrastructure retries or silent substitutions. Usage missing from a
response stays unknown and invalidates exact TCR. Separately exposed thinking is
retained but has no invented token cost. All provider-reported output is charged,
including fences/prose and failed candidates; extracted source length is separate.

## Correctness and execution boundary

Every task takes input/output paths, writes exact output, returns its byte length,
emits no extra stdout and leaves the input unchanged. The benchmark-only Rust
helper uses the trusted v5 reference evaluator with an in-memory Host, 100000 steps
and 256 frames. NIL must pass reference plus bounded native **O0 and O2** for all
four inputs. Python executes its `solve(input_path, output_path)` in Python 3.12
with the identical contract. No acceptance through merely matching file length.

Before any request, all eight handwritten task/language fixtures must pass using
the same pinned Python 3.12 interpreter as inference. A preflight failure aborts
before model access. Generated host processes use macOS sandbox-exec: no network, no writes outside
the case directory, no reads from user data or other temporary fixtures. System
loader/runtime reads and the exact pinned Python installation are permitted. Reference answer artifacts are deleted before
native execution. This requires macOS; other platforms must port and validate
this boundary before running generated host code. NIL's runtime itself remains
explicitly unsandboxed. Each execution has a five-second timeout and compilation
60 seconds. Python has no instruction counter but uses the same timeout; these
small contracts fit the shared requested step/depth limit. No runtime speed claim.

`solutions/` validates oracles and supplies stub fixtures only; it is never used
for real model requests. The stub intentionally fails first attempts and every
sum_pairs trial to exercise repairs and failure-inclusive accounting. Its usage
is synthetic and must never appear as model-efficiency evidence.

## Reproduce

From the compiler checkout, initialize the benchmarks submodule. Python 3.12,
pinned offline Rust toolchain, Clang and sandbox-exec are required. All raw outputs
must live outside both repositories. Start Ollama separately and install the exact
model digests from experiment.json; the runner rejects missing or different tags.

```sh
benchmarks/paired/.venv/bin/python -m unittest discover -s benchmarks/generation/application/tests -v
benchmarks/paired/.venv/bin/python benchmarks/generation/application/run.py --mock --output /tmp/nil-v5-stub-NEW
# Actual inference; no model installation/substitution happens automatically:
OLLAMA_HOST=127.0.0.1:11434 ollama serve
benchmarks/paired/.venv/bin/python benchmarks/generation/application/run.py --output /external/path/nil-v5-generation-NEW
benchmarks/paired/.venv/bin/python benchmarks/generation/application/run.py --report-only --output /external/path/nil-v5-generation-NEW
```

Choose fresh output paths. The default definition runs both models, all tasks and
seeds; there is no task-selection flag to cherry-pick measured cells. Config records
model/template metadata, server version, source hashes and compiler/suite revisions.
Audits reject incomplete matrices, bad usage arithmetic, changed measured sources,
continuation after solves, or success without all reference/native vectors.

## Metrics and limits

For each task/model/language and in aggregate, report input, output and repair
output totals, solved/trials, first-pass rate, and failure-inclusive
`TCR-out = all output tokens / solves` and
`TCR-total = (all input + all output tokens) / solves`. Zero solves are undefined
(null), never zero-cost. Unsolved trials retain every failed attempt's cost.
Report per-seed solves and costs, min/max across repeats and task-cluster paired
bootstrap intervals (2000 resamples); undefined resamples cannot select a winner.
Four clusters / three seeds provide weak generalization evidence. Do not treat
source characters, one successful candidate or a stub as model-token savings.
