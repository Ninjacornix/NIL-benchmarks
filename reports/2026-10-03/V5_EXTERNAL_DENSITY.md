# External corpus density: the Python advantage reverses

**NIL uses 10.6–19.9% MORE source tokens than Python on the 31 supported externally derived properties. The combined 55-program set uses 5.8–13.6% MORE. The original 24 still use 3.7–8.2% fewer; that advantage does not hold on this external sample.**

**75 tasks are retained: 25 self-authored and 50 externally derived. 20 lack verified NIL solutions (19 external, one original). These include missing capabilities and unimplemented adapters; excluded tasks are not zero-token wins. There are 55 verified NIL programs and 55 exported positives, still well below adaptation scale.**

Source density is not total model work. The prior generation/repair study remains unfavourable: NIL 0/24 versus Python 11/24. No inference or training occurred. This nonrandom, single-source, API-component sample does not establish an unbiased population estimate, despite removing discretionary task picking.

## Selection, provenance and license

The first 50 alphabetically sorted Exercism problem-specification directories with canonical-data.json were frozen at `9943fd751b684ba1a6a8673c3700a6e79c10a808`. The [selection](../../corpora/application-v5/external/selection.json) was committed as `eb90202`, and [transport contracts](../../corpora/application-v5/external/tasks.json) as `7f5f8b5`, before reference implementation `a52c203` and token counts. No selected exercise was removed. Each adapter targets the first declared canonical property; this is **not the complete upstream exercise API**. All matching canonical cases are retained except those explicitly superseded by reimplements.

Exercism specifications/canonical expected values are [MIT licensed](https://github.com/exercism/problem-specifications/blob/9943fd751b684ba1a6a8673c3700a6e79c10a808/LICENSE); the notice is retained in [EXERCISM_LICENSE](../../corpora/application-v5/external/EXERCISM_LICENSE). Adapted transports, implementations and original tasks are locally authored under the corpus MIT license. [Per-task provenance and license](../../corpora/application-v5/PROVENANCE.json) distinguishes all 75 tasks. No upstream solution was copied. Both sides still have the same author: external task provenance does not remove implementation bias.

New output oracles use pinned canonical input/expected-value maps with UUIDs. They are finite executable fixture oracles, not algorithms for arbitrary unseen inputs; unknown input is rejected. Text/file adapters and arithmetic domains are disclosed per task. Canonical expected values and both original oracle/golden files remain unchanged. Two classification/wording corrections occurred **before** counting: Armstrong includes 108/127-bit integers and became unsupported; invalid binary output is null, not zero. Neither fix changed a frozen expected value or dropped a source case.

The first coin-change DP and Hex flood implementation exceeded the existing 100,000-step budget. Branch-and-bound and union-find replaced them before counting; no limit/compiler change. Initial reference-authoring errors (redundant all-i64 typed headers, bool equality, C++ newline escaping) were corrected. No compiler bug was found.

## Verification and reproducibility

**2,380 checks passed:** 474 reference + 474 native O0 + 474 native O2 + 479 Python + 479 C++. The original group separately passes its existing 610 checks. External support contributes 1,770 checks; there are 353 distinct supported external task/input pairs and 354 checks per execution path (Hello World repeats its sole canonical input as the appended golden). Counts are execution checks, not independent proofs.

[Full verdicts/source hashes](V5_EXTERNAL_VERIFICATION.json), [original 610-check rerun](V5_EXTERNAL_ORIGINAL_VERIFICATION.json), [tokenizer metadata/counts](V5_EXTERNAL_DENSITY.json), [long-form CSV](V5_EXTERNAL_TOKENS.csv), [command evidence](../../../docs/validation/V5_EXTERNAL_DENSITY.md). CI remains 220 tests with strict Clippy; compiler/runtime/profiles/default, Rust dependencies, original 25 task objects, original oracles/goldens and all 74 old sources are unchanged.

Reused verify.py, application_check in-memory Host, native O0/O2, Python/C++ adapters, the original budget and quota. No new execution harness. Bench Python dependencies are unchanged. Same Gemma/Qwen GGUF vocabularies via vocabulary-only llama-cpp-python 0.3.16; tiktoken 0.12.0 cl100k/o200k. Qwen tokenizers 0.22.1 cross-checks 167 source counts without mismatches. No model server/inference context.

## Three cuts across all four tokenizers

Percent is (NIL / baseline − 1) × 100; positive means NIL costs more. All token sums pair the same supported tasks. Unsupported tasks remain in the total/unsupported counts but have no NIL denominator.

| Cut | Total / paired / unsupported | Tokenizer | NIL | Python | C++ | NIL vs Python | NIL vs C++ |
|---|---:|---|---:|---:|---:|---:|---:|
| original | 25 / 24 / 1 | gemma3_4b | 2144 | 2227 | 5454 | -3.73% | -60.69% |
| original | 25 / 24 / 1 | qwen2.5_7b_instruct | 1634 | 1728 | 4235 | -5.44% | -61.42% |
| original | 25 / 24 / 1 | cl100k_base | 1582 | 1705 | 4217 | -7.21% | -62.49% |
| original | 25 / 24 / 1 | o200k_base | 1571 | 1712 | 4238 | -8.24% | -62.93% |
| new_external | 50 / 31 / 19 | gemma3_4b | 7372 | 6147 | 12712 | +19.93% | -42.01% |
| new_external | 50 / 31 / 19 | qwen2.5_7b_instruct | 5650 | 5025 | 10148 | +12.44% | -44.32% |
| new_external | 50 / 31 / 19 | cl100k_base | 5520 | 4949 | 10113 | +11.54% | -45.42% |
| new_external | 50 / 31 / 19 | o200k_base | 5498 | 4972 | 10153 | +10.58% | -45.85% |
| combined | 75 / 55 / 20 | gemma3_4b | 9516 | 8374 | 18166 | +13.64% | -47.62% |
| combined | 75 / 55 / 20 | qwen2.5_7b_instruct | 7284 | 6753 | 14383 | +7.86% | -49.36% |
| combined | 75 / 55 / 20 | cl100k_base | 7102 | 6654 | 14330 | +6.73% | -50.44% |
| combined | 75 / 55 / 20 | o200k_base | 7069 | 6684 | 14391 | +5.76% | -50.88% |

| Cut | NIL bytes / characters | Python bytes / characters | C++ bytes / characters |
|---|---:|---:|---:|
| original | 3310 / 3310 | 6746 / 6746 | 17283 / 17283 |
| new_external | 10921 / 10921 | 19024 / 19024 | 40739 / 40739 |
| combined | 14231 / 14231 | 25770 / 25770 | 58022 / 58022 |

All authored source files are ASCII, so bytes and characters coincide; fixture/runtime data may be Unicode/binary. NIL is shorter in bytes but costs more tokens than Python externally. Counting includes imports, helper functions, headers, I/O and whitespace; shared CLI adapters are excluded. File wrappers favour NIL on tiny pure exercises, while Python standard-library operations help on collections/text. No wrappers were removed after results.

## Per-task sizes and tokens

Cells are NIL / Python / C++; “—” is unsupported/unverified, never zero. G=Gemma, Q=Qwen, C=cl100k, O=o200k. Raw bytes, characters, tokens and source hashes are separately present for every task/language/tokenizer in the CSV.

| Task | Origin | Bytes / characters (N / P / C) | G tokens | Q tokens | C tokens | O tokens |
|---|---|---:|---:|---:|---:|
| ascii_upper | self-authored | 96/96 / 235/235 / 667/667 | 75 / 81 / 213 | 53 / 64 / 167 | 49 / 60 / 166 | 48 / 60 / 166 |
| ascii_lower | self-authored | 95/95 / 234/234 / 667/667 | 74 / 80 / 213 | 52 / 63 / 167 | 49 / 60 / 166 | 48 / 60 / 166 |
| rot13 | self-authored | 170/170 / 355/355 / 778/778 | 133 / 124 / 267 | 98 / 107 / 218 | 86 / 95 / 214 | 85 / 95 / 214 |
| invert_bytes | self-authored | 66/66 / 211/211 / 625/625 | 51 / 68 / 193 | 37 / 52 / 148 | 35 / 50 / 146 | 34 / 50 / 146 |
| reverse_bytes | self-authored | 82/82 / 193/193 / 556/556 | 60 / 60 / 169 | 44 / 44 / 127 | 44 / 44 / 127 | 43 / 44 / 127 |
| hex_encode | self-authored | 148/148 / 209/209 / 668/668 | 97 / 64 / 213 | 78 / 47 / 169 | 69 / 47 / 161 | 68 / 47 / 161 |
| count_newlines | self-authored | 96/96 / 230/230 / 617/617 | 64 / 75 / 191 | 50 / 56 / 144 | 49 / 56 / 144 | 48 / 56 / 144 |
| nonempty_lines | self-authored | 142/142 / 240/240 / 665/665 | 90 / 80 / 203 | 70 / 61 / 155 | 68 / 61 / 155 | 67 / 62 / 157 |
| normalize_crlf | self-authored | 168/168 / 211/211 / 698/698 | 108 / 70 / 231 | 85 / 51 / 181 | 83 / 51 / 181 | 83 / 51 / 181 |
| prefix_lines | self-authored | 121/121 / 346/346 / 671/671 | 75 / 119 / 219 | 62 / 93 / 171 | 61 / 93 / 171 | 61 / 93 / 171 |
| first_fields_csv | self-authored | 157/157 / 324/324 / 672/672 | 98 / 113 / 208 | 77 / 90 / 158 | 74 / 90 / 158 | 73 / 91 / 160 |
| sum_pairs | self-authored | 120/120 / 282/282 / 780/780 | 70 / 91 / 245 | 56 / 69 / 188 | 56 / 69 / 188 | 55 / 70 / 190 |
| sum_integers | self-authored | 100/100 / 245/245 / 689/689 | 61 / 78 / 211 | 47 / 58 / 162 | 47 / 58 / 162 | 46 / 58 / 164 |
| min_max | self-authored | 164/164 / 278/278 / 821/821 | 98 / 88 / 259 | 75 / 67 / 204 | 75 / 67 / 204 | 76 / 67 / 206 |
| dedupe_adjacent_lines | self-authored | 373/373 / 371/371 / 773/773 | 224 / 129 / 232 | 167 / 104 / 180 | 163 / 104 / 180 | 166 / 105 / 182 |
| running_report | self-authored | 139/139 / 262/262 / 715/715 | 75 / 91 / 233 | 58 / 72 / 183 | 58 / 72 / 183 | 58 / 73 / 183 |
| number_lines | self-authored | 161/161 / 341/341 / 706/706 | 93 / 118 / 217 | 74 / 94 / 167 | 72 / 94 / 167 | 71 / 95 / 169 |
| histogram_digits | self-authored | 220/220 / 328/328 / 766/766 | 142 / 106 / 257 | 111 / 86 / 206 | 106 / 84 / 204 | 105 / 85 / 204 |
| buffer_sum | self-authored | 100/100 / 333/333 / 905/905 | 61 / 103 / 277 | 47 / 76 / 208 | 47 / 76 / 208 | 46 / 76 / 211 |
| buffer_dot | self-authored | 195/195 / 447/447 / 1117/1117 | 140 / 151 / 362 | 104 / 120 / 280 | 104 / 120 / 280 | 103 / 120 / 282 |
| prefix_sums | self-authored | 123/123 / 369/369 / 827/827 | 74 / 115 / 254 | 57 / 89 / 196 | 57 / 89 / 196 | 56 / 89 / 198 |
| copy_file | self-authored | 25/25 / 187/187 / 535/535 | 15 / 57 / 162 | 10 / 42 / 122 | 10 / 42 / 122 | 10 / 42 / 122 |
| slice_file | self-authored | 151/151 / 304/304 / 760/760 | 103 / 98 / 236 | 74 / 73 / 186 | 72 / 73 / 186 | 73 / 73 / 186 |
| expand_tabs | self-authored | 98/98 / 211/211 / 605/605 | 63 / 68 / 189 | 48 / 50 / 148 | 48 / 50 / 148 | 48 / 50 / 148 |
| env_lookup | self-authored | — / 249/249 / 619/619 | — / 78 / 188 | — / 58 / 143 | — / 58 / 143 | — / 58 / 143 |
| ex_accumulate | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_acronym | external | 273/273 / 352/352 / 966/966 | 182 / 114 / 283 | 147 / 86 / 221 | 134 / 86 / 221 | 134 / 86 / 222 |
| ex_affine_cipher | external | 461/461 / 588/588 / 1566/1566 | 325 / 227 / 522 | 253 / 190 / 419 | 239 / 178 / 417 | 240 / 178 / 420 |
| ex_all_your_base | external | 330/330 / 728/728 / 1579/1579 | 230 / 233 / 504 | 170 / 188 / 401 | 170 / 188 / 401 | 168 / 190 / 403 |
| ex_allergies | external | 338/338 / 467/467 / 1071/1071 | 191 / 155 / 330 | 155 / 127 / 268 | 149 / 127 / 268 | 149 / 127 / 268 |
| ex_alphametics | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_anagram | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_armstrong_numbers | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_atbash_cipher | external | 296/296 / 414/414 / 1064/1064 | 205 / 149 / 338 | 159 / 123 / 272 | 148 / 113 / 272 | 148 / 113 / 272 |
| ex_baffling_birthdays | external | 260/260 / 336/336 / 895/895 | 190 / 108 / 272 | 132 / 84 / 206 | 131 / 84 / 206 | 132 / 84 / 208 |
| ex_bank_account | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_beer_song | external | 540/540 / 872/872 / 1802/1802 | 228 / 279 / 556 | 194 / 242 / 460 | 193 / 241 / 459 | 193 / 241 / 461 |
| ex_binary | external | 148/148 / 348/348 / 827/827 | 99 / 117 / 255 | 73 / 92 / 201 | 70 / 90 / 201 | 70 / 90 / 201 |
| ex_binary_search | external | 286/286 / 636/636 / 1311/1311 | 196 / 203 / 389 | 144 / 164 / 298 | 143 / 164 / 298 | 144 / 164 / 300 |
| ex_binary_search_tree | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_bob | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_book_store | external | 373/373 / 931/931 / 1996/1996 | 285 / 307 / 630 | 227 / 255 / 504 | 216 / 242 / 491 | 213 / 242 / 494 |
| ex_bottle_song | external | 586/586 / 773/773 / 1708/1708 | 268 / 252 / 532 | 236 / 219 / 443 | 235 / 219 / 443 | 235 / 219 / 445 |
| ex_bowling | external | 618/618 / 1353/1353 / 2226/2226 | 481 / 440 / 732 | 387 / 373 / 595 | 374 / 362 / 584 | 368 / 368 / 588 |
| ex_camicia | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_change | external | 524/524 / 919/919 / 1805/1805 | 384 / 289 / 569 | 281 / 234 / 448 | 281 / 234 / 448 | 282 / 235 / 450 |
| ex_circular_buffer | external | 431/431 / 915/915 / 1780/1780 | 309 / 255 / 541 | 250 / 198 / 418 | 250 / 198 / 418 | 251 / 199 / 422 |
| ex_clock | external | 196/196 / 367/367 / 995/995 | 131 / 127 / 331 | 98 / 103 / 263 | 88 / 96 / 256 | 88 / 96 / 256 |
| ex_collatz_conjecture | external | 145/145 / 447/447 / 847/847 | 102 / 146 / 275 | 73 / 119 / 217 | 73 / 119 / 217 | 75 / 120 / 218 |
| ex_complex_numbers | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_connect | external | 803/803 / 1075/1075 / 2034/2034 | 660 / 364 / 662 | 470 / 317 / 545 | 463 / 312 / 545 | 459 / 314 / 548 |
| ex_crypto_square | external | 375/375 / 584/584 / 1223/1223 | 273 / 190 / 388 | 201 / 157 / 308 | 192 / 152 / 308 | 191 / 153 / 308 |
| ex_custom_set | external | 70/70 / 264/264 / 679/679 | 45 / 84 / 202 | 31 / 62 / 153 | 31 / 62 / 153 | 31 / 62 / 153 |
| ex_darts | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_diamond | external | 168/168 / 482/482 / 943/943 | 126 / 173 / 301 | 94 / 133 / 242 | 90 / 131 / 242 | 90 / 135 / 242 |
| ex_difference_of_squares | external | 105/105 / 307/307 / 739/739 | 64 / 101 / 229 | 49 / 77 / 178 | 49 / 77 / 178 | 49 / 77 / 178 |
| ex_diffie_hellman | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_dnd_character | external | 101/101 / 275/275 / 731/731 | 64 / 91 / 233 | 48 / 70 / 183 | 47 / 69 / 182 | 47 / 69 / 182 |
| ex_dominoes | external | 515/515 / 803/803 / 1829/1829 | 384 / 241 / 570 | 284 / 199 / 444 | 284 / 199 / 444 | 281 / 199 / 449 |
| ex_dot_dsl | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_eliuds_eggs | external | 101/101 / 275/275 / 784/784 | 66 / 86 / 244 | 47 / 63 / 189 | 47 / 63 / 189 | 47 / 63 / 189 |
| ex_etl | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_flatten_array | external | 223/223 / 556/556 / 1070/1070 | 157 / 158 / 328 | 115 / 120 / 254 | 110 / 120 / 254 | 108 / 121 / 254 |
| ex_flower_field | external | 362/362 / 772/772 / 1549/1549 | 299 / 255 / 484 | 225 / 207 / 399 | 218 / 204 / 399 | 216 / 207 / 401 |
| ex_food_chain | external | 928/928 / 1263/1263 / 2325/2325 | 389 / 380 / 648 | 357 / 332 / 538 | 357 / 332 / 538 | 356 / 329 / 536 |
| ex_forth | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_game_of_life | external | 370/370 / 774/774 / 1545/1545 | 304 / 262 / 494 | 231 / 215 / 410 | 223 / 211 / 410 | 221 / 214 / 412 |
| ex_gigasecond | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_go_counting | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_grade_school | external | 784/784 / 504/504 / 1219/1219 | 593 / 154 / 377 | 416 / 120 / 292 | 413 / 120 / 292 | 409 / 121 / 294 |
| ex_grains | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_grep | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_hamming | external | 161/161 / 397/397 / 972/972 | 115 / 132 / 302 | 84 / 101 / 234 | 83 / 101 / 234 | 84 / 101 / 234 |
| ex_hangman | external | — / — / — | — / — / — | — / — / — | — / — / — | — / — / — |
| ex_hello_world | external | 50/50 / 247/247 / 659/659 | 27 / 75 / 191 | 19 / 55 / 145 | 19 / 55 / 145 | 19 / 55 / 145 |

## Wins, ties and losses retained

| Cut | Tokenizer | Baseline | NIL wins | Ties | NIL losses |
|---|---|---|---:|---:|---:|
| original | gemma3_4b | python | 15 | 1 | 8 |
| original | gemma3_4b | cpp | 24 | 0 | 0 |
| original | qwen2.5_7b_instruct | python | 16 | 1 | 7 |
| original | qwen2.5_7b_instruct | cpp | 24 | 0 | 0 |
| original | cl100k_base | python | 17 | 1 | 6 |
| original | cl100k_base | cpp | 24 | 0 | 0 |
| original | o200k_base | python | 17 | 1 | 6 |
| original | o200k_base | cpp | 24 | 0 | 0 |
| new_external | gemma3_4b | python | 14 | 0 | 17 |
| new_external | gemma3_4b | cpp | 30 | 0 | 1 |
| new_external | qwen2.5_7b_instruct | python | 15 | 0 | 16 |
| new_external | qwen2.5_7b_instruct | cpp | 30 | 0 | 1 |
| new_external | cl100k_base | python | 15 | 0 | 16 |
| new_external | cl100k_base | cpp | 30 | 0 | 1 |
| new_external | o200k_base | python | 15 | 1 | 15 |
| new_external | o200k_base | cpp | 30 | 0 | 1 |
| combined | gemma3_4b | python | 29 | 1 | 25 |
| combined | gemma3_4b | cpp | 54 | 0 | 1 |
| combined | qwen2.5_7b_instruct | python | 31 | 1 | 23 |
| combined | qwen2.5_7b_instruct | cpp | 54 | 0 | 1 |
| combined | cl100k_base | python | 32 | 1 | 22 |
| combined | cl100k_base | cpp | 54 | 0 | 1 |
| combined | o200k_base | python | 32 | 2 | 21 |
| combined | o200k_base | cpp | 54 | 0 | 1 |

Every non-win is enumerated in the density JSON and visible above. Grade-school roster loses to both baselines under all four tokenizers: set/dedup/sort operations become positional buffer state and repeated key scans. On cl100k it is 413 NIL tokens versus 120 Python and 292 C++; on o200k 409 versus 121 and 294. Connect, dominoes, ciphers, circular state and decimal/padding logic contribute additional Python losses. These sources were not changed after counting.

## Unsupported tasks and generality catalogue

“Unsupported” is **not** uniformly a proven impossibility. Some contracts need missing primitives/integration; some algorithms could be byte/i64 emulations, but have no verified adapter in this corpus. Thus coverage gaps include engineering/library work as well as core language decisions. Baseline implementations for these 19 external tasks are also absent: their three rows are blank. Do not infer Python/C++ incapability or hide this conditional denominator.

| Task | Gap | Specific missing capability / adapter |
|---|---|---|
| env_lookup | environment | The v5 Host exposes only read/write/out, and the language has no environment lookup or external-call intrinsic. Identical files and arguments with differing environment values require differing outputs; the reference evaluator cannot observe that difference. Do not hardcode fixture values. |
| ex_accumulate | higher_order | The upstream collection/operator contract requires typed operation values and heterogeneous collections; neither is available in v5. |
| ex_alphametics | maps_records | The upstream result is a dynamically keyed assignment map/null. This corpus does not implement a hand-encoded mapping/search adapter; records/maps are absent. Algorithmic emulation is possible, not proven impossible. |
| ex_anagram | unicode | Unicode case-insensitive character comparison is required; no Unicode case database/operations are available. ASCII-only restriction would remove upstream cases. |
| ex_armstrong_numbers | integer_width | Upstream canonical property includes 108-bit and 127-bit Armstrong inputs, outside i64 parsing/arithmetic. Kept all such cases. Hand-rolled arbitrary-precision arithmetic is possible but not implemented. |
| ex_bank_account | concurrency | The published banking contract requires concurrent access to shared mutable account state; v5 has no threads/synchronization/shared-state ABI. |
| ex_binary_search_tree | recursive_values | The data property returns a recursive typed tree. Native recursive aggregate values are absent; a bespoke serialized-tree adapter is not implemented. This is an adapter gap, not a computability claim. |
| ex_bob | unicode | General Unicode letter/case/whitespace classification lacks standard Unicode operations/data; ASCII-only approximations are not claimed correct. |
| ex_camicia | nested_collections | Game cycle detection needs a set of variable-length deck states. No nested sequence/set representation; hand-encoded state simulation is not implemented. Emulation is possible. |
| ex_complex_numbers | floats | The real-part property accepts real-number complex components; v5 has no float type or parsing/formatting contract. |
| ex_darts | floats | Real Cartesian coordinates and squared-radius comparisons require floating-point semantics; integer-only restriction would remove upstream cases. |
| ex_diffie_hellman | entropy | The selected privateKeyIsInRange property generates a random private key; v5 Host has no randomness capability. Supplying a fixed key would change the task. |
| ex_dot_dsl | maps_records | The selected parse property returns graph/node/edge attribute maps; no typed maps/records or reusable parser adapter. Serialized emulation is possible but not implemented. |
| ex_etl | maps_records | Dynamic old/new score maps need a mapping adapter; no typed maps/records. Byte-encoded emulation is possible but not implemented. |
| ex_forth | dynamic_dictionary | Definitions and case-insensitive words require a runtime dictionary/code representation. A bespoke dictionary/interpreter is not implemented; this is a library/adapter gap, not theoretical impossibility. |
| ex_gigasecond | calendar | No date/time parsing/calendar arithmetic operation; a hand-written Gregorian adapter is not implemented. Integer/byte emulation is possible. |
| ex_go_counting | maps_records | Region result has an owner and collection of coordinate pairs. No typed multi-result/record representation; a serialized flood-fill adapter is not implemented. Emulation is possible. |
| ex_grains | integer_width | Square 64 yields 2^63, outside signed i64. No unsigned64/big-integer arithmetic/formatting. Hand-rolled decimal arithmetic could emulate it but is not implemented. |
| ex_grep | multi_file_fixture | Upstream multi-file flags/fixtures require a multi-file Host/runner contract; the current reusable corpus harness provisions a single input file. A packed emulation would change the I/O contract. |
| ex_hangman | reactive | Published task explicitly requires functional reactive programming/library integration. No first-class signals/events or integration ABI; a sequential transcript would not verify that requirement. |

| Gap | Blocked tasks | Tasks |
|---|---:|---|
| calendar | 1 | ex_gigasecond |
| concurrency | 1 | ex_bank_account |
| dynamic_dictionary | 1 | ex_forth |
| entropy | 1 | ex_diffie_hellman |
| environment | 1 | env_lookup |
| floats | 2 | ex_complex_numbers, ex_darts |
| higher_order | 1 | ex_accumulate |
| integer_width | 2 | ex_armstrong_numbers, ex_grains |
| maps_records | 4 | ex_alphametics, ex_dot_dsl, ex_etl, ex_go_counting |
| multi_file_fixture | 1 | ex_grep |
| nested_collections | 1 | ex_camicia |
| reactive | 1 | ex_hangman |
| recursive_values | 1 | ex_binary_search_tree |
| unicode | 2 | ex_anagram, ex_bob |

[Machine-readable gap catalogue](../../corpora/application-v5/GENERALITY_GAPS.json). No adapted task explicitly requires modules or recovering from host I/O failure: their observed blocking counts are zero, not evidence those features are implemented. Existing domain-error branches emit error bytes before traps; they do not provide recoverable I/O.

Supported awkwardness also remains: clock numeric padding and canonical parsing, circular-buffer multi-value metadata packed into buffers, repeated grade-school best-index/key calls, manual set/sort and grid-neighbor loops, character classification/grouping. Shared multi-result bindings, collection operations and Unicode facilities are findings for design work, not implemented here. Successful flattening/grid/graph cases show absence of records is not an absolute algorithmic barrier.

## Adaptation status and limits

**55 verified NIL programs / 55 exported JSONL records**: 24 original + 31 external, up 2.3× from the previous seed. The export includes source/verification hashes, origin/provenance and selected property for new tasks. Sources, tasks, frozen answers and license notices are committed; model assets, executables and generated exports stay outside the checkout. Rerun export.py or density.py to recreate JSONL.

This is still not an adaptation-scale dataset or evidence of successful fine-tuning. Against the earlier heuristic 500–2,000 independent verified tasks, it is roughly 9–36× too small. That range is a planning heuristic, not a model-specific data requirement or guarantee. Fifty exercise names deliver only 31 new positives; small API properties and related song/cipher/grid/reduction families reduce diversity further. Four original tasks overlap the prior generation study. Keep semantic-family holdouts, negative/repair trajectories and independently generated fixtures; never evaluate on adaptation targets.

The counts are deterministic for the published exact sources/tokenizers, not stochastic inference estimates. Task sampling is alphabetical and nonrandom; first-property ordering/curriculum bias, narrow byte adapters, locally authored baselines, finite oracles, differing algorithms and unsupported exclusions all limit generalization. No confidence interval here can turn this cohort into a representative sample. The observed reversal is real for this cohort; a universal superiority claim is not supported.

## Commands and archive

```sh
./scripts/ci.sh
benchmarks/paired/.venv/bin/python -m unittest discover -s benchmarks/corpora/application-v5/tests -v
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/verify.py --group original --output /tmp/nil-external/original-verification.json
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/verify.py --output /tmp/nil-external/verification.json
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/density.py --verification /tmp/nil-external/verification.json --output /tmp/nil-external/density
```

Outputs: CI 220 passed; corpus unit tests 10 passed; original 610 and combined 2,380 checks passed; 55 verified positives exported; four tokenizers with no Qwen cross-check mismatches. Raw logs, prior authoring failures, exact tables/pins and JSONL are archived externally:
`/Users/ninjacornix/.local/share/nil/benchmarks/archive/v5-external-density-2026-10-03.zip`
SHA-256 `293f6e778124818f4c938bc64b4a16681987876bf17ef5472290f2e95a08631c`.

Selection/contracts/verified sources were committed before observing token counts. No task/source/oracle/golden was changed after counts. Compiler/runtime/grammar/profiles/default and Rust dependency manifests are untouched. All commits are local; nothing pushed.
