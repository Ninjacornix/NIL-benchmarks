# Verified expr-v5 application corpus

**25 tasks; 24 verified NIL programs, 25 Python programs, 25 C++ programs.
One task (`env_lookup`) is unsupported in NIL and retained.**
These authored reference solutions are adaptation seeds and source-density samples,
not model outputs. [Before/after density results](../../reports/2026-10-03/V5_GENERALITY.md) do
**not** establish model efficiency: the [generation study](../../reports/2026-10-03/V5_GENERATION.md)
solved 0/24 with NIL versus 11/24 with Python, counting failed attempts and repairs.

## Layout and contracts

- `tasks.json`: frozen statements, inclusion rationales, categories, four fixtures,
  capability status and earlier-generation overlap. Tasks were chosen before counts.
- `goldens.json`: one additional independent literal answer per task, including binary
  boundaries and environment changes; checked against `oracles.py` and every runner.
- `programs/<task>.nil|py|cpp`: self-contained reference solutions. All use an
  input file and output file, return the output byte length, preserve input, and
  emit no extra stdout. Python/C++ `solve` signatures are in the manifest. NIL
  entry `(s,s)` accepts the two file paths. No NIL source exists for unsupported work.
- `oracles.py`: executable byte contracts; `tests/`: literal-golden and deliberate
  wrong-output/input-mutation checks. These finite fixtures are not exhaustive proof.
- `verify.py`: reuses the existing generation `oracle.py`, `application_check.rs`
  in-memory Host and native O0/O2 build path; adds trusted C++/environment runners.
- `driver.cpp`: shared CLI adapter, excluded from all source counts. Python uses
  the existing generation adapter; NIL uses its existing CLI.
- `density.py`: exact raw-source UTF-8 counts, four tokenizer counts and loss lists.
- `export.py`: verified-positive JSONL export; requires no tokenizer/model access.

The authored programs assume successful I/O and valid task input. Numeric domains
are in each statement; NIL still has its documented quota and execution limits.
UTF-8 is tested as bytes, not Unicode-aware case folding or grapheme handling.
The initial density study made no compiler changes. Eleven current references use
the corpus-ranked `parsebuf`, `find` and `equal` additions and require compiler
`abc6afe` or later. Tasks, oracles, goldens and Python/C++ sources remain unchanged
from benchmark commit `9be44d6`; that commit retains the original NIL solutions. Python's first-field reference initially
used `splitlines()`, which violates the LF-only contract for CR; review corrected
it before the final verification. No compiler bug was observed.

## Reproduce (from the compiler checkout, macOS)

Rust and Clang are required; this reuses the existing macOS evaluator/native harness.
Python-only dependencies stay in the benchmark environment:

```sh
uv sync --project benchmarks/paired --locked
benchmarks/paired/.venv/bin/python -m unittest discover -s benchmarks/corpora/application-v5/tests -v
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/verify.py --output /tmp/nil-v5-density/verification.json
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/density.py --verification /tmp/nil-v5-density/verification.json --output /tmp/nil-v5-density/measurement
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/export.py --verification /tmp/nil-v5-density/verification.json --output /tmp/nil-v5-density/adaptation.jsonl
```

Verification performs 120 reference checks, 120 native O0, 120 native O2,
125 Python and 125 C++ checks (610 total). It exits nonzero on failure. Counting and
export refuse stale verification hashes or failed references. Results must remain
outside source checkouts. Density output includes `density.json` and long-form
`tokens.csv`; unsupported NIL counts are blank, never zero. Aggregates pair only
the same 24 supported tasks; unsupported baseline sizes remain in the full table.

The Gemma/Qwen tokenizer vocabularies come from the **exact frozen GGUFs** used in
the generation study, under `~/.ollama/models` (override `--model-home`). See the
report for SHA-256 pins. Missing/mismatched assets fail explicitly; the runner does
not install models or use a substitute. `llama-cpp-python==0.3.16` loads vocabulary
only, skips tensors and never creates an inference context. No Ollama service is
needed or started. Both tiktoken encodings add no BOS/EOS and treat special-looking
text as ordinary source. First use may fetch tiktoken tables and the existing paired
Qwen tokenizer JSON into external caches; no inference occurs. The Qwen JSON has the
same SHA-256 as the official pinned Qwen 7B asset; cross-check all 74 source counts.
Gemma's upstream Hugging Face files are gated; the frozen local GGUF supplies its
real vocabulary. Different tokenizer implementations may differ: pins and probe IDs
are in the measurement record; these are not claimed to be Ollama runtime counters.

## Reuse and license

Tasks, fixtures, oracles, all authored references, and their exported JSONL are MIT
licensed; see [LICENSE](LICENSE). No third-party problem statement was copied.
Retain this license with redistributed data. Dependencies/model vocabularies retain
upstream licenses and are **not** redistributed with the corpus.

JSONL records contain `id`, `profile`, `prompt`, `entry_contract`, `completion`,
`rationale`, `license`, source/verification SHA-256 and `generation_study_overlap`.
Use statements/contracts as inputs and verified completions as targets; fixtures are
oracle data, not part of prompts. Unsupported tasks have no fabricated positive.

24 positives are enough for a few-shot seed and loader smoke test, **not evidence of
successful adaptation or a usable fine-tuning set**. Four overlap the previous
study (`ascii_upper`, `nonempty_lines`, `sum_pairs`, `running_report`). Related
transform/reduction families also overlap structurally: partition by semantic
family, hold out new families and oracle fixtures, and never report training-set
performance as generation improvement. A planning range of 500–2,000 independent
verified tasks, plus repair/negative trajectories and held-out families, could
support an initial adaptation pilot; it is a heuristic, not a model-specific sample
requirement or guarantee. This seed is roughly 20–80x smaller. No model adaptation,
inference or new generation trial was run here.

## Generality findings and measured additions

Bulk canonical integer parsing (`parsebuf`) replaces hand-written decimal row scans,
counting passes and repeated field parsing in six tasks. `find` replaces four
manual delimiter searches; `equal` removes the adjacent-deduplication comparator.
All eleven rewrites pass the same 610 checks. Their forecasts were counted and
committed before implementation; verified counts match exactly. NIL totals fell
32–33%, from 36.7–43.5% above Python to 3.7–8.2% below it across four tokenizers.
Thirteen tasks are unchanged; six to eight still lose to Python. Source density
is not generation efficiency, and no new inference was conducted.

Remaining costs: deduplication repeats slices, hex/CRLF/joins expand into loops,
parallel positional state cannot package multiple results, and records/buffer
builders remain absent. `parsebuf` performs two linear scans and fresh allocation;
it cannot reuse byte storage as an i64 buffer. Environment lookup stays unsupported.
No task, oracle or golden was relaxed, and no grammar/identifier compression was
used. Retain these limits when reusing the 24 verified adaptation positives.
