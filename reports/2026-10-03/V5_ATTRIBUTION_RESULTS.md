# External token attribution — reverified results

**No compiler, grammar or corpus source changes were justified. Actual savings are zero.**
The [preregistered plan](V5_ATTRIBUTION_PLAN.md) and [exact token ledger](V5_ATTRIBUTION.json) explain the 650-token cl100k surplus. The source-token gap remains unchanged. Density is not tokens until correctness; the generation finding remains NIL 0/24 versus Python 11/24.

## Three cuts, before and after

Each cell is before → after; the populations and every reference source are identical. Per-task results, bytes/characters and pinned tokenizer versions are in [JSON](V5_ATTRIBUTION_DENSITY.json) and [CSV](V5_ATTRIBUTION_TOKENS.csv).
| Cut | Tokenizer | NIL | Python | C++ | NIL vs Python | NIL vs C++ |
|---|---|---:|---:|---:|---:|---:|
| original (24 pairs) | gemma3_4b | 2144 → 2144 | 2227 → 2227 | 5454 → 5454 | -3.73% | -60.69% |
| original (24 pairs) | qwen2.5_7b_instruct | 1634 → 1634 | 1728 → 1728 | 4235 → 4235 | -5.44% | -61.42% |
| original (24 pairs) | cl100k_base | 1582 → 1582 | 1705 → 1705 | 4217 → 4217 | -7.21% | -62.49% |
| original (24 pairs) | o200k_base | 1571 → 1571 | 1712 → 1712 | 4238 → 4238 | -8.24% | -62.93% |
| new_external (32 pairs) | gemma3_4b | 7586 → 7586 | 6262 → 6262 | 13128 → 13128 | +21.14% | -42.22% |
| new_external (32 pairs) | qwen2.5_7b_instruct | 5828 → 5828 | 5112 → 5112 | 10493 → 10493 | +14.01% | -44.46% |
| new_external (32 pairs) | cl100k_base | 5686 → 5686 | 5036 → 5036 | 10458 → 10458 | +12.91% | -45.63% |
| new_external (32 pairs) | o200k_base | 5667 → 5667 | 5059 → 5059 | 10498 → 10498 | +12.02% | -46.02% |
| combined (56 pairs) | gemma3_4b | 9730 → 9730 | 8489 → 8489 | 18582 → 18582 | +14.62% | -47.64% |
| combined (56 pairs) | qwen2.5_7b_instruct | 7462 → 7462 | 6840 → 6840 | 14728 → 14728 | +9.09% | -49.33% |
| combined (56 pairs) | cl100k_base | 7268 → 7268 | 6741 → 6741 | 14675 → 14675 | +7.82% | -50.47% |
| combined (56 pairs) | o200k_base | 7238 → 7238 | 6771 → 6771 | 14736 → 14736 | +6.90% | -50.88% |

## Forecast versus implementation

| Unimplemented candidate | Gemma forecast | Qwen | cl100k | o200k | Actual implemented savings |
|---|---:|---:|---:|---:|---|
| Earlier identical signature reference | 78 | 32 | 32 | 32 | 0; not implemented |
| Empty unchanged-state step | 131 | 9 | 9 | 9 | 0; not implemented |

These are lexical counterfactual forecasts, not promises or native-verified programs. There is no executable actual saving to compare for either proposed syntax. The implementation gate rejected both; retaining the existing grammar is the measured outcome. No larger algorithm rewrite has a justified numerical forecast yet.

## Evidence and limits

64 source files × four tokenizers yield 256 streams and **46,236 fully accounted tokens**. Exact rational category differences sum to every measured gap. Whole-token assignment sensitivity is retained; in cl100k it moves much of `,a` from identifiers into separators, so fractional ranking drives the decision. All sources are ASCII; the ledger fails closed on non-ASCII rather than guessing byte offsets.

Token accounting is exhaustive under the documented classification. This is not a causal experiment proving minimum program lengths. The sources were written locally; task selection is a nonrandom first-50/first-property Exercism sample with finite independent fixture oracles. Counts are deterministic, not statistical estimates of future models/tasks. The top three tasks explain 80.5% of this net gap, not every possible general-purpose program. No inference was performed.

The [verification](V5_ATTRIBUTION_VERIFICATION.json) confirms **2400 checks**: 478 reference, 956 native (478 each O0/O2), 483 Python and 483 C++. The [original cohort](V5_ATTRIBUTION_ORIGINAL_VERIFICATION.json) separately confirms **610**. All 56 NIL sources, all existing Python/C++ sources, tasks, oracles and goldens match the previous frozen source hashes. The 19 unsupported tasks remain (18 external); no task was dropped or reworded.

See the main repository validation document for fresh CI, both sanitizer suites, three-seed differential counts and performance controls. The raw token ledger is regenerated outside the checkout; the committed summary retains all exact task/category totals.
