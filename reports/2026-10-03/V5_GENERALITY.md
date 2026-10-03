# Corpus-driven v5 generality additions

**Three typed operations reduced NIL source tokens by 32.3–32.9% on the frozen 24-task paired corpus. NIL moved from 36.7–43.5% more tokens than Python to 3.7–8.2% fewer, and now uses 60.7–62.9% fewer than C++ including headers and I/O. All 11 rewrites improve under every tokenizer; 13 tasks remain unchanged.**

**This is source density, NOT total model work. The original generation study remains unfavourable (NIL 0/24 versus Python 11/24). No inference, repairs or generation with the new operations were measured. The small, correlated authored corpus and C++ framing do not establish a universal language ranking.**

## Decision made before implementation

[Pre-implementation ranking](../../../docs/experiments/V5_GENERALITY_IMPACT.md) was committed in the compiler as `5832936`, before implementation `abc6afe` and fuzz extension `7142629`. It contains token-counted but explicitly unverified prototypes. Bulk canonical integer parsing ranked first (six tasks), scalar delimiter search second (four), and value equality third (one). All estimates match actual verified source counts; none was backfilled after implementation. No existing identifier or grammar spelling was changed. Function indices change only when obsolete helper declarations disappear.

Add `parsebuf(Bytes,Bytes)->Buffer`, `find(S,I64,I64)->I64` and `equal(S,S)->Bool` for matching dynamic S. New HIR signatures, reference evaluation, native checked helpers and borrowing summaries share the existing intrinsic mechanism. See [specification](../../../docs/language/EXPR_V5.md) and [ADR 022](../../../docs/adr/022.md). No records, new types, new profile, default/earlier profile change, Rust dependency, plugin ABI or environment access.

## Allocation and remaining cost

Parsebuf reserves one fresh exact-capacity integer buffer after counting fields, before canonical conversion; E013 precedes E016. It performs two linear byte scans plus canonical field conversion and reserves `8 * field_count + 40` bytes. Peak charge includes the live input and separator capacities (shared identities counted once) and other caller roots. Byte input cannot be reused as an i64 payload without a different conversion/lifetime proof; no such proof or view was added. This is bulk allocation, not zero-copy.

Search/equality allocate nothing and extend the HIR borrowing property without purity/nontrapping LLVM attributes. Parsed buffers compose with existing concat/replacement proofs. IR tests assert `nil_concat_unique` for dead single-use loop state and `nil_concat` when an old read remains. Runtime uniqueness still handles caller aliases. Allocation cases remain conservative; there is no per-field replacement/copy in parsebuf construction.

Builders, multi-result bindings/records and nested-sequence split were deferred: bulk conversion removes the measured numeric scaffolding more directly; search exposes line boundaries with existing types. Environment lookup stays unsupported and retained. Deduplication still repeats slice expressions; hex, CRLF and formatting have remaining language/library costs.

## Same tasks, outputs, baselines and tokenizers

Tasks, inclusion rationales, oracles, literal goldens, Python and C++ sources are byte-identical to benchmark commit `9be44d6`. The 24 updated NIL references again pass five fixtures each: **120 reference + 120 native O0 + 120 native O2 + 125 Python + 125 C++ = 610 checks**. `env_lookup` remains the one unsupported NIL task; missing counts are not zero. [Verdicts/source hashes](V5_GENERALITY_VERIFICATION.json).

Same raw-file accounting: imports, custom helpers, I/O and whitespace included; shared CLI adapters excluded. Same exact frozen Gemma/Qwen GGUF vocabularies via vocabulary-only llama-cpp-python 0.3.16, and tiktoken 0.12.0 cl100k/o200k. Qwen JSON cross-check: 74 counts, no mismatches. No model server or inference context. [Full pins/counts](V5_GENERALITY_DENSITY.json), [before/after CSV with bytes/characters](V5_GENERALITY_TOKENS.csv), [baseline](V5_DENSITY.md).

## Aggregate before/after (24 paired tasks)

| Tokenizer | NIL before | NIL after | Python | C++ | NIL change | After vs Python | After vs C++ |
|---|---:|---:|---:|---:|---:|---:|---:|
| gemma3_4b | 3196 | 2144 | 2227 | 5454 | -32.92% | -3.73% | -60.69% |
| qwen2.5_7b_instruct | 2418 | 1634 | 1728 | 4235 | -32.42% | -5.44% | -61.42% |
| cl100k_base | 2338 | 1582 | 1705 | 4217 | -32.34% | -7.21% | -62.49% |
| o200k_base | 2340 | 1571 | 1712 | 4238 | -32.86% | -8.24% | -62.93% |

## Every task, every tokenizer

Each cell is NIL before → after / Python / C++. G = Gemma; Q = Qwen; C = cl100k; O = o200k. Unsupported has no NIL count. Complete bytes, characters, source hashes and long-form counts are linked above.

| Task | G | Q | C | O |
|---|---:|---:|---:|---:|
| ascii_upper | 75 → 75 / 81 / 213 | 53 → 53 / 64 / 167 | 49 → 49 / 60 / 166 | 48 → 48 / 60 / 166 |
| ascii_lower | 74 → 74 / 80 / 213 | 52 → 52 / 63 / 167 | 49 → 49 / 60 / 166 | 48 → 48 / 60 / 166 |
| rot13 | 133 → 133 / 124 / 267 | 98 → 98 / 107 / 218 | 86 → 86 / 95 / 214 | 85 → 85 / 95 / 214 |
| invert_bytes | 51 → 51 / 68 / 193 | 37 → 37 / 52 / 148 | 35 → 35 / 50 / 146 | 34 → 34 / 50 / 146 |
| reverse_bytes | 60 → 60 / 60 / 169 | 44 → 44 / 44 / 127 | 44 → 44 / 44 / 127 | 43 → 43 / 44 / 127 |
| hex_encode | 97 → 97 / 64 / 213 | 78 → 78 / 47 / 169 | 69 → 69 / 47 / 161 | 68 → 68 / 47 / 161 |
| count_newlines | 64 → 64 / 75 / 191 | 50 → 50 / 56 / 144 | 49 → 49 / 56 / 144 | 48 → 48 / 56 / 144 |
| nonempty_lines | 114 → 90 / 80 / 203 | 87 → 70 / 61 / 155 | 85 → 68 / 61 / 155 | 86 → 67 / 62 / 157 |
| normalize_crlf | 108 → 108 / 70 / 231 | 85 → 85 / 51 / 181 | 83 → 83 / 51 / 181 | 83 → 83 / 51 / 181 |
| prefix_lines | 75 → 75 / 119 / 219 | 62 → 62 / 93 / 171 | 61 → 61 / 93 / 171 | 61 → 61 / 93 / 171 |
| first_fields_csv | 149 → 98 / 113 / 208 | 111 → 77 / 90 / 158 | 108 → 74 / 90 / 158 | 108 → 73 / 91 / 160 |
| sum_pairs | 163 → 70 / 91 / 245 | 122 → 56 / 69 / 188 | 119 → 56 / 69 / 188 | 120 → 55 / 70 / 190 |
| sum_integers | 109 → 61 / 78 / 211 | 82 → 47 / 58 / 162 | 80 → 47 / 58 / 162 | 81 → 46 / 58 / 164 |
| min_max | 282 → 98 / 88 / 259 | 209 → 75 / 67 / 204 | 205 → 75 / 67 / 204 | 207 → 76 / 67 / 206 |
| dedupe_adjacent_lines | 272 → 224 / 129 / 232 | 203 → 167 / 104 / 180 | 199 → 163 / 104 / 180 | 201 → 166 / 105 / 182 |
| running_report | 75 → 75 / 91 / 233 | 58 → 58 / 72 / 183 | 58 → 58 / 72 / 183 | 58 → 58 / 73 / 183 |
| number_lines | 147 → 93 / 118 / 217 | 114 → 74 / 94 / 167 | 111 → 72 / 94 / 167 | 111 → 71 / 95 / 169 |
| histogram_digits | 142 → 142 / 106 / 257 | 111 → 111 / 86 / 206 | 106 → 106 / 84 / 204 | 105 → 105 / 85 / 204 |
| buffer_sum | 231 → 61 / 103 / 277 | 177 → 47 / 76 / 208 | 172 → 47 / 76 / 208 | 171 → 46 / 76 / 211 |
| buffer_dot | 338 → 140 / 151 / 362 | 258 → 104 / 120 / 280 | 250 → 104 / 120 / 280 | 254 → 103 / 120 / 282 |
| prefix_sums | 245 → 74 / 115 / 254 | 188 → 57 / 89 / 196 | 183 → 57 / 89 / 196 | 182 → 56 / 89 / 198 |
| copy_file | 15 → 15 / 57 / 162 | 10 → 10 / 42 / 122 | 10 → 10 / 42 / 122 | 10 → 10 / 42 / 122 |
| slice_file | 114 → 103 / 98 / 236 | 81 → 74 / 73 / 186 | 79 → 72 / 73 / 186 | 80 → 73 / 73 / 186 |
| expand_tabs | 63 → 63 / 68 / 189 | 48 → 48 / 50 / 148 | 48 → 48 / 50 / 148 | 48 → 48 / 50 / 148 |
| env_lookup | unsupported / 78 / 188 | unsupported / 58 / 143 | unsupported / 58 / 143 | unsupported / 58 / 143 |

Unchanged tasks: `ascii_upper`, `ascii_lower`, `rot13`, `invert_bytes`, `reverse_bytes`, `hex_encode`, `count_newlines`, `normalize_crlf`, `prefix_lines`, `running_report`, `histogram_digits`, `copy_file`, `expand_tabs`. No rewritten task worsened. These unchanged results are retained, not omitted as unsuccessful candidates.

### Every remaining non-win

- **gemma3_4b / python**: 15 wins, 1 ties, 8 losses. Losses: `rot13`, `hex_encode`, `nonempty_lines`, `normalize_crlf`, `min_max`, `dedupe_adjacent_lines`, `histogram_digits`, `slice_file`. Ties: `reverse_bytes`.
- **gemma3_4b / cpp**: 24 wins, 0 ties, 0 losses. Losses: none. Ties: none.
- **qwen2.5_7b_instruct / python**: 16 wins, 1 ties, 7 losses. Losses: `hex_encode`, `nonempty_lines`, `normalize_crlf`, `min_max`, `dedupe_adjacent_lines`, `histogram_digits`, `slice_file`. Ties: `reverse_bytes`.
- **qwen2.5_7b_instruct / cpp**: 24 wins, 0 ties, 0 losses. Losses: none. Ties: none.
- **cl100k_base / python**: 17 wins, 1 ties, 6 losses. Losses: `hex_encode`, `nonempty_lines`, `normalize_crlf`, `min_max`, `dedupe_adjacent_lines`, `histogram_digits`. Ties: `reverse_bytes`.
- **cl100k_base / cpp**: 24 wins, 0 ties, 0 losses. Losses: none. Ties: none.
- **o200k_base / python**: 17 wins, 1 ties, 6 losses. Losses: `hex_encode`, `nonempty_lines`, `normalize_crlf`, `min_max`, `dedupe_adjacent_lines`, `histogram_digits`. Ties: `slice_file`.
- **o200k_base / cpp**: 24 wins, 0 ties, 0 losses. Losses: none. Ties: none.

## Performance regression controls

Same Apple M2/macOS 27, Apple Clang 21.0.0, Rust 1.98.1 and Python 3.12.11. Before compiler `5391b3a`; after `7142629` (implementation sources committed). Same existing benchmark sources; dirty benchmark state is corpus rewrites only. Nine timed whole-process samples after one warmup, rotating NIL/C++/Python order; builds and byte verification excluded. Cached files, no fsync, no CPU isolation. All substantial validation/counting jobs finished before accepted timings. An initial after-workload run overlapped final corpus verification and was excluded; retained externally for audit.

NIL O2 uses existing LTO, C++ clang++ -std=c++17 -O2. No workload source was changed to use the new operations: these are regression controls, not proof of new-operation runtime superiority. Scan has 986895 newlines in the 16 MiB fixture; arbitrary-byte control also passes. Append contents verified separately. Every transform byte matches and double transforms round-trip at all three sizes.

| Control | NIL before ms | NIL after ms | C++ before ms | C++ after ms | Python before ms | Python after ms |
|---|---:|---:|---:|---:|---:|---:|
| newlines 16777216 | 7.320 | 7.371 | 9.840 | 9.851 | 23.392 | 23.161 |
| append 1048576 | 24.176 | 24.153 | 4.785 | 4.692 | 43.629 | 43.103 |
| transform 16777216 | 39.051 | 37.855 | 15.755 | 14.741 | 818.625 | 785.756 |

No systematic regression appears: scan +0.7%, append −0.1%, transform −3.1%. These are noisy whole-process medians, not statistical equivalence proof. NIL still loses to C++ on append and transform, and beats Python on these controls. Scan beats the direct C++ scan here; do not generalize that advantage. Normalized emitted IR for all three is identical except the three new unused declarations, with hashes in [full manifests](V5_GENERALITY_PERFORMANCE.json). New operations introduce no changed instructions into these control kernels.

The [corpus](../../corpora/application-v5/README.md) remains an MIT adaptation seed with 24 verified positives, not a usable fine-tuning set or demonstrated adaptation. Old source versions remain at `9be44d6`; updated sources require compiler `abc6afe` or later. Keep semantic-family holdouts and the earlier-generation overlap labels.

## Commands and validation

Archived command logs, seeds, [per-code/call-family counts](V5_GENERALITY_FUZZ.json), IR and provenance are cited in [compiler validation](../../../docs/validation/V5_GENERALITY.md).

```text
./scripts/ci.sh: 220 passed, 0 failed; no clippy warnings
./scripts/ci.sh release: 220 passed, 0 failed
./scripts/sanitize.sh: 36 native application tests passed at O0/O2
./scripts/fuzz-v5.sh --seed SEED --cases 312 --out /tmp/nil-generality/fuzz-SEED
SEED = 5130572, 17, 991: each 312 programs / 624 native builds / 0 divergences
Total: 936 programs / 1872 native builds; all new operation/failure families covered
verify.py: 610 checks passed; 24 verified NIL programs / 25 Python / 25 C++
density.py: estimates match verified counts under all four tokenizers
```

No production defect was found by the differential campaigns or sanitizers. An initial native test incorrectly declared a zero-parameter helper as `0=`; the fixture was corrected to the existing `=` form. Initial strict Clippy caught a new Rust helper placed after the test module; moved it before the module. No task/oracle/golden was changed to make tests pass. Additional final checks assert exact reference results, copy-vs-reuse IR, and E013 with a valid-size result exceeding combined live caller/input capacity. Everything committed locally; nothing pushed.
