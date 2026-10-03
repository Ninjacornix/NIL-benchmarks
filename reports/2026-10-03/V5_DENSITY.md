# Expr-v5 application source density — 2026-10-03

**Expr-v5 uses 36.7–43.5% more source tokens than Python on the 24 supported tasks. It uses 41.4–44.8% fewer than C++, including headers and file-I/O framing. This is an unfavourable density result against Python.**

**Source density is NOT the project's thesis: total tokens to a correct program, including failed attempts and repairs, is. Density is a representation-compression prerequisite, not evidence of model efficiency. The [generation study](V5_GENERATION.md) was unfavourable: NIL solved 0/24 versus Python 11/24. Nothing here reverses that result.**

## Task selection and verification

[Frozen corpus](../../corpora/application-v5/README.md): 25 tasks, each with a statement and inclusion rationale in `tasks.json`; byte transforms, LF/field processing, decimal formats, output builders, dynamic integer buffers, binary file pipelines, and one missing application capability. No task was dropped after results. `env_lookup` remains unsupported: identical files/arguments with different environment values require different outputs, but the v5 Host has no environment operation. Its Python/C++ references pass. The other 24 NIL references pass the in-memory Host and native O0/O2; all 25 baselines pass.

The original four fixtures per task were frozen before counting. One independent literal golden per task adds checks for CR preservation, binary data, unterminated/empty segments and independently varying environments. Five harness tests check literal outputs, edge policies, rejection of wrong-output/input-mutating references, and refusal of stale/failed verification. This is finite correctness evidence, not exhaustive validation over every input. Four tasks overlap the earlier generation study; they are labelled and must not become adaptation holdouts.

The benchmark compiler revision is `ce7301d`; compiler, runtime, grammar, Cargo manifests/lock, profiles and default are unchanged. Full per-program hashes and verdicts: [verification](V5_CORPUS_VERIFICATION.json). The only reference defect found in review was Python CSV `splitlines()` violating LF-only/CR-preserving semantics; corrected before final verification. No compiler bug was found.

## Accounting and limitations

All source files are hand-authored idiomatic references, not generated trials and not a code-golf competition. Count exact UTF-8 files including whitespace, function declarations, custom helpers, imports/headers and file I/O. Exclude shared CLI drivers in every language. C++ gets its standard library, Python gets its standard library, NIL gets its builtins; this measures the deployed programming interface, not isolated grammar expressiveness. NIL's compact positional state and one-line functions are its normal profile form; baselines use descriptive names and normal formatting. Other equally correct implementations could have different counts. No Rust baseline was added.

C++ framing is substantial on these small tasks, so the C++ advantage must not be generalized to large modules or algorithms after shared-header amortization. Python builtins compress work that NIL spells out. Pair aggregates only on the same 24 tasks: unsupported NIL is missing, not zero. Full tables retain both unsupported-task baseline sizes. Token counts are deterministic for pinned assets; no statistical confidence interval over model generation exists here. Task selection is purposeful, correlated and small, not a random sample of applications. No repairs, prompt/spec tokens, inference, model adaptation or runtime timings were measured.

## Paired aggregate (24 tasks)

| Tokenizer | NIL | Python | C++ | NIL vs Python | NIL vs C++ |
|---|---:|---:|---:|---:|---:|
| gemma3_4b | 3196 | 2227 | 5454 | +43.51% | -41.40% |
| qwen2.5_7b_instruct | 2418 | 1728 | 4235 | +39.93% | -42.90% |
| cl100k_base | 2338 | 1705 | 4217 | +37.13% | -44.56% |
| o200k_base | 2340 | 1712 | 4238 | +36.68% | -44.79% |

| Language | Bytes | Characters | Gemma tokens / 100 bytes | Qwen tokens / 100 bytes |
|---|---:|---:|---:|---:|
| expr-v5 | 4775 | 4775 | 66.93 | 50.64 |
| python | 6746 | 6746 | 33.01 | 25.62 |
| cpp | 17283 | 17283 | 31.56 | 24.50 |

All solution source happens to be ASCII, hence bytes equal characters; binary/UTF-8 inputs remain in the oracles. NIL has fewer characters than Python but more model tokens: character compression is not token compression.

## Every non-win

Counts below list every NIL loss and tie; exact per-language counts are in the next table and [long-form CSV](V5_DENSITY_TOKENS.csv). Win/loss counts are task-level and unweighted; aggregate percentages are ratios of token totals, not averages of percentages.

- **gemma3_4b / python**: 8 wins, 1 ties, 15 losses. Losses: `rot13`, `hex_encode`, `nonempty_lines`, `normalize_crlf`, `first_fields_csv`, `sum_pairs`, `sum_integers`, `min_max`, `dedupe_adjacent_lines`, `number_lines`, `histogram_digits`, `buffer_sum`, `buffer_dot`, `prefix_sums`, `slice_file`. Ties: `reverse_bytes`.
- **gemma3_4b / cpp**: 22 wins, 0 ties, 2 losses. Losses: `min_max`, `dedupe_adjacent_lines`. Ties: none.
- **qwen2.5_7b_instruct / python**: 9 wins, 1 ties, 14 losses. Losses: `hex_encode`, `nonempty_lines`, `normalize_crlf`, `first_fields_csv`, `sum_pairs`, `sum_integers`, `min_max`, `dedupe_adjacent_lines`, `number_lines`, `histogram_digits`, `buffer_sum`, `buffer_dot`, `prefix_sums`, `slice_file`. Ties: `reverse_bytes`.
- **qwen2.5_7b_instruct / cpp**: 22 wins, 0 ties, 2 losses. Losses: `min_max`, `dedupe_adjacent_lines`. Ties: none.
- **cl100k_base / python**: 9 wins, 1 ties, 14 losses. Losses: `hex_encode`, `nonempty_lines`, `normalize_crlf`, `first_fields_csv`, `sum_pairs`, `sum_integers`, `min_max`, `dedupe_adjacent_lines`, `number_lines`, `histogram_digits`, `buffer_sum`, `buffer_dot`, `prefix_sums`, `slice_file`. Ties: `reverse_bytes`.
- **cl100k_base / cpp**: 22 wins, 0 ties, 2 losses. Losses: `min_max`, `dedupe_adjacent_lines`. Ties: none.
- **o200k_base / python**: 10 wins, 0 ties, 14 losses. Losses: `hex_encode`, `nonempty_lines`, `normalize_crlf`, `first_fields_csv`, `sum_pairs`, `sum_integers`, `min_max`, `dedupe_adjacent_lines`, `number_lines`, `histogram_digits`, `buffer_sum`, `buffer_dot`, `prefix_sums`, `slice_file`. Ties: none.
- **o200k_base / cpp**: 22 wins, 0 ties, 2 losses. Losses: `min_max`, `dedupe_adjacent_lines`. Ties: none.

## Per-task, per-language sizes

G = frozen Gemma 3 4B; Q = frozen Qwen 2.5 7B Instruct; C = cl100k_base; O = o200k_base. Full IDs, versions, hashes, probe IDs and source hashes are in [the measurement record](V5_DENSITY.json).

| Task | Language | Bytes | Characters | G | Q | C | O |
|---|---|---:|---:|---:|---:|---:|---:|
| ascii_upper | expr-v5 | 96 | 96 | 75 | 53 | 49 | 48 |
| ascii_upper | python | 235 | 235 | 81 | 64 | 60 | 60 |
| ascii_upper | cpp | 667 | 667 | 213 | 167 | 166 | 166 |
| ascii_lower | expr-v5 | 95 | 95 | 74 | 52 | 49 | 48 |
| ascii_lower | python | 234 | 234 | 80 | 63 | 60 | 60 |
| ascii_lower | cpp | 667 | 667 | 213 | 167 | 166 | 166 |
| rot13 | expr-v5 | 170 | 170 | 133 | 98 | 86 | 85 |
| rot13 | python | 355 | 355 | 124 | 107 | 95 | 95 |
| rot13 | cpp | 778 | 778 | 267 | 218 | 214 | 214 |
| invert_bytes | expr-v5 | 66 | 66 | 51 | 37 | 35 | 34 |
| invert_bytes | python | 211 | 211 | 68 | 52 | 50 | 50 |
| invert_bytes | cpp | 625 | 625 | 193 | 148 | 146 | 146 |
| reverse_bytes | expr-v5 | 82 | 82 | 60 | 44 | 44 | 43 |
| reverse_bytes | python | 193 | 193 | 60 | 44 | 44 | 44 |
| reverse_bytes | cpp | 556 | 556 | 169 | 127 | 127 | 127 |
| hex_encode | expr-v5 | 148 | 148 | 97 | 78 | 69 | 68 |
| hex_encode | python | 209 | 209 | 64 | 47 | 47 | 47 |
| hex_encode | cpp | 668 | 668 | 213 | 169 | 161 | 161 |
| count_newlines | expr-v5 | 96 | 96 | 64 | 50 | 49 | 48 |
| count_newlines | python | 230 | 230 | 75 | 56 | 56 | 56 |
| count_newlines | cpp | 617 | 617 | 191 | 144 | 144 | 144 |
| nonempty_lines | expr-v5 | 177 | 177 | 114 | 87 | 85 | 86 |
| nonempty_lines | python | 240 | 240 | 80 | 61 | 61 | 62 |
| nonempty_lines | cpp | 665 | 665 | 203 | 155 | 155 | 157 |
| normalize_crlf | expr-v5 | 168 | 168 | 108 | 85 | 83 | 83 |
| normalize_crlf | python | 211 | 211 | 70 | 51 | 51 | 51 |
| normalize_crlf | cpp | 698 | 698 | 231 | 181 | 181 | 181 |
| prefix_lines | expr-v5 | 121 | 121 | 75 | 62 | 61 | 61 |
| prefix_lines | python | 346 | 346 | 119 | 93 | 93 | 93 |
| prefix_lines | cpp | 671 | 671 | 219 | 171 | 171 | 171 |
| first_fields_csv | expr-v5 | 218 | 218 | 149 | 111 | 108 | 108 |
| first_fields_csv | python | 324 | 324 | 113 | 90 | 90 | 91 |
| first_fields_csv | cpp | 672 | 672 | 208 | 158 | 158 | 160 |
| sum_pairs | expr-v5 | 251 | 251 | 163 | 122 | 119 | 120 |
| sum_pairs | python | 282 | 282 | 91 | 69 | 69 | 70 |
| sum_pairs | cpp | 780 | 780 | 245 | 188 | 188 | 190 |
| sum_integers | expr-v5 | 163 | 163 | 109 | 82 | 80 | 81 |
| sum_integers | python | 245 | 245 | 78 | 58 | 58 | 58 |
| sum_integers | cpp | 689 | 689 | 211 | 162 | 162 | 164 |
| min_max | expr-v5 | 484 | 484 | 282 | 209 | 205 | 207 |
| min_max | python | 278 | 278 | 88 | 67 | 67 | 67 |
| min_max | cpp | 821 | 821 | 259 | 204 | 204 | 206 |
| dedupe_adjacent_lines | expr-v5 | 432 | 432 | 272 | 203 | 199 | 201 |
| dedupe_adjacent_lines | python | 371 | 371 | 129 | 104 | 104 | 105 |
| dedupe_adjacent_lines | cpp | 773 | 773 | 232 | 180 | 180 | 182 |
| running_report | expr-v5 | 139 | 139 | 75 | 58 | 58 | 58 |
| running_report | python | 262 | 262 | 91 | 72 | 72 | 73 |
| running_report | cpp | 715 | 715 | 233 | 183 | 183 | 183 |
| number_lines | expr-v5 | 254 | 254 | 147 | 114 | 111 | 111 |
| number_lines | python | 341 | 341 | 118 | 94 | 94 | 95 |
| number_lines | cpp | 706 | 706 | 217 | 167 | 167 | 169 |
| histogram_digits | expr-v5 | 220 | 220 | 142 | 111 | 106 | 105 |
| histogram_digits | python | 328 | 328 | 106 | 86 | 84 | 85 |
| histogram_digits | cpp | 766 | 766 | 257 | 206 | 204 | 204 |
| buffer_sum | expr-v5 | 313 | 313 | 231 | 177 | 172 | 171 |
| buffer_sum | python | 333 | 333 | 103 | 76 | 76 | 76 |
| buffer_sum | cpp | 905 | 905 | 277 | 208 | 208 | 211 |
| buffer_dot | expr-v5 | 462 | 462 | 338 | 258 | 250 | 254 |
| buffer_dot | python | 447 | 447 | 151 | 120 | 120 | 120 |
| buffer_dot | cpp | 1117 | 1117 | 362 | 280 | 280 | 282 |
| prefix_sums | expr-v5 | 336 | 336 | 245 | 188 | 183 | 182 |
| prefix_sums | python | 369 | 369 | 115 | 89 | 89 | 89 |
| prefix_sums | cpp | 827 | 827 | 254 | 196 | 196 | 198 |
| copy_file | expr-v5 | 25 | 25 | 15 | 10 | 10 | 10 |
| copy_file | python | 187 | 187 | 57 | 42 | 42 | 42 |
| copy_file | cpp | 535 | 535 | 162 | 122 | 122 | 122 |
| slice_file | expr-v5 | 161 | 161 | 114 | 81 | 79 | 80 |
| slice_file | python | 304 | 304 | 98 | 73 | 73 | 73 |
| slice_file | cpp | 760 | 760 | 236 | 186 | 186 | 186 |
| expand_tabs | expr-v5 | 98 | 98 | 63 | 48 | 48 | 48 |
| expand_tabs | python | 211 | 211 | 68 | 50 | 50 | 50 |
| expand_tabs | cpp | 605 | 605 | 189 | 148 | 148 | 148 |
| env_lookup | expr-v5 | unsupported | — | — | — | — | — |
| env_lookup | python | 249 | 249 | 78 | 58 | 58 | 58 |
| env_lookup | cpp | 619 | 619 | 188 | 143 | 143 | 143 |

## Tokenizer identity

Use the exact local GGUF vocabulary assets from the generation study. `llama-cpp-python` **0.3.16** loads with `vocab_only=True`, `n_gpu_layers=0`; logs say `vocab only - skipping tensors`. No inference context, decode, model server or generation request is created. `add_special=False`, `parse_special=False`: no BOS/EOS/chat template, and special-looking strings are ordinary source. Gemma is its actual 262145-entry SPM vocabulary; Qwen is its actual 152064-entry BPE vocabulary. This backend is pinned; it is not claimed to reproduce every normalization/version detail of Ollama's internal tokenizer.

| Tokenizer | Generation model/asset | Manifest SHA-256 | GGUF SHA-256 |
|---|---|---|---|
| gemma3_4b | `gemma3/4b` | `a2af6cc3eb7fa8be8504abaf9b04e88f17a119ec3f04a3addf55f92841195f5a` | `aeda25e63ebd698fab8638ffb778e68bed908b960d39d0becc650fa981609d25` |
| qwen2.5_7b_instruct | `qwen2.5/7b-instruct` | `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e` | `2bada8a7450677000f678be90653b85d364de7db25eb5ea54136ada5f3933730` |

Gemma's official Hugging Face tokenizer files require authenticated gated access, so no unofficial replacement was used. Vocabulary-only loading of the existing frozen GGUF avoids another model download. Qwen was independently cross-checked against its official tokenizer JSON at revision `a09a35458c702b33eeacc393d103063234e8bc28`, SHA-256 `c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539`, using `tokenizers` **0.22.1**: **74 counts, zero mismatches**. That JSON is byte-identical to the existing paired suite asset; the runner reuses its hash-checked loader. [Official Qwen asset](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/blob/a09a35458c702b33eeacc393d103063234e8bc28/tokenizer.json).

`tiktoken` **0.12.0** supplies both `cl100k_base` and `o200k_base` (ordinary-text special-token handling). Rank-table hashes and tokenizer probe IDs are recorded. Python **3.12.11**, Apple Clang **21.0.0 (clang-2100.1.1.101)**, macOS **27.0 arm64**; dependencies are pinned in the benchmark Python environment only. Missing model assets stop counting explicitly. No compiler workspace dependency was added.

## Language findings and adaptation value

`buffer_dot` is the largest NIL solution (338 Gemma tokens); `min_max` (282), adjacent dedupe (272), `prefix_sums` (245), and `buffer_sum` (231) follow. Manual delimiter scans, counting passes before buffer allocation, repeated parsing across parallel loop updates, and hand-written sequence equality dominate these cases. Their Python equivalents use standard-library operations and fewer positional-state transfers. Min/max and dedupe also exceed C++ under every tokenizer. Simple built-in file copy and some byte transforms favour NIL; see every row rather than selecting only those wins.

Record missing environment access, no built-in byte equality or delimiter iterator, no dynamic buffer builder, and no multi-result bindings/records as generality input. Typed semantic operations or binding changes are **unimplemented proposals**, not syntax changes made to win. Read the [corpus findings](../../corpora/application-v5/README.md#generality-findings-unimplemented) for the awkward formulations.

The corpus contains **24 verified NIL positives**, with statements/oracles and MIT license, plus 50 verified baselines. `export.py` emits hashed positive JSONL; unsupported tasks are excluded from positives, retained in the manifest. Four tasks overlap the earlier generation study; split by semantic family and use new held-out tasks. 24 examples support few-shot seeds, not a usable fine-tuning claim. A rough planning range of 500–2,000 independent verified tasks plus repair/negative trajectories is 20–80x larger; this is a heuristic for a pilot, not an experimentally established requirement. No adaptation was run.

## Commands and actual output

From the compiler checkout; exact commands and dependency setup are in the [corpus README](../../corpora/application-v5/README.md#reproduce-from-the-compiler-checkout-macos).

```text
benchmarks/paired/.venv/bin/python -m unittest discover -s benchmarks/corpora/application-v5/tests -v
Ran 5 tests; OK. Two deliberate bad references rejected.

benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/verify.py --output /tmp/nil-v5-density/verification.json
TOTALS {"tasks":25,"nil_programs":24,"unsupported":1,"reference_checks":120,"native_checks":240,"python_checks":125,"cpp_checks":125}

benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/density.py --verification /tmp/nil-v5-density/verification.json --output /tmp/nil-v5-density/measurement
Adaptation examples: 24
QWEN_CROSSCHECK comparisons: 74; mismatches: []
PAIRED_TOTALS: see measured aggregate table above.

benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/export.py --verification /tmp/nil-v5-density/verification.json --output /tmp/nil-v5-density/adaptation.jsonl
Exported 24 verified NIL examples

./scripts/ci.sh
208 passed; 0 failed; no clippy warnings (sum of cargo test result blocks).
```

Raw logs and exported JSONL are archived outside source control. Small measured CSV/JSON and full source/verdict hashes are committed so the aggregate is auditable without downloading weights. Local commits only; nothing pushed.

External raw evidence archive: `~/.local/share/nil/benchmarks/archive/v5-density-2026-10-03.zip`; SHA-256 `23339aa15d4be0f5f632884c7379718a65b890e8aa4923a6f33089326fde9762`. It contains command logs, measured tables, verification, exports and environment details, not weights or executables. Frozen tasks commit `f1d2ba2`; verified corpus commit `4731369` in the benchmark repository. These are local commits and are not remotely available until explicitly published.
