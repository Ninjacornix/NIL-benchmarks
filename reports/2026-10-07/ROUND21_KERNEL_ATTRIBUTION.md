# Round 21: exact kernel token attribution

NIL costs **1,739 more cl100k tokens (+66.7%)** and **1,748 more o200k tokens (+66.7%)** than Python on the frozen 29-program Round 20 kernel cut. This is source density, not model generation efficiency. Helpers, flat-buffer offsets and callback signatures remain charged. No source, oracle, golden or syntax was changed.

The ledger uses greatest non-whitespace byte overlap, breaking ties by first source occurrence. Every category is disjoint; positive costs and negative savings sum exactly to the gap. The per-token raw ledger is emitted outside git by `core-generalize-study/attribution.py`. The JSON alongside this report freezes the method, density hash and aggregate checks.

## cl100k_base

| Category | NIL | Python | Difference |
|---|---:|---:|---:|
| separator | 1376 | 509 | 867 |
| numeric_literal | 688 | 161 | 527 |
| signature | 370 | 167 | 203 |
| operator | 506 | 303 | 203 |
| conditional | 273 | 75 | 198 |
| loop_delimiters | 192 | 31 | 161 |
| loop_index_bound | 117 | 60 | 57 |
| call_identifier | 51 | 5 | 46 |
| record_definition | 42 | 0 | 42 |
| boolean_literal | 40 | 9 | 31 |
| unchanged_state | 15 | 0 | 15 |
| identifier | 575 | 567 | 8 |
| comment | 0 | 0 | 0 |
| text_literal | 31 | 42 | -11 |
| intrinsic_name | 68 | 110 | -42 |
| keyword | 0 | 111 | -111 |
| whitespace | 4 | 459 | -455 |
| **Total** | **4348** | **2609** | **1739** |

## o200k_base

| Category | NIL | Python | Difference |
|---|---:|---:|---:|
| separator | 1376 | 512 | 864 |
| numeric_literal | 688 | 161 | 527 |
| operator | 509 | 304 | 205 |
| signature | 370 | 167 | 203 |
| conditional | 274 | 75 | 199 |
| loop_delimiters | 192 | 31 | 161 |
| loop_index_bound | 115 | 60 | 55 |
| call_identifier | 52 | 5 | 47 |
| record_definition | 42 | 0 | 42 |
| boolean_literal | 40 | 9 | 31 |
| identifier | 591 | 574 | 17 |
| unchanged_state | 15 | 0 | 15 |
| comment | 0 | 0 | 0 |
| text_literal | 31 | 41 | -10 |
| intrinsic_name | 69 | 111 | -42 |
| keyword | 0 | 111 | -111 |
| whitespace | 4 | 459 | -455 |
| **Total** | **4368** | **2620** | **1748** |

## Interpretation

Separators/brackets and numeric literals dominate the positive costs. Categories cannot establish the savings of a syntax or library change: replacing arithmetic, flat layouts or whole helpers may move several categories together. This round freezes the attribution and changes no spelling.

Verification: `benchmarks/paired/.venv/bin/python -m unittest discover -s benchmarks/core-generalize-study -p "test_*.py" -v` passed **5 tests**; attribution independently reconstructs every source byte and reproduces **4,348/2,609 cl100k and 4,368/2,620 o200k**. tiktoken 0.12.0.

This is Part A3 only. Copy census, complete memory/qualification measurements, forecasts, ADR 043 and implementation are pending.
