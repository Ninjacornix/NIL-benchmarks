# Round 23 B2 — dependency-sliced guarded replay

**Natural qualification stays 19/150; tuned stays 22/150.** The 20–22 natural forecast missed. Balanced Binary Tree remains 111× C++, Course Schedule 196×, Validate BST 113× and Spiral 3.61×. G1, std swap/pop and native depth/stack safety are not implemented. Unbounded deep recursion can still signal instead of E008; Round 23 is not complete. Nothing was pushed.

Natural Last Stone Weight improves 25,180.46 → 60.94 ms without editing its frozen source, but remains 5.64× C++. The gain is compiler work, not a newly qualifying natural solution.

## Decision and soundness boundary

ADR 046’s dated B2 amendment (`2afaa70`) precedes compiler `9129976` and fuzz `4848a78`. A backward SSA slice covers every later local use of the original and all scalar dependencies, using semantic liveness’s operand/capture traversal. Only needed i64/bool observations are guarded and cached. Independent allocations, effects and updates remain at their original sites. The first replacement’s bounds/byte checks run before nontrapping probes. Any invalid/unsupported probe selects ordinary execution and copying.

Only complete guard success clears the original **owned local** root. Its slot is reserved through its old last use. Caller roots, returned aliases and aggregate child edges remain rooted; runtime uniqueness still copies for aliases. Escaping sequence uses and dependencies on a newly produced sequence remain conservative. No source-name, index or benchmark-shape recognizer was added. The inherited 128-site / 8-expansion-depth / 512-node limits and bounded budget execution remain conservative. G1 needs a separate returned-alias/child-provenance fixed point.

## Five cliffs: isolated 15-repeat warm timings

Times are whole-process milliseconds, min / median / max. All 29 admitted problems were measured with rotating natural/tuned/C++ order; all outputs and frozen source hashes were checked. No held-out problem was attempted. B1 medians are historical separate-session measurements, not a fresh paired comparison.

| Natural program | B1 median | B2 natural | B2 tuned | C++ | Natural/C++ |
|---|---:|---|---|---|---:|
| balanced-binary-tree | 1588.608 | 1496.452 / 1507.334 / 1561.072 | 26.414 / 27.325 / 28.841 | 12.998 / 13.545 / 15.068 | 111.28× |
| course-schedule | 4452.347 | 4252.784 / 4396.318 / 4529.201 | 40.676 / 41.331 / 41.681 | 21.820 / 22.441 / 23.649 | 195.90× |
| last-stone-weight | 25180.457 | 60.362 / 60.944 / 62.929 | 54.186 / 54.734 / 56.864 | 10.569 / 10.815 / 11.089 | 5.64× |
| spiral-matrix | 27.239 | 26.769 / 27.178 / 28.640 | 24.393 / 24.889 / 25.912 | 7.162 / 7.527 / 8.037 | 3.61× |
| validate-binary-search-tree | 1479.272 | 1437.158 / 1460.407 / 1510.473 | 22.811 / 23.730 / 24.694 | 12.418 / 12.972 / 13.674 | 112.58× |

## Physical payload-copy census

Native O0 mechanism counts are joined to reference logical versions, with REQUIRED meaning the original is read later in reference execution. Cached logical reads can remain REQUIRED while physical copies disappear. This is not an O2 copy count. Construction, input decoding, output materialization and growth relocation are separate categories in the JSON. Trace-capped joins and resource-inconclusive fixtures are retained and listed, not zero-copy successes.

| Scope | Programs before/after | Events before/after | Bytes before/after | REQUIRED bytes before/after | AVOIDABLE bytes before/after |
|---|---:|---:|---:|---:|---:|
| application | 68 / 68 | 8,034 / 8,034 | 157,613 / 157,613 | 26,310 / 26,310 | 131,303 / 131,303 |
| neetcode-natural | 29 / 29 | 5,890,907 / 4,213,644 | 1,741,354,909,621 / 400,057,333,597 | 1,581,298,251,755 / 240,000,675,731 | 160,056,657,866 / 160,056,657,866 |
| neetcode-tuned | 29 / 29 | 3,713,514 / 3,713,514 | 60,501,789 / 60,501,789 | 3,060,795 / 3,060,795 | 57,440,994 / 57,440,994 |
| fuzz-22001 | 687 / 701 | 5,265 / 5,285 | 81,120,423 / 81,120,531 | 81,092,592 / 81,092,688 | 27,831 / 27,843 |
| fuzz-22002 | 687 / 701 | 5,008 / 5,028 | 81,124,078 / 81,124,186 | 81,092,592 / 81,092,688 | 31,486 / 31,498 |

The application scope is exactly unchanged. Natural copied payload falls 77.0%; REQUIRED bytes fall 84.8% and REQUIRED events 84.1%, while AVOIDABLE bytes/events are exactly unchanged. The forecast was 60–90% REQUIRED-byte reduction (met), 30–70% REQUIRED-event reduction (exceeded), and 0–10% AVOIDABLE reduction (zero). The positive byte result does not override the missed natural-qualification forecast.

Fuzz census uses the same seeds 22001/22002 as B1, fixed census host fixtures and bounded native execution. It measures compatibility, not the unbounded G2 fast path. B2 adds fourteen families, so whole-scope fuzz totals have different denominators; compare common source hashes separately, not shifted family indices. Main differential seeds 23501/23502 use unbounded v5 O0/O2 builds and compare host effects.

Exactly **674 source-hash-matched cases per census seed** have identical before/after native totals: seed 22001 has 5,264 events / 81,120,407 bytes; seed 22002 has 5,007 / 81,124,062 bytes. Thirteen acquisition-fault sources change when their global family indices shift; they are explicitly unmatched, not normalized into a paired result. Fourteen new families also change the whole-scope denominator. Each census excludes 36 clean E013-inconclusive fixtures. Both NeetCode censuses exclude the same largest 3sum native join (6,745,501 events exceeds the five-million trace cap); timings and correctness still include that fixture.

## Historical controls: fresh paired 25-repeat run

Warm whole-process milliseconds, min / median / max. B1 `da7f64c` was archived and built with the same toolchain. Counter builds are excluded from timing/RSS. Byte-exact transform and double-transform round-trip passed. The historical scan input is **17 MiB**, not 16 MiB. No samples/outliers were dropped.

| Workload | Paired B1 | B2 | C++ |
|---|---|---|---|
| append | 4.123 / 4.315 / 5.303 | 4.167 / 4.304 / 4.992 | 3.263 / 3.354 / 4.318 |
| scan | 6.995 / 7.271 / 8.737 | 7.087 / 7.265 / 7.985 | 9.659 / 9.878 / 58.089 |
| transform | 34.915 / 38.118 / 42.394 | 34.620 / 37.025 / 40.490 | 13.530 / 17.869 / 31.940 |

All three control IR files are byte-identical before/after; B2 changes no runtime C. Their timing differences are not credited as optimizer gains. Wide transform ranges remain visible; the old absolute drift is not reattributed to this patch.

## Remaining-copy explanations

The opt-in copy hints still report nullable `keeping_read`, separate `retaining_use` and a retention reason. Largest-fixture runs preserved byte-exact output; hints are one exemplar per static site/kind, not dynamic totals.

| Natural case | Remaining copy site | Keeping read | Retaining use | Reason |
|---|---|---|---|---|
| Balanced Binary Tree | `[c-1:a[3+3*d]]` | null | `[c-1]` | live-root-retention |
| Course Schedule | `[c:b.counts[c]-1]`, `[b.tail:c]` | null | `?` | live-root-retention |
| Validate BST | `[c:d]` | null | `?` | live-root-retention |

These roots belong to callers/parent scopes or aggregate retention, not the owned local slot B2 may retire. A null keeping read does not establish permission to drop them. The balanced-tree forecast assumed a broader root-handoff benefit than this proof supplies; its measured 1,507 ms misses the 20–80 ms forecast. The course forecast of 500–4,500 ms technically contains 4,396 ms, but there is no material improvement. BST and Spiral stay within the ±10% forecast. Heap 60.94 ms meets its 40–250 ms forecast. This is a compiler proof boundary, not a claim that the avoidable copies are inherently unavoidable.

## Peak RSS

MacOS `/usr/bin/time -l`, three samples per binary, uninstrumented; medians in MiB. The guard is managed storage, not RSS. Full ranges, guard headroom and all cohort results are in the JSON. Course RSS remains elevated versus Round 22 (15.44 → 18.48 MiB); it is essentially unchanged from B1 (18.47 MiB), not a new B2 regression.

| Natural cliff | B1 RSS | B2 RSS | C++ RSS |
|---|---:|---:|---:|
| balanced-binary-tree | 7.78 | 7.78 | 11.20 |
| course-schedule | 18.47 | 18.48 | 13.31 |
| last-stone-weight | 6.81 | 3.73 | 4.52 |
| spiral-matrix | 4.59 | 4.59 | 6.09 |
| validate-binary-search-tree | 7.02 | 5.47 | 8.66 |

## Gates and findings

| Command | Final result |
|---|---|
| `./scripts/ci.sh` | 545 tests; zero Clippy warnings |
| `./scripts/ci.sh release` | 545 tests; zero Clippy warnings |
| `./scripts/sanitize.sh` | 246 tests; no ASan/UBSan findings |
| `./scripts/fuzz-v5.sh --seed 23501` | All 701 families; 1,402 native builds; zero non-E013 divergences; 88 inconclusive comparisons |
| `./scripts/fuzz-v5.sh --seed 23502` | Same coverage/counts; independent seed |
| `audit_read_order.py --repeats 3 --require-parity` | 14 families; 72 exact / 96 inconclusive comparisons; zero diagnostic divergences |
| Application `verify.py` | 2,815 checks; zero inconclusive |
| Application `verify.py --group original` | Exactly 610 checks; zero inconclusive |
| NeetCode `verify.py --verified-only` | 1,070 tuned checks |
| NeetCode `verify.py --candidate-dir .../natural` | 1,070 natural checks |

Commands, raw-log SHA-256 hashes, compiler patch receipt, counters and per-program copy data are in `ROUND23_B2.json`. Raw logs/programs/binaries remain outside git at `~/.local/share/nil/round23-memory/ordinary-b2/`. The committed compiler/fuzzer diff matches the gated/measured patch exactly. Frozen tasks, fixtures, goldens, baseline sources and verified NIL programs were not edited. Intrinsic count stays **35**.

Each seed: reference OK=515, E009=8, E012=29, E013=44, E014=11, E015=12, E016=14, E017=10, E018=11, E019=3, E020=6, E021=35, E022=3; E008=0. Native O0 and O2 each: OK=516, E013=43; other counts identical. Clean E013 on either side is inconclusive, never a divergence-free semantic success. Signals, malformed diagnostics and sanitizer output still fail.

Fourteen new G2 families cover multi-update slices, independent allocation/effects, bad later reads/updates/bytes, live caller and parent aliases, new-sequence dependencies, mutual recursion, loops, nested lazy arms, escapes and Buffer variants. Every family executes once per seed; the JSON retains all 43 G2 family counts. Each campaign has 693 distinct source hashes; the pair has 785, with 601 shared. Fixed witnesses and changed constants are not unrestricted structural diversity. E008/unbounded stack-exhaustion coverage remains mandatory B4 work.

Initial test failures exposed stale copy-hint expectations and a malformed new fuzz fixture declaring a record inside the entry body. The all-family typing test caught the fixture; it now uses the existing Cell. An IR counterexample also prompted rejecting dependencies on the first updated sequence result. No unexplained compiler divergence or sanitizer finding occurred. Corrected final gates, not those failed attempts, are cited above.

## Code inventory and rerun commands

B1's removal inventory and its missed net-deletion forecast remain in the B1 report. B2 removes no further quota-only machinery; it adds a general analysis and regressions. Diff `2afaa70..4848a78`:

| Component | Added / removed | Net |
|---|---:|---:|
| LLVM emitter/ownership/replay source | 68 / 18 | +50 |
| LLVM regression tests | 46 / 7 | +39 |
| CLI regression tests | 5 / 1 | +4 |
| Fuzz generator | 15 / 1 | +14 |
| Runtime C, evaluator, parser, std | 0 / 0 | 0 |

Run serially from the NIL root, with Clang 21 / Rust 1.98.1 used here. Outputs stay outside the checkout. Do not overlap timing/RSS with CI, fuzz or census work.

```sh
nil_b2_out=/tmp/nil-b2-recheck
mkdir -p "$nil_b2_out"
./scripts/ci.sh
./scripts/ci.sh release
./scripts/sanitize.sh
./scripts/fuzz-v5.sh --seed 23501 --out "$nil_b2_out/fuzz-23501"
./scripts/fuzz-v5.sh --seed 23502 --out "$nil_b2_out/fuzz-23502"
python3 benchmarks/core-memory-study/audit_read_order.py --out "$nil_b2_out/read-audit" --repeats 3 --require-parity
python3 benchmarks/corpora/application-v5/verify.py --output "$nil_b2_out/corpus.json"
python3 benchmarks/corpora/application-v5/verify.py --group original --output "$nil_b2_out/original.json"
python3 benchmarks/corpora/neetcode150/verify.py --verified-only --jobs 1 --output "$nil_b2_out/tuned.json"
python3 benchmarks/corpora/neetcode150/verify.py --verified-only --jobs 1 --candidate-dir "$PWD/benchmarks/core-generalize-study/natural" --output "$nil_b2_out/natural.json"
mkdir -p "$nil_b2_out/baseline"
git archive da7f64c | tar -x -C "$nil_b2_out/baseline"
(cd "$nil_b2_out/baseline" && cargo build --release --locked --offline -p nil)
python3 benchmarks/core-generalize-study/measure_controls.py --repeats 25 --baseline-compiler "$nil_b2_out/baseline/target/release/nil" --baseline-revision da7f64c --output "$nil_b2_out/controls.json"
python3 benchmarks/core-generalize-study/measure_cohort.py --repeats 15 --output "$nil_b2_out/cohort.json"
python3 benchmarks/core-generalize-study/reference_profile.py --copies --output "$nil_b2_out/overlay"
for scope in application neetcode-natural neetcode-tuned fuzz:22001 fuzz:22002; do
  python3 benchmarks/core-generalize-study/copy_census.py --overlay "$nil_b2_out/overlay" --scope "$scope" --native --output "$nil_b2_out/census-${scope/:/-}.json"
done
```

The measured compiler/fuzzer commits are `9129976` / `4848a78`; later report-only commits do not alter them. The actual run used the preregistration commit plus the hash-verified uncommitted patch for the overlay. A committed-tree rerun no longer needs `--working-tree`.

## Remaining boundary

G1 is deferred; no caller/parent root is released based on diagnostics. Std swap/pop and configurable call depth/verified native stack safety remain open. The default unbounded recursion SIGSEGV is a known defect, not a passed guarantee. Limits 128/8/512 deliberately select copying beyond the replay proof. No claims about density, new language capability or Core 1.0 completion follow from this step.
