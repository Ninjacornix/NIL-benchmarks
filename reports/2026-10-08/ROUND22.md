# Round 22 — guarded replay, with ownership still incomplete

**Natural qualification stays 19/150; tuned stays 22/150. No newly qualifying
program. G1 did not ship, and the full cross-frame copy-hint contract remains open.**
Natural copied payload falls 16.5%, but REQUIRED bytes fall only 17.9% against a
70–95% forecast. Natural Last Stone Weight still takes 24.46 s / 2,232x C++;
balanced tree and BST remain over 100x. Spiral Matrix improves 1,422.33 -> 27.31 ms
but still misses at 3.65x C++. These are compiler gaps, not successful qualifications.

G2 ships with guards and an ordinary-copy fallback. Tuned copied payload falls
105.6 GB -> 60.5 MB without further source edits, but the tuned heap remains
55.46 ms / 5.06x C++. General interprocedural ownership still needs a proof of
alias provenance and logical quota charges, not another source-shape recognizer.

Main starts at `92d62b3`, benchmarks at `84a20fc`; local branches are
`feat/core-ownership` and `exp/core-ownership`, with no upstreams and **nothing pushed**.
ADR 044 (`46c10fc`) precedes G2 (`d97b481`) and hints (`bce3d6e`). The repaired
fuzz baseline (`eab1320`, benchmarks `76af011`) precedes the ADR. Later benchmark
tracker corrections preserve the original forecasts and baseline artifacts.

## Qualification and five cliffs

Unmodified frozen Round 19 sources remain the headline. All 29 admitted natural
and tuned programs passed reference/native O0/O2; seven sampled blocked candidates
and 114 held-out problems were not attempted. Qualification sets are unchanged,
not merely their counts. No previously qualified program loses qualification or
shows more than 10% normalized median drift. Timing uses 15 rotating repetitions,
one warmup excluded, the same original largest fixture and same-algorithm C++;
RSS uses three separate `/usr/bin/time -l` runs. No CI/fuzz/census ran alongside.

All times below are ms. After columns are **min/median/max**.

| Natural problem | Before median | After | C++ after | After ratio | Tuned after |
|---|---:|---:|---:|---:|---:|
| last-stone-weight | 26904.111 | 24321.212/24463.637/24689.084 | 10.577/10.960/11.577 | 2232.00x | 54.581/55.460/57.091 |
| balanced-binary-tree | 1570.207 | 1477.509/1502.601/1553.562 | 12.826/13.248/14.116 | 113.42x | 26.303/26.796/27.811 |
| course-schedule | 7482.260 | 4167.232/4234.484/4427.805 | 21.568/22.130/22.778 | 191.34x | 40.689/41.007/41.687 |
| validate-binary-search-tree | 1467.230 | 1424.114/1443.241/1495.595 | 12.298/12.808/17.429 | 112.68x | 22.540/23.409/28.407 |
| spiral-matrix | 1422.327 | 26.944/27.314/28.382 | 7.162/7.479/8.068 | 3.65x | 24.588/25.160/26.574 |

Before medians are the frozen Round 21 campaign, not a simultaneous baseline run.
Same-session C++ ratios are more defensible than cross-day absolute speedups.
The complete 29-program timing distributions, source hashes, RSS and separate
observed-root-charge samples are in [ROUND22_COHORT.json](ROUND22_COHORT.json).
Native root-charge samples are **not** semantic liveness or quota headroom.

| Problem | Natural RSS MiB | C++ RSS MiB | Ratio | Tuned RSS MiB |
|---|---:|---:|---:|---:|
| last-stone-weight | 6.81 | 4.52 | 1.51x | 3.73 |
| balanced-binary-tree | 7.02 | 11.20 | 0.63x | 5.47 |
| course-schedule | 16.98 | 13.31 | 1.28x | 12.33 |
| validate-binary-search-tree | 5.47 | 8.64 | 0.63x | 5.36 |
| spiral-matrix | 4.59 | 6.09 | 0.75x | 4.58 |

## Census: native O0, strict observation metric

[ROUND22_CENSUS.json](ROUND22_CENSUS.json) includes per-program application/cohort
results, all category totals, source hashes, exclusions and raw-output hashes.
The table uses bytes, not GiB, and compares the same frozen scopes. AVOIDABLE
means no later reference observation; it does **not** prove a copy can be removed.
For example, appending an output element may still require a physical write.

| Scope | REQUIRED events | REQUIRED bytes | AVOIDABLE events | AVOIDABLE bytes |
|---|---:|---:|---:|---:|
| application before | 2,130 | 31,214 | 6,017 | 131,303 |
| application after | 2,017 | 26,310 | 6,017 | 131,303 |
| natural before | 2,526,935 | 1,926,575,088,147 | 3,896,307 | 160,059,871,794 |
| natural after | 1,994,680 | 1,581,298,251,755 | 3,896,227 | 160,056,657,866 |
| tuned before | 249,354 | 105,513,231,643 | 3,696,155 | 57,440,994 |
| tuned after | 17,359 | 3,060,795 | 3,696,155 | 57,440,994 |
| fuzz-22001 before | 216 | 58,722,907 | 5,024 | 29,387,957 |
| fuzz-22001 after | 216 | 58,722,907 | 5,024 | 29,387,957 |
| fuzz-22002 before | 216 | 58,722,907 | 4,767 | 29,391,612 |
| fuzz-22002 after | 216 | 58,722,907 | 4,767 | 29,391,612 |


The repaired fuzz baseline executes all 644 original programs for each seed.
Afterwards those exact 644 hashes and copy counts agree; bounded replay is off.
The 29 new families add 32 native copies / 22,369,714 bytes per seed, of which
25 / 22,369,686 bytes are REQUIRED and 7 / 28 bytes AVOIDABLE. This is added test
coverage, not a regression in frozen programs. Both censuses have zero skipped
or unjoinable fuzz cases and one bounded E008 per seed. New families must not be
mixed into the original baseline when calculating improvement.

Reference ledgers agree exactly before/after: application 7,595 events / 165,218 B;
natural 13,269,808 / 2,166,682,394,099 B; tuned 12,469,338 /
1,526,915,682,819 B. Fuzz originals: 5,528 / 197,172,225 B and
5,296 / 197,160,178 B. All REQUIRED/AVOIDABLE and payload-only cuts are retained
in the JSON. Ordinary and instrumented execution agree before accepting events.

Worst remaining natural native payload: heap 1,341,298,377,096 B; course
239,996,800,007 B; BST 80,000,016,879 B; balanced tree 80,000,014,943 B.
Spiral falls 79,770,871,628 -> 1,076,740 B. Application's entire reduction is
113 copies / 4,904 B in Dominoes; its AVOIDABLE traffic is unchanged.

## Forecasts versus actuals

| Forecast | Actual | Assessment |
|---|---|---|
| Natural qualification 20–21 | 19 | Miss |
| Natural REQUIRED bytes -70–95% | -17.92% | Major miss; quota barriers dominate |
| Natural REQUIRED events -40–85% | -21.06% | Miss |
| Natural AVOIDABLE bytes -0–20%, events -0–15% | -0.00201%, -0.00205% | In range but negligible; not G1 |
| Tuned payload bytes -50–95% | -99.94% | More than forecast, but not a natural success |
| Application events/bytes -0–15% | -1.39% / -3.02% | In range; small scope effect |
| Original fuzz categories -0–15% | 0% | Compatibility coverage, not G2 evidence |
| Heap 40–200 ms | 24,463.64 ms | Major miss |
| Balanced 20–50 ms | 1,502.60 ms | Major miss |
| Course 500–7,500 ms | 4,234.48 ms | In range, still 191x C++ |
| BST unchanged within 10% | 1,443.24 vs 1,467.23 ms | No G1 gain |
| Spiral 20–100 ms | 27.31 ms | Timing range met; qualification missed |
| Conditional G1 gains | No G1 shipped, zero gains claimed | Admission boundary, not an experiment result |

## What shipped and why it is a partial result

Replay covers i64/bool computation and Buffer/Bytes replacements; other numeric
types and fixed arrays retain their existing paths. G2 uses typed SSA intervals, not matched source strings or identical index expressions.
After the original update's own checks, it computes later scalar reads with guards,
retains the original roots, and caches successful results. Invalid probes execute
ordinary copying and reads in their original positions. Reads in selected nested
lazy arms and read-only callees are supported; effectful, allocating, unsupported,
recursive-budget-exhausted and result-dependent regions fall back. Expansion is
bounded to 512 operations and depth 8, with a 128-instruction interval bound.
These are compiler work bounds, not changes to NIL call or memory limits.
Bounded execution retains its operations, step/call counters and legacy captures.

G1 did not ship. A borrowing fixed point does not provide argument/returned-child
provenance or logical version charges. The live-parent witness in ADR 044 retains
an unread text child until a later scalar field read; removing that edge changes
E013. The second-update witness needs three simultaneous semantic capacities.
The current reserve-as-if-copying check accounts for only the next result, so it
cannot make sharing several still-live versions quota-equivalent. No narrower
callee matcher replaces the missing proof. These are boundaries of this implementation,
not claims that a logical-charge ledger or general ownership analysis is impossible.

| Obligation | G2 discharge | G1 status |
|---|---|---|
| Live aliases | Existing physical roots and uniqueness guard decide copying; replay changes no roots | Parameter/child provenance missing |
| Returned aliases | Replay caches scalars only; sequence results fall back | Returned origins not established |
| Lazy arms | Only selected branch probed; invalid operations cannot run effects | Union summaries insufficient for physical ownership |
| Recursion | Actual body guarded; depth/budget exhaustion falls back | No ownership fixed point admitted |
| Record/map children | Existing parent/child roots retained; child aliases still force copying | Root-edge provenance missing |
| Trap/effect order | Original update checks first; probes cannot trap or run effects; discarded operations also guarded | No scheduling or root surrender shipped |
| Quota | Reserve-as-if-copying unchanged; allocation/second-update barriers fall back | Logical charge/death proof missing |
| Deferred/recycled roots | Slot/mirror and observation protocols unchanged; no early root deletion | Handoff not proven |

This is an observational argument for the admitted replay subset plus fallback,
not a formal verification of the compiler. Tests cover reordered operands,
different indices, inline/bound expressions, nested conditionals, earlier/later
reads, call aliases, returned aliases, recursion/mutual recursion, record children,
map values, empty and zero-slot values, selected/unselected traps and host effects.

## Copy hints: useful but incomplete

```sh
target/release/nil --profile expr-v5 --unbounded --explain-copies run /tmp/example.nil
```

For `:s=b("abcd")` / `(s):s=a[0:90][1:a[2]][2:a[0]]`, stdout is `Zcad` and
stderr contains:

```json
{"kind":"replace","bytes":4,"span":[20,26],"keeping_read":[30,33],"precision":"direct-local-read"}
```

The runtime emits `NIL_COPY_HINT ` before each JSON record, once per successful
copy site. Default binaries contain no copy-site calls. Tests compare return code,
stdout, host effects and repeated diagnostics with/without hints at O0/O2.
A direct-local span identifies a later source/reference read; it is not proof that
this is the sole physical alias forcing the copy. Unknown interprocedural/child
provenance is null. Map extraction, LLVM aggregate copies and subsequent executions
of an already reported site are not exhaustively enumerated. The full Part D
keeping-read contract remains open; no invented keeping-read spans are supplied.

For `:s=b("abcd")` / `(s):s=a[0:90][1:a[2]]`, emitted IR changes from
one `nil_set`, one `nil_set_unique` and one `nil_get` to one `nil_set_replay_check`,
one `nil_set_replay`, one `nil_set_unique`, two guarded/fallback `nil_get` paths
and cached scalar phis. At native O0, the old compiler traces a four-byte `set`
copy; the new compiler traces no payload copy. Both return `Zccd`.

Exact emitted excerpts (omitted blocks are labelled, not reconstructed):

```llvm
; Before: update copies, then reads original
%v1 = call ptr @nil_set(ptr %p0, i64 0, i64 90, i64 20, i64 26)
%v3 = call i64 @nil_get(ptr %p0, i64 2, i64 30, i64 33)

; After: update's checks precede nontrapping guarded read
call void @nil_set_replay_check(ptr %p0, i64 0, i64 90, i64 20, i64 26)
; ... length phi and guard blocks ...
%v6 = icmp ult i64 2, %v5
%v7 = and i1 %v3, %v6
br i1 %v7, label %b4, label %b5
b4:
%v8 = call i64 @nil_get(ptr %p0, i64 2, i64 -1, i64 -1)
; ... merge validity and cached value ...
%v11 = call ptr @nil_set_replay(ptr %p0, i64 0, i64 90, i1 %v10, i64 20, i64 26)
; ... ordinary read remains in fallback block ...
%v16 = phi i64 [ %v9, %b14 ], [ %v15, %b13 ]
```


## Measurement integrity and remaining limits

The corrected fuzz census supplies the actual four argument types, explicit Host
fixtures and providers; E006 aborts rather than masquerading as coverage. It is
bounded to 100,000 steps/256 calls and therefore does **not** measure unbounded G2
improvements. Compare its original 644 sources separately from the 29 additions.
The differential campaigns and unbounded replay controls exercise G2.

A later instrumentation defect was found: fresh sequence/empty-map/decoded
aggregate storage could inherit an expired record version when an address was
reused. The measurement-only overlay now registers every birth. Three repeated
golden runs each of BST, BFS and interval merge classify identically; ten synthetic
Rust tracker tests and Python coverage checks pass. Retrospective corrected before
and after reference ledgers agree. In applications, four baseline classifications
(528 bytes) change; the three initially observed drifting events comprised 432 bytes.
Original preregistered forecasts and artifacts remain in history. This was a census
bug, not a compiler miscompile or a new source rewrite.

Native copy counts are O0 emitter-mechanism counts joined to reference observations,
not a claim about physical copies surviving O2. The existing five-million-event
native trace cap excludes the largest 3Sum fixture; reference counts still include
it and exclusion receipts remain explicit. Timings and RSS use separate plain O2
binaries and run after all owned CI/fuzz/census processes finish. No O2 copy census
is claimed. Qualification uses same-session C++ median <=3x; process timings include
startup and I/O. RSS is not live-charge liveness. The host is shared with ordinary
Mac applications; this is not a dedicated performance machine.

Accepted limits: G1 and full cross-frame hints remain unproved, replay cannot cross
quota/host-effect observations or unsupported scalar operations, bounded replay is
disabled to retain tick parity, and configurable limits/native stack safety remain
out of scope. No frozen source, task, fixture, oracle, golden or baseline changes;
no held-out problem attempted. No intrinsic, dependency, grammar or default-profile change.


## Historical controls and transform drift

25 rotating repetitions of **old compiler, new compiler and C++ interleaved**,
with no other owned heavy process. After separate-block runs showed C++ timing
drift too, this additional paired control was used to distinguish code changes
from block-to-block movement. No benchmark source or fixture was changed.
Append is 1 MiB, transform 16 MiB. The historical newline fixture is actually
**17 MiB**, despite earlier shorthand calling it 16 MiB.

All time triples are min/median/max ms; RSS is median MiB.

| Control | Round 21 BEFORE median | Old compiler now | New compiler now | C++ now | New/old | NIL/C++ | NIL/C++ RSS |
|---|---:|---:|---:|---:|---:|---:|---:|
| append | 5.589 | 4.248/4.413/4.909 | 4.313/4.573/5.051 | 3.126/3.388/4.142 | 1.036x | 1.350x | 2.67/3.59 |
| scan | 8.792 | 6.750/7.023/7.319 | 7.038/7.224/7.778 | 9.328/9.531/10.080 | 1.029x | 0.758x | 18.61/18.61 |
| transform | 39.495 | 34.586/35.735/96.996 | 35.181/36.335/40.607 | 12.475/13.252/14.349 | 1.017x | 2.742x | 17.61/17.62 |

Both single transforms are byte-exact and double transforms round-trip. The prior
+14% absolute transform drift is not established as a compiler regression: Round
21 made no compiler changes, and paired old/current control timing is stated above.
Current paired medians are +3.6% append, +2.9% scan and +1.7% transform versus
the old compiler. Ranges overlap; this is not a claim of zero overhead or proof
that the small increases are random. They do not reproduce the historical +14%.
The exact cause of cross-campaign absolute drift remains unidentified; it is not
labelled thermal noise without evidence. Separate current/old blocks measured
38.290/35.857 ms while C++ moved 14.451/13.333 ms in the same direction. Their
normalized NIL/C++ ratios differ by about -1.5%, demonstrating why comparing only
those absolute medians would misattribute movement. These controls, not census
elapsed time, are the performance evidence.

## Gates and differential coverage

Compiler codegen revision is `bce3d6e`; later `159d07c` adds the live-parent
quota witness inside an existing test. Later changes are measurement tooling and
documentation. [ROUND22_GATES.json](ROUND22_GATES.json) records full output hashes.

| Command | Output/result |
|---|---|
| `./scripts/ci.sh` | 520 tests, strict Clippy clean, exit 0 |
| `./scripts/ci.sh release` | 520 tests, exit 0 |
| `./scripts/sanitize.sh` | 231 tests, ASan/UBSan clean, exit 0 |
| `python3 benchmarks/corpora/application-v5/verify.py` | 2,815 checks, all pass; 68 supported, 11 unsupported |
| same with `--group original` | Exactly 610 checks, all pass |
| NeetCode `verify.py --verified-only` natural and tuned separately | Each 29 programs, 1,070/1,070 checks |
| Study Python unit suite | 25 tests, including ten synthetic Rust tracker tests |
| `verify_copy_overlay.py` | 18 adversaries / 36 native O0/O2 runs |
| `verify_copy_stability.py` | Three programs x three identical golden classifications |

Final differential campaigns run full 673-case index coverage at seeds 22021,
22022 and 22023: 2,019 programs, 4,038 native O0/O2 builds, zero divergences.
The reported 491 named-family keys include mutation labels; not every base case
has a named tag. All 29 new ownership families execute once per seed. Per-family
and per-code counts are preserved in the JSON, including full existing families.
Effects compare stdout, written files and preserved input; diagnostics compare
codes **and spans**. Each final unbounded campaign has no E008; bounded census
and existing call/step-limit tests cover E008. Do not imply it was hit by these
campaigns. E013 is hit 38 times per seed.

| Seed | OK | E009 | E012 | E013 | E014 | E015 | E016 | E017 | E018 | E019 | E020 | E021 | E022 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 22021 | 500 | 8 | 27 | 38 | 10 | 8 | 14 | 10 | 11 | 3 | 6 | 35 | 3 |
| 22022 | 499 | 8 | 28 | 38 | 10 | 8 | 14 | 10 | 11 | 3 | 6 | 35 | 3 |
| 22023 | 500 | 8 | 27 | 38 | 10 | 8 | 14 | 10 | 11 | 3 | 6 | 35 | 3 |

The new matrix includes different indices, reordered operands, multiple reads,
bindings, reads before and after writes, readonly/conditional/recursive/mutual
callees, replay-budget exhaustion, nested lazy arms, selected and unselected
traps/effects, division/allocation/quota barriers, live/returned/record/map aliases,
loop state, empty bytes and zero-slot records. These 29 additions are primarily
fixed adversarial programs; only the different-index family varies by seed.
This is not broad randomized ownership-program synthesis. No sanitizer finding
or unexplained compiler divergence was observed. Instrumentation address reuse,
outdated IR assertions and a bad test callee label were found and corrected;
the instrumentation fix has its own synthetic regression and stability checks.

## Reproduce

Run timing alone. Build helpers through the existing corpus verification first.

```sh
./scripts/ci.sh
./scripts/ci.sh release
./scripts/sanitize.sh
./scripts/fuzz-v5.sh --seed 22021
./scripts/fuzz-v5.sh --seed 22022
./scripts/fuzz-v5.sh --seed 22023
python3 benchmarks/corpora/application-v5/verify.py --jobs 1 --output /tmp/r22-app.json
python3 benchmarks/corpora/application-v5/verify.py --group original --jobs 1 --output /tmp/r22-original.json
python3 benchmarks/corpora/neetcode150/verify.py --verified-only --jobs 1   --candidate-dir "$PWD/benchmarks/core-generalize-study/natural" --output /tmp/r22-natural.json
python3 benchmarks/corpora/neetcode150/verify.py --verified-only --jobs 1 --output /tmp/r22-tuned.json
python3 benchmarks/core-generalize-study/measure_cohort.py --repeats 15 --output /tmp/r22-cohort.json
python3 benchmarks/core-generalize-study/measure_controls.py --repeats 25   --baseline-compiler /path/to/compiler-built-from-92d62b3   --baseline-revision 92d62b3 --output /tmp/r22-controls.json
```

The repaired overlays and census commands are documented in
[core-generalize-study/README.md](../../core-generalize-study/README.md).
Use `--revision 92d62b3` for before and current compiler for after, and run each
of `application`, `neetcode-natural`, `neetcode-tuned`, `fuzz:22001`, `fuzz:22002`.
Raw outputs stay outside git under `~/.local/share/nil/round22-ownership/`;
aggregate JSON includes their SHA-256 receipts and the
[archive manifest](ROUND22_RAW_MANIFEST.json).

## Next ownership decision

General G1 and replay across multi-update quota barriers need parameter/returned/
child provenance plus an explicit logical charge/death model. A last payload read
alone is not enough. Consider a version/charge ledger in a separate decision;
do not erase semantic reservations or rewrite natural solutions to claim success.
Full keeping-read hints depend on that provenance. No new core capability, profile,
intrinsic or held-out algorithm was added in this round.
