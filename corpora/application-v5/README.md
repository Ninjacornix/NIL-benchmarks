# Verified expr-v5 application corpus

## Latest algorithmic result

Sort and snapshot each improve eleven external references against unchanged
oracles; 2400 checks pass and the original 610 pass separately. **NIL still costs
4.3–12.3% more tokens than Python externally, 1.2–8.1% more combined.** Joint
553/401/398/388 token savings (Gemma/Qwen/cl100k/o200k) match preregistration;
cl100k's external surplus drops from 650 to 252. All original NIL and baseline
sources remain unchanged. 56 verified programs/exports, 19 unsupported remain.
[All three cuts, per-task counts and category movement](../../reports/2026-10-03/V5_ALGORITHMS.md).

`algorithms_forecast.py` freezes the before-implementation proposals against
920e510; `algorithms_results.py` recounts the committed intermediate sort-only
sources and compares verified final counts. `attribution.py` recognizes each's
three regions while preserving legacy category accounting. [Retained task review](ALGORITHMS_ATTEMPTS.md).
Source density is not model efficiency: generation remains NIL 0/24 vs Python
11/24. These 56 examples are adaptation seeds, not fine-tuning scale.

## Previous keyed-data result

The corpus now has **56 verified NIL positives and 19 unsupported tasks** (18
external). ETL joins the supported set; grade_school uses maps for duplicate names.
Contracts, oracles, goldens, original NIL references and all existing baseline
sources remain unchanged and hash-locked. SUPPORT.json carries the new status.
2,400 execution checks pass, including the original 610 separately.

**The external Python density gap persists: 12.0–21.1% more NIL tokens externally,
6.9–14.6% more combined**, versus 42.2–46.0% fewer than C++ externally. The original
24 counts are unchanged. Grade_school improves 10–11%, but newly supported ETL
costs more than twice Python, so expanding support worsens the aggregate.
[Before/after, three cuts and every per-task count](../../reports/2026-10-03/V5_KEYED_DATA.md).
Source density is not model efficiency: generation remains unfavourable (0/24
versus 11/24), with no new inference. 56 exported seeds are not adaptation scale.
[Remaining task attempts and limits](KEYED_ATTEMPTS.md).

The sections below preserve the historical external expansion and original
sequence-operation studies, before this keyed extension.


**75 retained tasks: 25 self-authored + 50 externally derived; 55 verified NIL
programs and 20 unsupported tasks (19 external, one original).**

**The Python density advantage reverses externally:** NIL costs 10.6–19.9% more
source tokens on the 31 supported external properties, and 5.8–13.6% more on all
55 paired tasks. The original 24 still cost 3.7–8.2% fewer. See [three-cut results](../../reports/2026-10-03/V5_EXTERNAL_DENSITY.md).
These authored references are adaptation seeds, not model outputs. Source density
does not establish model efficiency; the [generation study](../../reports/2026-10-03/V5_GENERATION.md)
solved 0/24 NIL versus 11/24 Python, including failures and repairs.

External tasks are the first 50 alphabetical Exercism canonical specifications at
a pinned revision, scoped to their first declared property. This is not full-API
coverage or a representative random sample. Some unsupported tasks need missing
primitives; others lack a serialized adapter and are not proven unexpressible.
[Selection, contracts, licensing and limitations](external/README.md).

## Layout and contracts

- `tasks.json`: unchanged original statements, inclusion rationales, categories, four fixtures,
  capability status and earlier-generation overlap. Tasks were chosen before counts.
- `external/`: 50 pinned specifications, MIT notice, selection, adapted contracts,
  upstream expected values and separate goldens. `PROVENANCE.json` records origin
  and license for every task; `GENERALITY_GAPS.json` gives blocked counts.
- `goldens.json`: unchanged original independent literal answers, including binary
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

Verification performs 474 reference checks, 474 native O0, 474 native O2,
479 Python and 479 C++ checks (2,380 total). `verify.py --group original` retains
the original 610-check path; `--group external` selects new work only. It exits nonzero on failure. Counting and
export refuse stale verification hashes or failed references. Results must remain
outside source checkouts. Density output includes `density.json` and long-form
`tokens.csv`; unsupported NIL counts are blank, never zero. Aggregates pair only
the same 55 supported tasks; all three cuts are reported separately; unsupported baseline sizes remain in the full table.

The Gemma/Qwen tokenizer vocabularies come from the **exact frozen GGUFs** used in
the generation study, under `~/.ollama/models` (override `--model-home`). See the
report for SHA-256 pins. Missing/mismatched assets fail explicitly; the runner does
not install models or use a substitute. `llama-cpp-python==0.3.16` loads vocabulary
only, skips tensors and never creates an inference context. No Ollama service is
needed or started. Both tiktoken encodings add no BOS/EOS and treat special-looking
text as ordinary source. First use may fetch tiktoken tables and the existing paired
Qwen tokenizer JSON into external caches; no inference occurs. The Qwen JSON has the
same SHA-256 as the official pinned Qwen 7B asset; cross-check all 167 verified source counts.
Gemma's upstream Hugging Face files are gated; the frozen local GGUF supplies its
real vocabulary. Different tokenizer implementations may differ: pins and probe IDs
are in the measurement record; these are not claimed to be Ollama runtime counters.

## Reuse and license

Authored tasks/references and code are MIT licensed; see [LICENSE](LICENSE).
External statements and fixtures derive from MIT-licensed Exercism specifications;
also retain [EXERCISM_LICENSE](external/EXERCISM_LICENSE) and per-task provenance
when redistributing. Original tasks remain separately identified. Dependencies/model vocabularies retain
upstream licenses and are **not** redistributed with the corpus.

JSONL records contain `id`, `profile`, `prompt`, `entry_contract`, `completion`,
`rationale`, `license`, source/verification SHA-256 and `generation_study_overlap`.
Use statements/contracts as inputs and verified completions as targets; fixtures are
oracle data, not part of prompts. Unsupported tasks have no fabricated positive.

55 positives are enough for a few-shot seed and loader smoke test, **not evidence of
successful adaptation or a usable fine-tuning set**. Four overlap the previous
study (`ascii_upper`, `nonempty_lines`, `sum_pairs`, `running_report`). Related
transform/reduction families also overlap structurally: partition by semantic
family, hold out new families and oracle fixtures, and never report training-set
performance as generation improvement. A planning range of 500–2,000 independent
verified tasks, plus repair/negative trajectories and held-out families, could
support an initial adaptation pilot; it is a heuristic, not a model-specific sample
requirement or guarantee. This seed is roughly 9–36x smaller. No model adaptation,
inference or new generation trial was run here.

## Original cohort: measured generality additions

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

## Expanded evidence and remaining gaps

The original generality-addition history above concerns the unchanged 24-task
cohort. The external audit adds 31 positives and retains 19 unsupported properties;
the total is 55 verified NIL references, 56 Python and 56 C++ references (the extra
baseline task is original environment lookup). Finite external oracles are pinned
upstream expected-value maps, not general algorithms for unknown inputs. Goldens
remain independent of reference code, and original files are protected by hash locks.

[Current gaps and counts](GENERALITY_GAPS.json) include floats, integer widths,
Unicode, higher-order callbacks, concurrency, entropy/reactive integration, and
unimplemented map/tree/dictionary/calendar/multi-file adapters. Record these as
findings; no compiler feature was added in this expansion. New references and tasks
were frozen before token counting. No task, oracle, golden or reference was changed
after observing counts. JSONL now exports 55 verified positives with provenance
for external tasks; the original metadata has the separate PROVENANCE.json overlay.

## Keyed-data token attribution snapshot

The keyed-data snapshot has 56 verified NIL programs, 32 external pairs and 19
unsupported tasks. The attribution audit leaves every program and frozen oracle
unchanged: 2,400 checks pass, with the original 610 separately reconfirmed.
`attribution.py` reconstructs every source token under the four pinned vocabularies
and writes a full byte-offset ledger plus a compact exact-fraction summary.
`remediation.py` forecasts two **unimplemented, invalid** syntax proposals outside
the corpus; these are not adaptation positives. See
[the decision and rankings](../../reports/2026-10-03/V5_ATTRIBUTION_PLAN.md) and
[unchanged three-cut measurements](../../reports/2026-10-03/V5_ATTRIBUTION_RESULTS.md).
The Python density gap remains; source density does not establish model efficiency.

Keep the generated full ledger outside the checkout. Reproduce with the report's
commands; run `python -m unittest discover -s corpora/application-v5/tests` using
the paired Python environment from this submodule root. No Rust dependencies or
model inference are needed.

## Numeric expansion (ADR 027)

Four previously unsupported frozen external contracts now have verified solutions:
Armstrong Numbers (u128 with accumulation overflow detection), Grains (u64),
Darts (binary64 squared-distance comparisons), and Complex Numbers' selected
real-part property (not the full complex API). There are **60 verified NIL
programs**, 36 external, with 15 unsupported tasks remaining (14 external).
All original contracts, fixtures, goldens and existing baseline sources remain
unchanged; new baselines fill previously absent paths. Numeric JSON adapters cover
the pinned minified contracts; they are not general JSON parsers. No float/unsigned
collections, records or complex type were introduced. Each task's upstream MIT
provenance and corpus license continue to apply. Export produces 60 adaptation
seeds, still far below a credible training set. No inference or training occurred.

## Records (ADR 028): current corpus state

Go counting now has verified expr-v5, Python and C++ references under its existing
MIT upstream provenance and the corpus's MIT licence. Compact JSON input/output
adapters implement the frozen contract; NIL uses fixed-point flood-fill, baselines
use queue/set traversal. No original task, oracle, golden, baseline or old NIL
source changed. **75 tasks, 61 verified NIL programs (37 external), 14 unsupported
(13 external)**; export emits **61 JSONL positives** in the existing reusable format.
This remains a small, nonrandom partial-API seed, not a sufficient training dataset.

All 2,625 checks pass, with the original 610 separately confirmed. Records unblock
one of five candidates; the gap catalogue distinguishes unavailable types from
unimplemented adapters. The density gap **worsens**: external +12.9–23.3% against
Python, combined +8.0–16.8%, while the old 60 sources/counts are unchanged. Go loses
to both baselines under all four vocabularies. No model inference occurred, and
source density does not overturn the unfavourable generation study. See
[the record report](../../reports/2026-10-04/V5_RECORDS.md) for every task's counts,
bytes/characters, refreshed attribution, provenance and reproduction commands.
