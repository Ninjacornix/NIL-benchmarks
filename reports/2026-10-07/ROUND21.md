# Round 21 — copy census, preregistration, and no compiler change

Main `ab6c1c5` → this round; benchmarks `a3c466b` → this round. Branches
`feat/core-generalize` and `exp/core-generalize`, no upstream, nothing pushed.

**Qualification is unchanged: NATURAL 19/150, TUNED 22/150.** Both cohorts pass
all 1,070 correctness checks. The 114 unattempted NeetCode problems remain held
out (rule R3).

## Unfavourable results first

**1. No compiler change shipped. Steps 4, 5 and 6 of the round are not
implemented.** `git diff 2e6614e..HEAD -- crates cli tools scripts examples
plugins` is empty. Configurable limits, native stack safety and the copy-hint
diagnostic are preregistered in ADR 043 but not built; general ownership is
explicitly declined. The round delivers measurement and preregistration only.

**2. ADR 043's primary stated reason for declining general ownership was
falsified by this round's own census.** The ADR was written before the census
finished and claimed "the census does not yet show native payload-copy volume
proportional to the cliff magnitudes, so the premise is unproven." That is wrong:
the census shows the opposite, decisively. A dated addendum corrects it rather
than editing the original text. The decision not to ship stands on the remaining
reasons (interacting soundness obligations, rule R2's ban on shape recognizers,
and budget), not on that one.

**3. The fuzz scope of Part A1 is NOT achieved.** Both seeds report zero copy
events across all 644 generated families. The cause is a harness gap, not a
finding: the generated families declare a four-argument `(v,s,s,s)` entry and the
census harness supplies two byte arguments, so every family stops at
`E006 entry arity mismatch expected:4 got:2` before executing. Instrumented and
ordinary runs still agreed, so parity held — on nothing. Part A1 is therefore
complete for the application corpus and both NeetCode cohorts and **incomplete
for the fuzz scope**. The fix is a dedicated helper that supplies a Buffer and
three Bytes arguments.

**4. One fixture is excluded from the native census.** 3sum's largest fixture is
dropped in both NeetCode cohorts because its native trace of 6,745,501 events
exceeds the 5,000,000 cap. All other 28 programs and every one of their fixtures
are joined in both cohorts; the application scope has no exclusions.

**5. The transform control is slower than Round 20 and that is retained, not
dismissed.** 41.19 ms median against Round 20's 36.04 ms, **+14.3%**. The
Round 21 before-measurement already recorded 39.50 ms (+9.6%) and kept it. No
compiler file changed between those two measurements, so this is machine drift,
but it is drift in the unfavourable direction and is not declared noise.

**6. The reference evaluator copies far more than the native runtime, and most of
it is avoidable.** On the natural cohort the reference evaluator performs
13,269,808 payload copies to the native runtime's 6,423,242, and it emits
7,307,101 *certain* reallocations: `Sequence::append` reallocates on nearly every
call for builder-shaped programs. The reference evaluator is an oracle, not a
performance target, so this is not a qualification problem — but it is the reason
reference runs dominate census wall time, and it is recorded rather than hidden.

## Part A1 — the copy census

Protocol: `COPY_CENSUS_PROTOCOL.md`. Ledger: `copy_ledger.py`. Runner:
`copy_census.py`. Summary: `ROUND21_COPY_CENSUS.json`, which carries raw-run
hashes, the overlay manifest hash and the full ledger receipt.

Classification is against later **reference-semantic** observations, by
monotonically assigned version IDs, never addresses or root counts. Addresses are
private lookup keys and are never serialized, so a late read of an old snapshot
cannot be attributed to a newer version that reused its address. An event kind
missing from the ledger raises and aborts the census; `UNCLASSIFIED` is a failed
census, never silently AVOIDABLE. A program's events are accepted only after the
instrumented and ordinary runs agree on exit code, stdout, output bytes and
preserved input.

**AVOIDABLE means "no later observation of the source version under this
metric". It is not a proof that the copy can be removed, and scheduling can
remove copies inside the REQUIRED set too.** That distinction turns out to carry
the round's main finding.

Groups partition owning storage: `PAYLOAD_COPY` (the only group in the headline,
because it is the only one a generalized ownership analysis could remove),
`CONSTRUCTION`, `INPUT_DECODE`, `OUTPUT_MATERIALIZE`, `GROWTH_RELOCATION`.
Relabelling a site between groups changes the published per-group totals, so a
payload copy cannot be hidden as construction.

### Reference evaluator, per scope

| Scope | Programs | Payload events | Payload bytes | strict REQUIRED | strict AVOIDABLE | payload-only REQUIRED |
|---|---:|---:|---:|---:|---:|---:|
| NeetCode natural | 29 | 13,269,808 | 2,166.7 GB | 2,627,053 | 10,642,755 | 2,526,934 |
| NeetCode tuned | 29 | 12,469,338 | 1,526.9 GB | 2,026,735 | 10,442,603 | 1,926,616 |
| Application corpus | 68 | 7,595 | 165,218 B | 1,469 | 6,126 | 1,437 |
| Fuzz seed 5130572 | 644 | — | — | — | — | — |
| Fuzz seed 777001 | 644 | — | — | — | — | — |

Other groups, both NeetCode cohorts: `CONSTRUCTION` 1,940, `GROWTH_RELOCATION`
7,307,101, `INPUT_DECODE` 0, `OUTPUT_MATERIALIZE` 0 — the latter two because the
reference host paths and formatting are enumerated in the ledger's `EXCLUDED`
list with reasons rather than hooked. Application corpus: `CONSTRUCTION` 183,
`GROWTH_RELOCATION` 3,792.

### Native O0 mechanism census — the actionable number

The native census is joined to reference versions by site and occurrence,
fail-closed: an unknown site, operand role or source version aborts that fixture
and is recorded. O0 preserves the emitter's copy decisions, which is the decision
being measured; it makes **no** claim about which copies survive the O2 pipeline.

| Cohort | events | copied bytes | strict REQUIRED | strict AVOIDABLE |
|---|---:|---:|---:|---:|
| natural | 6,423,242 | 2,086.6 GB | 2,526,935 (1,926.6 GB) | 3,896,307 (160.1 GB) |
| tuned | 3,945,509 | 105.6 GB | 249,354 (105.5 GB) | 3,696,155 (57.4 MB) |
| application | 8,147 | 162,517 B | 2,130 (31,214 B) | 6,017 (131,303 B) |

**Round 20's tuning removed 94.9% of native copied bytes.**

### The decisive result: natural versus tuned, per program

The **only** five programs whose native payload-copy count differs between the
natural and tuned cohorts are **exactly the five cliff programs**. The other 24
programs are identical in copy behaviour across the two cohorts.

| Program | natural events | natural MB | tuned events | tuned MB | natural REQUIRED | natural AVOIDABLE | natural/C++ | tuned/C++ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| last-stone-weight | 1,809,154 | 1,446,604 | 131,891 | 105,306 | 1,809,138 | 16 | 2155.55× | 157.85× |
| course-schedule | 500,234 | 399,995 | 7 | 0.0 | 400,228 | 100,006 | 327.59× | 1.86× |
| spiral-matrix | 299,957 | 79,771 | 199,974 | 1.1 | 99,965 | 199,992 | 158.81× | 3.04× |
| balanced-binary-tree | 100,194 | 80,002 | 7 | 0.0 | 100,125 | 69 | 107.64× | 1.94× |
| validate-binary-search-tree | 100,080 | 80,000 | 7 | 0.0 | 0 | 100,080 | 103.48× | 1.78× |

Two conclusions follow, and the second is the one that matters for the next round.

**The cliffs are copy traffic.** Three programs went from 10^5–10^6 copies to
**seven** when Round 20 rewrote them with bindings, and the same three moved from
performance-miss to pass. This is direct evidence for rule R1: the natural source
is the honest measurement, and what the rewrite bought was copy elimination the
compiler should have found.

**Liveness alone cannot fix the biggest cliff.** The REQUIRED/AVOIDABLE split
decides which analysis is needed, and it differs per program:

- `validate-binary-search-tree` is **100% AVOIDABLE** — 0 of 100,080 copies have
  a later observation. A general interprocedural last-use analysis (G1) removes
  these.
- `last-stone-weight` is **99.999% REQUIRED** — 16 of 1,809,154 are avoidable —
  and `balanced-binary-tree` is 99.93% REQUIRED. The original *is* observed after
  the update, so no liveness analysis may reuse its storage. Only read-before-write
  scheduling (G2) can help, which is exactly what the Round 20 binding did by hand.
- `course-schedule` is 80% REQUIRED and `spiral-matrix` 67% AVOIDABLE; both need
  G1 and G2.

So **G2 is the primary target for the next round, not G1.** Had this round shipped
a liveness-only ownership analysis, it would have left the two largest cliffs
untouched while appearing to address the problem.

### Census validation

`verify_copy_overlay.py`: **18 adversaries, 36 native executions, all pass** —
live, dead and metadata-only old values; slices; selected and unselected lazy
arms; returned aliases; fixed arrays; map key and byte-value arguments; the map's
own index and entry key copies; and map value materialization. Each is checked
against the ordinary evaluator and native O0/O2.

`copy_trace.rs`: 9 tracker unit tests, including address reuse, in-place version
change, snapshot retention, and that same-instruction copy reads are not later
observations.

Study Python suite: **21 tests pass**, including `test_copy_ledger.py`, which
scrapes both overlay sources and fails if the ledger and the hooks drift apart in
either direction — an unledgered hook *or* a ledger entry with no hook.

## Parts A4 and ADR 043 — preregistration

`FORECASTS.md` (benchmarks `0337c54`) commits numeric forecasts for steps 4–6
before ADR 043 and before any code: defaults of 256 MiB and 1024 frames, chosen
as 4.92× the worst observed admitted reservation (3sum at 81.29% of 64 MiB) and
4× the current depth; all 1,070 NeetCode and 2,815 application checks unchanged;
every current E013 reproduced at the same instruction, code and span under a
64 MiB configuration; qualification unchanged by limits alone; and general
ownership forecast **not** to ship.

ADR 043 (main `40497f2`) decides:

- **(a)** Memory limit and call depth become declared execution parameters with a
  Rust API field and CLI flags, deterministic for a given limit on every path.
  **The reserve-as-if-copying rule is explicitly retained**, because removing it
  would make a program's E013 boundary depend on whether an ownership proof fired
  — a sound optimization could then admit a program that previously failed. The
  limit is raised instead. Stated consequence: peak quota stays near twice live
  payload, so 256 MiB of quota is not 256 MiB of usable payload.
- **(b)** The reference evaluator must reach the configured depth and raise E010
  rather than fault; native stack exhaustion must become a clean E008, which
  requires a stack-headroom guard in unbounded builds. If that guard cannot stay
  within 2% on the historical controls, the unbounded default depth stays at 256
  and the limitation is published rather than shipping a crash.
- **(c)** `--explain-copies` emits machine-readable records naming each copying
  update and the later read that kept the original live; opt-in, deterministic,
  no effect on semantics, exit codes or output.
- **(d)** General ownership is **not** implemented. The eight soundness
  obligations are recorded verbatim so a later round cannot weaken them: live
  aliases expressed over ADR 038 observation points, returned aliases, lazy-arm
  union, a recursion fixed point, record children reachable through a live
  parent, trap order, quota observation under the retained reserve rule, and the
  ADR 038/039 deferred-root slot and committed-mirror pair.

## Gates

| Gate | Command | Result |
|---|---|---|
| Debug CI | `./scripts/ci.sh` | exit 0, **511 tests**, 0 failed, **0 Clippy warnings** |
| Release CI | `./scripts/ci.sh release` | exit 0, **511 tests**, 0 failed, **0 Clippy warnings** |
| Sanitizers | `./scripts/sanitize.sh` | exit 0, **223 tests**, 0 failed, no ASan/UBSan finding |
| Fuzz seed 21001 | `./scripts/fuzz-v5.sh --seed 21001 --out <tmp>` | 644 programs, 1,288 native builds, **0 divergences** |
| Fuzz seed 918273645 | same | 644 programs, 1,288 native builds, **0 divergences** |
| Fuzz seed 424242 | same | 644 programs, 1,288 native builds, **0 divergences** |
| Application corpus | `application-v5/verify.py` | **2,815 checks** (563 + 1,126 + 563 + 563) |
| Original group | same, `--group original` | **610 exactly** (120 + 240 + 125 + 125) |
| NeetCode tuned | `neetcode150/verify.py --verified-only` | 29 tasks, **1,070 / 1,070** |
| NeetCode natural | same, `--candidate-dir .../natural` | 29 tasks, **1,070 / 1,070** |
| Study tests | `unittest discover -s core-generalize-study` | **21 tests**, OK |
| Census adversaries | `verify_copy_overlay.py` | **18 cases, 36 native executions**, all pass |

All three fuzz seeds produced **identical** observed and static code counts —
E009 7, E012 24, E013 35, E014 9, E015 8, E016 14, E017 10, E018 11, E019 3,
E020 6, E021 35, E022 3, OK 479; static E001 507, E002 252, E004 252, E005 421,
E007 1,180 — matching Round 20 exactly. No E013 or E008 expectation moved,
because no limit changed. No gate was weakened and no check was skipped.

### Historical controls

Run alone, 25 rotating repetitions, three separate RSS runs. Because no compiler,
runtime, CLI or program file changed this round, these confirm machine drift
rather than a code effect; the ratio is the comparable quantity.

| Control | Before NIL / C++ ms | After NIL / C++ ms | Before ratio | After ratio |
|---|---:|---:|---:|---:|
| append (1 MiB) | 5.589 / 4.472 | 4.660 / 3.511 | 1.25 | 1.33 |
| scan (17 MiB) | 8.792 / 11.526 | 7.390 / 10.004 | 0.76 | 0.74 |
| transform (16 MiB) | 39.495 / 18.527 | 41.191 / 19.390 | 2.13 | 2.12 |

NIL and C++ moved in the same direction and by similar magnitudes on every
control, so the ratios are stable to within 6%. The transform absolute figure
remains above Round 20's 36.04 ms and is retained as item 5 above.

## What this round does not establish

- No limits change, stack guard, copy hint or ownership analysis was implemented,
  so none of their forecasts is yet tested. Every F4, F5 and F6 entry in
  `FORECASTS.md` remains open except **F6.1**, which forecast that general
  ownership would not ship: that one **held**.
- The census measures the native **O0** mechanism. It does not establish which
  copies survive O2, and the cliff timings in the table are O2 whole-process
  medians. The correlation between the two is strong across the five programs but
  is not a per-copy attribution.
- Copied-byte totals are cumulative traffic summed over every fixture, not peak
  memory. Peak RSS and quota reservation are separate measurements in
  `ROUND21_BEFORE.md`.
- The fuzz scope is unmeasured, so no claim is made about copies in generated
  programs.
- One machine, macOS arm64, Apple clang 21.0.0. Compare ratios, not milliseconds.
