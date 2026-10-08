# Round 23 — Ordinary memory: B1 checkpoint

**The ownership cliffs and unbounded recursion crash are not fixed in B1.**
B2 replay admission, B3 swap/pop and B4 configurable depth/stack safety remain
unimplemented. This is a completed removal step, not a completed Round 23.
No natural or frozen program was rewritten, no held-out task attempted, nothing pushed.

ADR 046 was preregistered in `f362c22`, literal admission in `e5b0121`, and the
independent-review safety amendment in `afc5d51`, before implementation.
Allocation failure is environmental. The managed-storage guard defaults to
256 MiB, selectable through `Limits.memory_bytes`, `Options.memory_bytes` and
`--memory-limit BYTES|NMiB`; 0 disables it. This is not a process RSS bound or a
promise to recover from OS termination/Rust allocator abort.

## Removal inventory and forecast

The binding itemized inventory and converted test/fuzz list are in ADR 046.
Removed prospective copied-result reservations on unique updates/sort/map/record
paths, virtual stack-singleton charges/release calls, and future-copy growth caps.
Guard actual allocation and growth instead. KEEP roots, child retention, deferred
reconciliation, recycled slots, identity/alias tracking, SSA pruning, collection
heuristics and checked size arithmetic: these also serve memory safety/immutability.
No ledger or descriptors. The old 64 MiB byte-literal validator used E008 for a
resource ceiling; it was removed as preregistered, keeping representable-length
validation. Compiler/parser budgets remain independent.

The forecast of **150–350 net lines removed missed**. Most bookkeeping was not
quota-only; guard/API plumbing and fail-closed testing add lines. Positive net =
added. All changed files, including new test/report files, are in the JSON.

| Component | Added | Removed | Net |
|---|---:|---:|---:|
| documentation | 315 | 202 | +113 |
| other | 2 | 2 | +0 |
| CLI API | 22 | 0 | +22 |
| Rust tests | 613 | 124 | +489 |
| reference evaluator/API | 142 | 75 | +67 |
| HIR | 7 | 3 | +4 |
| native runtime | 30 | 50 | -20 |
| emitter | 0 | 9 | -9 |
| native API | 17 | 4 | +13 |
| differential fuzzer | 131 | 17 | +114 |

## Natural qualification and five cliffs

Previous: **19/150 natural, 22/150 tuned**. Current: **19/150 natural, 22/150 tuned**. Only the 29 admitted programs were timed, 15 repetitions each, same original largest fixtures and algorithm-class C++ references. No rewrite receives natural credit.

| Natural problem | Round 22 median ms | B1 min/median/max ms | C++ min/median/max ms | Ratio |
|---|---:|---:|---:|---:|
| last-stone-weight | 24962.076 | 24723.499/25180.457/26926.139 | 10.895/11.708/12.875 | 2150.78× |
| balanced-binary-tree | 1535.545 | 1523.905/1588.608/1863.820 | 13.507/14.482/16.535 | 109.70× |
| course-schedule | 4508.621 | 4204.681/4452.347/4776.838 | 22.071/22.641/29.342 | 196.65× |
| validate-binary-search-tree | 1465.216 | 1447.034/1479.272/1593.641 | 12.236/13.260/16.112 | 111.56× |
| spiral-matrix | 27.892 | 26.725/27.239/28.260 | 7.137/7.533/12.937 | 3.62× |

| Cliff RSS | Round 22 natural MiB | B1 natural MiB | C++ MiB | B1/C++ |
|---|---:|---:|---:|---:|
| last-stone-weight | 6.81 | 6.81 | 4.52 | 1.51× |
| balanced-binary-tree | 7.69 | 7.78 | 11.20 | 0.69× |
| course-schedule | 15.44 | 18.47 | 13.31 | 1.39× |
| validate-binary-search-tree | 7.02 | 7.02 | 8.66 | 0.81× |
| spiral-matrix | 4.59 | 4.59 | 6.09 | 0.75× |

No G2 fallback was lifted and G1 remains unproved: returned/child aliases still
need provenance. Timing variation does not demonstrate an ownership improvement.
The complete 29-program timing/RSS/guard table is in the JSON.

## Copy census

All application/natural/tuned reference and native group totals match corrected
Round 22 exactly. Native O0 payload numbers below; REQUIRED uses the stricter
semantic retention classification. They are physical copy traffic, not RSS.

| Scope | Programs | Events | Bytes | REQUIRED events / bytes | AVOIDABLE events / bytes |
|---|---:|---:|---:|---:|---:|
| application | 68 | 8,034 | 157,613 | 2,017 / 26,310 | 6,017 / 131,303 |
| natural | 29 | 5,890,907 | 1,741,354,909,621 | 1,994,680 / 1,581,298,251,755 | 3,896,227 / 160,056,657,866 |
| tuned | 29 | 3,713,514 | 60,501,789 | 17,359 / 3,060,795 | 3,696,155 / 57,440,994 |
| fuzz-22001 | 687 | 5,265 | 81,120,423 | 240 / 81,092,592 | 5,025 / 27,831 |
| fuzz-22002 | 687 | 5,008 | 81,124,078 | 240 / 81,092,592 | 4,768 / 31,486 |

Fuzz census uses its fixed 1024-byte fixture, not campaign inputs. Each seed has
36 resource-inconclusive native joins (named in JSON), not zero-copy programs.
Against the 673-family corrected Round 22 archive, the 637 complete common
joins match exactly; the 14 added fault families account for one extra 16-byte
copy. The census fixture does not interpose faults; the separate fault campaign
and audit do. Census overlays predate the final direct-FileHost convenience-cap
fix and symmetric RHS assertion; the measured execution path uses read_with_limit,
and neither late change alters copying. Overlay manifests retain their patch hashes.

## Isolated timings and RSS

25 rotated warm repetitions, plain native O2 and the same Clang C++ O2, plus a
fresh archived `b23d0e9` compiler. Counters are separate binaries; RSS has three
separate samples per mode. Transform output and double-transform roundtrip are
byte-exact. Scan's historical input is **17 MiB**, not 16 MiB: the repeated line
has 17 bytes. No CI/fuzz/sanitizer/census work ran alongside timing.

| Control | Before min/median/max ms | B1 min/median/max ms | C++ min/median/max ms | B1/C++ | B1/C++ RSS |
|---|---:|---:|---:|---:|---:|
| append | 4.273/4.471/5.400 | 4.189/4.360/5.189 | 3.248/3.474/4.402 | 1.26× | 0.74× |
| scan | 7.202/7.563/7.984 | 7.204/7.526/7.999 | 9.913/10.205/11.091 | 0.74× | 1.00× |
| transform | 35.489/39.164/52.556 | 35.512/40.148/44.848 | 12.814/21.134/31.189 | 1.90× | 1.00× |

RSS, managed peak live storage, guard headroom and every raw sample are in JSON.
The counter samples live storage at reconciliation, not process RSS or an exact
allocator/transient maximum. No additional ledger bookkeeping was introduced.
Course Schedule RSS rose 15.44 → 18.47 MiB in the three-sample comparison;
this is reported rather than hidden behind unchanged copied bytes. The ordinary
model does not promise an exact RSS bound or unchanged allocator residency.
Absolute timing drift is not automatically attributed to this patch; the paired
before compiler and C++ controls show its machine/session dependence.

## Gates and resources

- `ci-debug-review`: **543 tests**, exit 0; zero warnings/findings.
- `ci-release-review`: **543 tests**, exit 0; zero warnings/findings.
- `sanitize-review`: **244 tests**, exit 0; zero warnings/findings.
- Corpus: **2,815** checks, original separately **610**, zero inconclusive checks; natural/tuned separately **1,070** each.
- Permanent 14-family fault audit: three repeats, `--require-parity`; resource-inconclusive cases are listed, non-resource output/code/span/receipts exact.

| Seed | Families / builds | Non-E013 divergences | E013 inconclusive comparisons | E008 |
|---|---:|---:|---:|---:|
| 23467 | 687 / 1374 | 0 | 88 | 0 |
| 23468 | 687 / 1374 | 0 | 88 | 0 |

Each seed has 679 distinct source hashes; their union is 771. Seeds mainly vary constants inside the fixed family matrix, not arbitrary grammar structure.

| Code | Seed 23467 reference / O0 / O2 | Seed 23468 reference / O0 / O2 |
|---|---:|---:|
| E008 | 0 / 0 / 0 | 0 / 0 / 0 |
| E009 | 8 / 8 / 8 | 8 / 8 / 8 |
| E012 | 27 / 27 / 27 | 27 / 27 / 27 |
| E013 | 44 / 43 / 43 | 44 / 43 / 43 |
| E014 | 10 / 10 / 10 | 10 / 10 / 10 |
| E015 | 12 / 12 / 12 | 12 / 12 / 12 |
| E016 | 14 / 14 / 14 | 14 / 14 / 14 |
| E017 | 10 / 10 / 10 | 10 / 10 / 10 |
| E018 | 11 / 11 / 11 | 11 / 11 / 11 |
| E019 | 3 / 3 / 3 | 3 / 3 / 3 |
| E020 | 6 / 6 / 6 | 6 / 6 / 6 |
| E021 | 35 / 35 / 35 | 35 / 35 / 35 |
| E022 | 3 / 3 / 3 | 3 / 3 / 3 |
| OK | 504 / 505 / 505 | 504 / 505 / 505 |

Per-code/backend, per-family, per-source-mutation counts and hashes are preserved
in the JSON. Clean E013 on either side is inconclusive, even matching failures;
no signals, malformed diagnostics or sanitizer output can be masked. Existing
negative-allocation-size checks also use E013; the all-E013 rule conservatively
marks those inconclusive too, rather than claiming semantic coverage. Host output,
written files and injected-fault receipts compare for non-resource outcomes.
**E008 depth coverage remains absent in these campaigns; B4 must add unbounded
stack-exhaustion families.** This report does not claim that review finding fixed.

A sparse-file regression fixes the direct FileHost helper's inherited 64 MiB cap.
A symmetric RHS-root assertion now protects concat's pre-realloc collection;
heap RHS, stack singleton and record-child regressions pass reference/O0/O2.
No assertion fired in the reported campaigns/sanitizers. The initial timing
wrapper failed because its destructor referenced the guard macro before definition;
it was fixed in the measurement harness, not by changing compiler semantics.
One earlier overloaded correctness run hit the Last Stone Weight reference timeout;
it remains an archived failure, not E013. Isolated reruns passed.

## Reproduction and remaining limits

```sh
./scripts/ci.sh
./scripts/ci.sh release
./scripts/sanitize.sh
./scripts/fuzz-v5.sh --seed 23467 --out /tmp/nil-r23-23467
./scripts/fuzz-v5.sh --seed 23468 --out /tmp/nil-r23-23468
python3 benchmarks/core-memory-study/audit_read_order.py --out /tmp/nil-r23-read --repeats 3 --require-parity
python3 benchmarks/corpora/application-v5/verify.py --output /tmp/nil-r23-corpus.json
python3 benchmarks/corpora/application-v5/verify.py --group original --output /tmp/nil-r23-original.json
python3 benchmarks/corpora/neetcode150/verify.py --verified-only --jobs 1 --output /tmp/nil-r23-tuned.json
python3 benchmarks/corpora/neetcode150/verify.py --verified-only --jobs 1 --candidate-dir benchmarks/core-generalize-study/natural --output /tmp/nil-r23-natural.json
python3 benchmarks/core-generalize-study/measure_controls.py --repeats 25 --output /tmp/nil-r23-controls.json
python3 benchmarks/core-generalize-study/measure_cohort.py --repeats 15 --output /tmp/nil-r23-cohort.json
```

Raw artifacts and their hashes: `~/.local/share/nil/round23-memory/ordinary-b1/`,
JSON `raw_manifest`. Generated binaries/traces/logs remain outside git. Frozen
inputs and verified NIL/Python/C++ programs are unchanged. The HIR intrinsic enum still has 35 entries; no new language surface. Swap/pop forecasts (6/4 tokens cl100k/o200k)
remain unimplemented. Current call depth 256 is unchanged, no configurable depth
or unbounded stack protection has shipped; the default recursion SIGSEGV remains
an explicit blocker. Other accepted limits: general returned/child provenance,
conservative G2 across allocating/sequence-valued regions, and builders with
live immutable aliases that still require copying. None is silently waived.
