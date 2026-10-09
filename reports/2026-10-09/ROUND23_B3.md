# Round 23: flat sequence swap/pop (B3)

**Unfavourable finding:** the within-10% std/caller forecast missed for all four controls. Swap is 3.54–3.83× slower, pop 1.80–1.88× slower. Natural qualification stays 19/150; tuned stays 22/150. B4 is not implemented: default unbounded deep recursion can still signal instead of E008. Round 23 remains incomplete. Nothing was pushed.

## Design and correctness

ADR 046 preregistered this step before code. `!swap` and `!pop` are validated NIL-source std functions for Bytes/Buffer; no intrinsic was added (35 remain). Swap evaluates call arguments left to right, reads/checks j then i before either write, and returns the exchanged sequence. Pop returns the shortened sequence, not the removed element; empty input reports E012. Source-callee diagnostic spans remain the ordinary std/module convention.

The existing last-use analysis selects a generic flat unique slice path. It synchronizes roots and checks bounds before mutation; a non-unique value copies. Offset slices use overlapping-safe memmove, then change length, preserving capacity. Caller aliases, map/record children and parent roots remain authoritative. Record buffers retain their separate child-aware copying path. Record-buffer swap/pop is deferred rather than weakening child-edge proofs.

## Tokens

tiktoken 0.12.0; both cl100k_base and o200k_base give the same counts:

| Surface | Tokens |
|---|---:|
| `!swap(a,b,c)` | 6 |
| `a[b:a[c]][c:a[b]]` | 9 |
| `!pop(a)` | 4 |
| `!slice(a,0,#a-1)` | 10 |
| `!remove_last(a)` | 5 |

No frozen program was rewritten. Natural Last Stone Weight has one direct heap-swap candidate; there are no direct physical-pop candidates (its heap stores logical size separately).

## Std boundary measurement

1,048,576 iterations, O2, one discarded warm-up, 25 rotating process-wall-time samples; all outputs checked. No C++ comparison is claimed for these small boundary controls. Sources and hashes are in the JSON.

| Type / operation | Std min / median / max ms | Caller min / median / max ms | Median ratio |
|---|---:|---:|---:|
| bytes swap | 23.717 / 24.390 / 42.360 | 6.257 / 6.371 / 18.355 | 3.83× |
| bytes pop | 12.577 / 12.866 / 24.027 | 6.629 / 6.861 / 19.285 | 1.88× |
| buffer swap | 23.445 / 23.745 / 39.679 | 6.557 / 6.715 / 19.911 | 3.54× |
| buffer pop | 13.276 / 13.559 / 23.945 | 7.305 / 7.517 / 23.858 | 1.80× |

Both operations have tested in-place paths; this is remaining source-callee/root bookkeeping overhead, not evidence of payload copying on the unique witnesses. The HIR std leaf inliner accepts a restricted linear single-expression form; pop contains length/arithmetic/slice and swap contains repeated parameter reads and updates, so neither qualifies. No new shape-specific inliner was added to rescue the forecast. The raw lowered IR has two root frames for std versus one for the caller, with 19 versus 10 root-store calls for swap and 15 versus 11 for pop (both sequence types). Both forms select the unique update helpers. These are whole-module static counts, not dynamic O2 costs; IR hashes and commands are in the JSON. Exact attribution of the residual instruction cost is not established by wall time alone.

## Historical controls and RSS

25 rotating warm repeats, measured alone after validation. The paired before compiler is an archived build of 73dbc79. Scan input is the historical **17 MiB**, not 16 MiB. Transform output and double-transform round trip are byte-exact. RSS uses three separate `/usr/bin/time -l` runs.

| Control | Before median ms | After min / median / max ms | C++ min / median / max ms | After / before | NIL / C++ RSS MiB |
|---|---:|---:|---:|---:|---:|
| append | 4.440 | 4.286 / 4.468 / 5.775 | 3.219 / 3.481 / 4.676 | 1.006 | 2.67 / 3.59 |
| scan | 7.726 | 7.445 / 7.798 / 8.304 | 10.116 / 10.396 / 11.164 | 1.009 | 18.61 / 18.61 |
| transform | 36.542 | 35.167 / 36.295 / 47.463 | 12.942 / 14.229 / 25.503 | 0.993 | 17.62 / 17.62 |

No material regression in these controls is demonstrated. Absolute timings from older rounds are not an isolated causal comparison; the fresh paired baseline is used.

## Frozen natural cliffs

15 rotating warm repeats at unchanged largest fixtures. All 29 admitted programs retain correctness; 114 held-out problems remain unattempted. Full per-program timing/RSS and source hashes are in the JSON.

| Problem | Before natural median ms | Natural min / median / max ms | Tuned min / median / max ms | C++ min / median / max ms | Natural / C++ |
|---|---:|---:|---:|---:|---:|
| balanced-binary-tree | 1507.334 | 1527.993 / 1549.636 / 1672.874 | 27.362 / 27.932 / 29.043 | 13.244 / 14.323 / 16.161 | 108.19× |
| course-schedule | 4396.318 | 4404.733 / 4491.148 / 4733.228 | 41.875 / 42.700 / 46.701 | 22.676 / 23.371 / 24.570 | 192.17× |
| last-stone-weight | 60.944 | 61.680 / 62.068 / 63.000 | 55.497 / 55.795 / 56.806 | 10.949 / 11.169 / 11.395 | 5.56× |
| spiral-matrix | 27.178 | 27.391 / 27.749 / 29.231 | 25.175 / 25.551 / 27.786 | 7.442 / 7.794 / 8.135 | 3.56× |
| validate-binary-search-tree | 1460.407 | 1463.900 / 1485.749 / 1537.757 | 23.647 / 24.325 / 25.131 | 12.645 / 13.441 / 14.173 | 110.54× |

## Copy census

An audit found that the first overlay missed the in-place offset-slice memmove. The overlay now counts actual nonzero-offset moves as slice payload traffic; zero-offset truncation remains zero copies. Eighteen copy-harness tests pass, including a regression for this hook. The affected programs were rerun: emitted IR proves absence of the new move in unselected programs; unresolved standalone plugin contexts were conservatively selected. Merging requires identical source hashes and unchanged reference groups/kinds. The JSON records selection, old/rerun/merged hashes and corrected totals; preliminary undercounted totals are not presented as the result.

Native O0 mechanism census joined to reference versions. This measures physical payload copies, not all allocator or O2 traffic. REQUIRED/AVOIDABLE classification follows the existing strict protocol. Totals include every admitted fixture except the explicitly listed resource inconclusives and pre-existing largest-3sum trace-cap exclusions. Timing/correctness still include 3sum.

| Scope | Before events / bytes | After events / bytes | After REQUIRED events / bytes | After AVOIDABLE events / bytes |
|---|---:|---:|---:|---:|
| application | 8,034 / 157,613 | 8,027 / 157,594 | 2,017 / 26,310 | 6,010 / 131,284 |
| neetcode-natural | 4,213,644 / 400,057,333,597 | 3,920,307 / 400,057,040,260 | 317,417 / 240,000,675,731 | 3,602,890 / 160,056,364,529 |
| neetcode-tuned | 3,713,514 / 60,501,789 | 3,420,177 / 60,208,452 | 17,359 / 3,060,795 | 3,402,818 / 57,147,657 |
| fuzz-22001 | 5,285 / 81,120,531 | 5,288 / 81,120,515 | 261 / 81,092,702 | 5,027 / 27,813 |
| fuzz-22002 | 5,028 / 81,124,186 | 5,030 / 81,124,146 | 261 / 81,092,702 | 4,769 / 31,444 |

fuzz-22001: 652 hash-matched completed common sources; before 5,284 events / 81,120,515 bytes, after 5,278 / 81,120,464. Shifted acquisition cases/new cases change the denominator; unpaired totals are not an optimization-effect estimate.

fuzz-22002: 652 hash-matched completed common sources; before 5,027 events / 81,124,170 bytes, after 5,020 / 81,124,095. Shifted acquisition cases/new cases change the denominator; unpaired totals are not an optimization-effect estimate.

## Gates and coverage

| Command | Result |
|---|---|
| `./scripts/ci.sh` | 551 tests, zero warnings |
| `./scripts/ci.sh release` | 551 tests, zero warnings |
| `./scripts/sanitize.sh` | 250 tests, no findings |
| `./scripts/fuzz-v5.sh --seed 23601` | 715 indexed cases, 1,430 native builds, zero non-E013 divergences, 88 resource-inconclusive comparisons |
| `./scripts/fuzz-v5.sh --seed 23602` | Same counts, independent seed |
| `audit_read_order.py --repeats 3 --require-parity` | 14 families; 72 exact / 96 resource-inconclusive; zero diagnostic divergences |
| Application `verify.py` | 2,815 checks, zero inconclusive |
| Application `verify.py --group original` | Exactly 610 checks, zero inconclusive |
| NeetCode tuned and natural verification | 1,070 checks each, zero inconclusive |

Every seed executes the full indexed schedule, including 14 new swap/pop/slice families. Native comparison uses O0/O2 unbounded application builds and checks host effects and diagnostic code/span. E013 on either side is inconclusive. E008 count is zero: no native stack-safety claim follows from these campaigns. Each seed has 707 distinct source hashes; union 799, intersection 615. This is structured witness coverage plus seeded constants, not unrestricted grammar diversity.

| Code | Reference, each seed | Native O0, each seed | Native O2, each seed |
|---|---:|---:|---:|
| Code | Reference per seed | Native O0 per seed | Native O2 per seed |
|---|---:|---:|---:|
| E008 | 0 | 0 | 0 |
| E009 | 8 | 8 | 8 |
| E012 | 33 | 33 | 33 |
| E013 | 44 | 43 | 43 |
| E014 | 11 | 11 | 11 |
| E015 | 12 | 12 | 12 |
| E016 | 14 | 14 | 14 |
| E017 | 10 | 10 | 10 |
| E018 | 11 | 11 | 11 |
| E019 | 3 | 3 | 3 |
| E020 | 6 | 6 | 6 |
| E021 | 35 | 35 | 35 |
| E022 | 3 | 3 | 3 |
| OK | 525 | 526 | 526 |

Per-code, per-index and per-named-family counts are retained in the JSON (533 named family labels with 660 executions; the other 55 are base cases). Raw log hashes and command receipts are retained alongside the archived artifacts.

## B4 admission remains open

The current compiler was rechecked on the reported 200,000-deep bytes-building recursion: unbounded O0 and O2 both terminate with signal 11 and no diagnostic; bounded O0/O2 return E008 @40..46. Commands and exit statuses are in the JSON. This defect is not an accepted clean failure or an E013 inconclusive.

An isolated Clang probe with LLVM `warn-stack-size=0` reports a 32,800-byte machine frame at O0/O2, including after LTO. This is a useful mechanism, not a complete stack-safety proof. Existing unbounded linear HIR expansion erases source call boundaries, and guarded replay expands scalar calls; simply enabling function-entry counters would not establish reference-equivalent call depth. The pre-call frame bound, source-call guards through these transformations, private stack and deep/large-frame sanitizer tests remain required before B4 can ship. No partial depth implementation is committed.

## Findings and accepted boundaries

The census instrumentation omission was found and corrected before publishing these totals. The final compiler gates found no non-E013 divergence or sanitizer finding. During test development, a full-message comparison was narrowed to the specified code/span because existing reference/native slice wording differs. A benchmark fixture initially used invalid `(i)` rather than numeric arity; a copy probe initially selected the wrong entry. Corrected preflight fixtures were rerun; these were harness errors, not compiler bugs.

G1 caller/returned-alias/child provenance remains unproved; escaping sequence uses and unsupported replay dependencies stay conservative. Record-buffer truncation is deferred. Swap/pop std call overhead is a measured miss, not accepted as C++ parity. Unbounded native stack safety and configurable depth remain unresolved B4 work. Round 23 is not complete.

Reproduction: `python3 benchmarks/core-memory-study/measure_updates.py --repeats 25 --output /tmp/std-updates.json`; controls/census commands are in the archived measurement receipts. Raw artifacts remain outside git at `/Users/ninjacornix/.local/share/nil/round23-memory/ordinary-b3`; only summarized results and hashes are committed.
