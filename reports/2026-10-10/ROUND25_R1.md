# Round 25 — R1 selected-region ownership (partial round)

**R2 caller/callee and R3 child-edge transfers are not implemented.** Balanced tree
still costs 107.91× C++; course schedule 188.80×. Natural heap and spiral remain
above the 3× qualification bound. Do not read this R1 checkpoint as the completed
three-class goal. No held-out problem or frozen source was edited.

**Natural qualification increased 19 → 20/150; tuned stays 23/150.** The unchanged
natural BST validator goes from 1,411.189 to 23.841 ms (1.90× C++).
Native O0 census removes 80,000,016,872 bytes and 100,073 copy events (20.00% of
natural bytes). This is a compiler gain on the frozen natural source.

## Proof and boundaries

ADR 049 was committed as `d0a197a` before compiler changes. R1 uses semantic
def-use/liveness and backward scalar slices across selected sequence-valued lazy
regions. It does not match the BST source or index spelling. Valid guarded scalar
snapshots retire only the proved outer owner slot, before the leaf update; the
ordinary runtime root count still decides reuse. Other owners retain their slots.
Invalid probes retain the original and fall back to copying. Traps/effects remain
at their original sites; unselected arms execute nothing. Leaf ownership covers
the GC handoff; no runtime C changes or forced-unique assertion were introduced.

This discharges aliases, returned aliases, laziness, recursion, child roots,
trap/effect order, resource/GC safety and deferred-root obligations for R1.
The observed-frame fast path rejects lazy regions, so replay updates reconcile
roots normally. Independent caller, parent, map and record-buffer roots remain.
Flat Buffer/Bytes, unbounded wrapping execution only; bounded builds keep their
original budgets. Scalar continuations are limited to 128 instructions, probe
budget 512/depth 8. Unsupported computations retain conservative roots.

Variant tests cover grouping, computed indices, bindings, nested conditionals,
extra parameters, reordered loop state, scalar helpers and mutual recursion.
Negative cases cover old aliases, returned aliases, record parents, future bounds
and update bounds, byte range and effects. A 500-iteration allocation-after-handoff
case exercises collection. Actual copying is asserted with runtime copy hints for
caller and record-parent aliases, not inferred solely from the IR call name.

No non-resource divergence or sanitizer finding was found. During pre-test review
the new join loads initially preceded the phi; they were moved after it before
running the compiler. Native region tests validate the corrected IR.

## Five natural cliffs

Milliseconds: min / median / max, 15 rotating repetitions; byte-exact oracles.

| Program | Round 24 natural median | R1 natural | C++ | Ratio | R1 tuned |
|---|---:|---|---|---:|---|
| balanced-binary-tree | 1481.530 | 1498.061 / 1509.301 / 1612.940 | 13.481 / 13.987 / 15.275 | 107.91× | 27.039 / 27.888 / 28.340 |
| course-schedule | 4315.198 | 4219.753 / 4283.140 / 4618.291 | 21.998 / 22.686 / 24.632 | 188.80× | 41.163 / 41.990 / 47.219 |
| last-stone-weight | 53.104 | 52.115 / 54.498 / 71.672 | 10.542 / 11.215 / 14.780 | 4.86× | 24.791 / 25.905 / 30.437 |
| spiral-matrix | 27.424 | 26.871 / 27.700 / 28.763 | 7.262 / 7.374 / 7.564 | 3.76× | 24.751 / 24.945 / 26.271 |
| validate-binary-search-tree | 1411.189 | 23.673 / 23.841 / 27.189 | 12.171 / 12.534 / 15.013 | 1.90× | 22.705 / 22.978 / 26.228 |

R1 forecast BST 20–45 ms, 90–100% copies removed: met (23.841 ms, all 100,073
set copies removed; seven output append bytes remain). Natural 19–20: met.
Application forecast 0–15%: measured zero. Bounded fuzz census cannot measure
this unbounded-only optimization; it is not evidence of a fuzz copy reduction.
R2/R3 forecasts are untested. Heap/spiral have no claimed R1 ownership gain.

## Copy census

Native O0 mechanism trace joined to reference logical versions; strict REQUIRED
includes retention for quota/GC, not only payload reads. Decimal bytes, all admitted
fixtures, not a claim about copies surviving O2. Full source hashes and exclusions
are in the JSON/raw archive. Application/tuned counts are unchanged.

| Scope | Events after | Bytes after | REQUIRED bytes | AVOIDABLE bytes |
|---|---:|---:|---:|---:|
| application | 8,034 | 157,626 | 26,078 | 131,548 |
| neetcode-natural | 3,820,234 | 320,057,023,388 | 240,000,675,731 | 80,056,347,657 |
| neetcode-tuned | 3,420,177 | 60,208,452 | 3,060,795 | 57,147,657 |
| fuzz-25101 | 5,294 | 58,764,547 | 58,731,976 | 32,571 |
| fuzz-25102 | 5,290 | 58,757,702 | 58,731,976 | 25,726 |

Natural before: 3,920,307 events / 400,057,040,260 bytes; REQUIRED
240,000,675,731 and AVOIDABLE 160,056,364,529 bytes. After REQUIRED unchanged,
AVOIDABLE reduced by 80,000,016,872. Balanced retains 80,000,014,943 bytes;
course retains 239,996,800,007; heap 801,072; spiral 1,076,740. Application
8,034 / 157,626 and tuned 3,420,177 / 60,208,452 are unchanged.
Fuzz adds nineteen R1 families; its census is bounded and is not an apples-to-apples
aggregate comparison with the 773-family baseline. Native trace cap and resource
exclusions remain named in the JSON; no missing trace is counted as zero.

## Timing controls and RSS

25 rotating repetitions, timing/RSS alone; baseline binary preserved from 929527d.
Historical scan is **17 MiB**, separately measured true 16 MiB. Transform output
is byte-exact and double transform round-trips. No matched-session regression.

| Control | Before | After | C++ |
|---|---|---|---|
| append | 4.340 / 4.596 / 5.526 | 4.322 / 4.503 / 5.024 | 3.214 / 3.451 / 4.118 |
| scan | 7.574 / 7.865 / 8.152 | 7.415 / 7.718 / 7.908 | 9.894 / 10.196 / 10.516 |
| transform | 35.665 / 36.547 / 43.522 | 35.414 / 36.609 / 42.942 | 12.245 / 13.893 / 25.547 |
| scan 16 MiB | 7.073 / 7.445 / 7.777 | 6.983 / 7.255 / 7.569 | 9.276 / 9.602 / 10.057 |

Historical Round 24 medians: append 4.449, 17 MiB scan 7.489, transform
39.003 ms. Matched-session transform before/after 36.547/36.609 ms exposes
the historical elevation as session variance, not a measured R1 regression.

| Natural cliff | Peak RSS median bytes | NIL/C++ |
|---|---:|---:|
| balanced-binary-tree | 7,405,568 | 0.630× |
| course-schedule | 18,595,840 | 1.332× |
| last-stone-weight | 3,948,544 | 0.834× |
| spiral-matrix | 4,849,664 | 0.759× |
| validate-binary-search-tree | 5,652,480 | 0.623× |

All cohort/control RSS min/median/max (three isolated samples) are in JSON.
Control before/after RSS is unchanged. Whole-process frontend+IR (25 alternating
runs, no Clang): 3.707 / 3.903 / 4.170 → 3.673 / 3.801 / 3.897 ms.
No R2 fixed point exists yet, so no fixed-point overhead claim.
Reference evaluator, largest unchanged heap fixture: verified VALUE 2 in 70.261 s,
alone with a 300 s timeout. This is still slow, not a reference performance fix.

## Gates and fuzz outcomes

Command outputs are archived with SHA-256 hashes in `ROUND25_R1.json`.

```text
./scripts/ci.sh                         582 tests; zero warnings; passed
./scripts/ci.sh release                 582 tests; zero warnings; passed
./scripts/sanitize.sh                  270 tests; no findings; passed
./scripts/fuzz-v5.sh --seed 25101        792 families; 1696 native builds; 0 divergences
./scripts/fuzz-v5.sh --seed 25102        792 families; 1696 native builds; 0 divergences
application-v5/verify.py                2815 checks; no inconclusives; passed
application-v5/verify.py --group original 610 checks; no inconclusives; passed
neetcode150/verify.py natural / tuned   1070 each; no inconclusives; passed
core-memory-study/audit_depth.py         36/36; no signals; passed
```

Every indexed family executes once per seed; each of the nineteen new
`g1_selected_*` families executes once. Effects and input preservation compare
on every outcome. Each seed: 112 escalations, 76 resolved exactly, 36 persistent
E008 (large-record both 12, mutual both 10, mutual reference-only 2, sequence
both 12); native-only persistent resource outcomes zero, E013 zero, rule-3 zero.
Joint 4× escalation remains unchanged. Reference code counts per seed:

```text
OK 568; E008 18; E009 14; E012 42; E013 38; E014 17; E015 12;
E016 15; E017 10; E018 11; E019 3; E020 6; E021 35; E022 3.
Native initial O0/O2: same, except E013 36 and OK 570; reruns match.
```

Per-family and escalation-direction counts are included for both seeds in JSON.
35 intrinsics; no syntax/type/default/earlier-profile change. Frozen source hashes
are retained in verification and timing receipts. No push was performed.

## Remaining work

R2 requires per-parameter ownership/returned-alias summaries and an SCC fixed
point; R3 requires last-use parent child-edge transfer. Neither is proved/shipped.
Balanced caller reads the old sequence in sibling state expressions **after**
the call: caller last-use alone cannot fix it; selected snapshots must compose
with transfer. Map-value and record-buffer-row extraction remain deferred.
Reference heap runtime, other aliases/escaping scalar continuations and bounded
builds stay conservative. This checkpoint completes R1 only.
