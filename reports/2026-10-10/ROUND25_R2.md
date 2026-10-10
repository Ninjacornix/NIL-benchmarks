# Round 25 — R2 caller/callee root transfer (partial round)

**R3 child-edge transfer is not implemented, so course schedule is unchanged at
200.886× C++.** Natural heap (4.937×) and spiral (3.662×) still miss the 3×
bound and have no claimed R2 gain. Do not read this as the completed
three-class goal. No held-out problem or frozen source was edited, and nothing
was pushed.

**Natural qualification rises 20 → 21/150; tuned stays 23/150.** The unchanged
natural balanced-tree validator goes from 1,509.301 to 27.151 ms (2.020× C++).
Native O0 census removes a further 80,000,014,936 bytes and 100,061 copy events,
which is 20.00% of the Round 24 natural baseline and takes the cumulative R1+R2
reduction to 39.99%. Application and tuned censuses are byte-identical to R1, so
this is a gain at one witness, not a broad improvement.

## Proof and boundaries

ADR 049's R2 design addendum was committed as `66bd66c` before any R2 compiler
code, as `git log --reverse --name-only fc6c279..HEAD` shows. R2 is not a new
transfer mechanism: the emitter already retired an argument root immediately
before a call when semantic liveness made the call that argument's last use.
R2 extends *which* calls qualify, and adds the summary that makes surrender safe.

Two per-function facts are inferred from validated HIR after ADR 040 expansion
(`crates/nil-hir/src/parameters.rs`):

- `owns[f][k]`: parameter `k` is semantically live in `f` and `f` is not an
  allocation-free borrow function. These are exactly the conditions under which
  lowering already roots a parameter at entry, so the summary describes lowering
  rather than predicting it.
- `origins[f]`: the parameters whose storage `f`'s result may alias, or
  `Unknown`. Solved as a least fixed point over finite parameter-index sets,
  iterating the whole call graph until stable; direct and mutual recursion
  converge with no acyclic shortcut. Unknown absorbs in the join and blocks
  transfer; it is never relaxed into "no origin".

A caller surrenders its root for a Buffer/Bytes argument only when the argument
occupies exactly one slot by SSA identity, `owns` holds for that parameter,
`origins` is known, every later use of the argument is a proved scalar snapshot,
the caller actually holds a root slot, and the build is unbounded with wrapping
arithmetic. At most one argument per call is transferred, so two snapshot sets
can never contend for one replayed read, and a call whose snapshot set overlaps
an admitted R1 interval is dropped rather than merged.

ADR 049 was explicit that the witness needs more than last-use handoff: the
caller reads `b[c-1]` in sibling state expressions *after* `g(a,b,c,b[c-1])`.
R2 therefore composes transfer with R1's scalar continuations. Probes run after
the final argument and before the call, so they observe the pre-call contents
the caller's later reads are entitled to see; the root is surrendered only on the
path where every snapshot is valid. An invalid snapshot keeps the root and runs
the original reads at their original spans. Probes never trap and never
diagnose: `replay_instruction` falls back to an invalid probe for any operation
it does not model, so an unsupported later read can only fail the guard, never
forge a snapshot.

The gap between surrender and the callee's parameter root contains no allocation
and no collection, because parameter roots are installed at callee entry ahead of
the body; this discharges obligation 7. Surrender is an ordinary
`nil_root_store` of null, discharging obligation 8. Returning an alias is not a
transfer condition: it hands a live obligation back, which the caller discharges
by rooting the result in the ordinary way.

**Uniqueness remains a runtime decision at the mutation.** Transfer removes one
caller root; a record child edge, a second loop-state slot, an independently
retained returned alias or a callee-side store still raise the observed count and
still force a copy. Every negative case below was confirmed by runtime copy
hints, not inferred from the IR.

### Stated conservative gaps

Refused with the missing fact named: record, record-map and record-buffer
arguments (container edge tables are deferred R3 and map/row work); plugin and
unresolved callees; bounded builds; checked arithmetic; any caller use of the
argument that is not a proved scalar snapshot. Two precision gaps inside the
summary are also conservative by construction — every intrinsic is `Unknown`,
because none has a published result-provenance proof and `!slice` may reuse an
argument's storage; and a region result naming an enclosing local rather than a
parameter is `Unknown`, because the walk covers one SSA scope at a time. A
callback cannot receive a sequence in this profile, so the sequence-taking std
higher-order intrinsics are never transfer anchors.

## Five natural cliffs

Milliseconds: min / median / max, 15 rotating repetitions, `--jobs 1`, byte-exact
oracles. Balanced tree and the BST control were re-measured alone in the
mandated three-witness run; that run gives balanced 26.485/27.151/30.635 against
C++ 12.971/13.438/14.880 (2.020×) and BST 24.118/24.935/27.356 against
12.665/13.125/14.520 (1.900×).

| Program | R1 natural median | R2 natural | C++ | Ratio | Qualifies |
|---|---:|---|---|---:|---|
| balanced-binary-tree | 1509.301 | 26.509 / 26.865 / 27.377 | 12.903 / 13.131 / 13.796 | 2.046× | yes |
| course-schedule | 4283.140 | 4269.596 / 4520.276 / 5898.282 | 21.874 / 22.502 / 24.389 | 200.886× | no |
| last-stone-weight | 54.498 | 52.286 / 52.875 / 54.224 | 10.548 / 10.711 / 10.917 | 4.937× | no |
| spiral-matrix | 27.700 | 27.102 / 27.832 / 33.357 | 7.286 / 7.600 / 13.260 | 3.662× | no |
| validate-binary-search-tree | 23.841 | 23.633 / 24.119 / 24.418 | 12.183 / 12.347 / 12.567 | 1.953× | yes |

The BST control is the one that matters for regression: it stays at ~1.9×, so
R2 did not disturb R1's result. Course schedule, heap and spiral move only
within session variance and have no claimed R2 mechanism.

### Forecast outcomes

| ADR 049 R2 forecast | Outcome |
|---|---|
| Balanced tree 20–50 ms, 1.5–3.8× | **met**: 27.151 ms, 2.020× |
| Copy reduction at witness 90–100% of 80.000 GB / 100,068 events | **met**: 80,000,014,936 bytes (≈100%) and 100,061 events (99.99%) |
| Cumulative natural qualification R2 20–21 | **met at the top**: 21/150 |
| Tuned stays 23–25 | **met**: 23/150 |
| Natural census cumulative R1+R2 36–40% | **met at the top**: 39.99% |
| Application 0–15% payload reduction | measured **zero** |
| Controls within ±10% | **met**: no regression |

## Copy census

Native O0 mechanism trace joined to reference logical versions, decimal bytes,
all admitted fixtures. Overlay rebuilt from the committed HEAD so the reference
side matches this compiler.

| Scope | Events | Bytes | REQUIRED bytes | AVOIDABLE bytes |
|---|---:|---:|---:|---:|
| application | 8,034 | 157,626 | 26,078 | 131,548 |
| neetcode-natural | 3,720,173 | 240,057,008,452 | 160,000,660,795 | 80,056,347,657 |
| neetcode-tuned | 3,420,177 | 60,208,452 | 3,060,795 | 57,147,657 |

Natural before R2 (the R1 receipt): 3,820,234 events / 320,057,023,388 bytes,
REQUIRED 240,000,675,731 and AVOIDABLE 80,056,347,657. R2 removes 100,061 events
and 80,000,014,936 bytes, **all of it out of REQUIRED**; AVOIDABLE is unchanged
to the byte. Against the Round 24 natural baseline of 3,920,307 events /
400,057,040,260 bytes, R1+R2 together remove 200,134 events and 160,000,031,808
bytes (39.99%). Balanced tree now retains 7 bytes, the output append that ADR
049's table already classified as AVOIDABLE; course schedule still retains
239,996,800,007 bytes pending R3. Application (8,034 / 157,626) and tuned
(3,420,177 / 60,208,452) are byte-identical to R1, so R2 produced no application
or tuned gain.

## Timing controls

25 repetitions, measured alone. No matched-session regression; transform and
scan are slightly faster, append slightly slower, all inside ±10%.

| Control | R1 | R2 | C++ |
|---|---|---|---|
| append | 4.503 | 4.546 | 3.383 |
| scan | 7.718 | 7.317 | 9.561 |
| transform | 36.609 | 35.385 | 12.705 |

## Negative-case matrix

Every row was run at O0 and O2, compared against the reference evaluator, and
its copy behaviour read from runtime hints. "Transfers" is whether the caller
surrendered its root; "copies" is whether a payload copy still happened.

| Case | Transfers | Copies | Why |
|---|---|---|---|
| baseline single owner | yes | no | the only owner is surrendered |
| `f(a,a)` repeated argument | no | yes | two parameter slots by SSA identity |
| caller observes the original as a sequence | no | yes | not a scalar snapshot; statically refused |
| live record parent | no | yes | the projection is not the last use and the child edge stays counted |
| independently retained returned alias | yes | **yes** | transfer is admitted for the argument, and the other owner still forces the copy |
| two loop-state slots | no | yes | two independent roots on one allocation |
| callee stores the parameter in a record | yes | **yes** | the callee's own liveness forbids reuse |
| read-only borrow callee | no | no | no parameter root to receive ownership, and nothing to copy |
| unknown return provenance (`!concat`, `!slice`) | no | no | `origins` is Unknown |
| std sequence-taking HOF | no | no | an intrinsic is never a transfer anchor |

Three rows deserve naming because they are not simple refusals. A *dead* record
parent does transfer and does not copy: the parent's last use is the projection,
so its edge is legitimately released, and the live-parent row above is the
genuine negative. A recursive ancestor that re-reads its own buffer after the
recursive call mutated that storage is *admitted*, and is correct because the
snapshot is taken pre-call; this is the case ADR 049 obligation 4 warns about,
and the snapshot rather than a refusal is what discharges it. A specialized
static callback leaves an ordinary resolved call and is treated as one.

Positive variant coverage: argument order, extra parameters, bindings versus
inline, computed and literal indices, two sequence parameters, Bytes as well as
Buffer, unrelated reads of a different sequence, a loop whose sibling state
expression reads the original, mutual recursion, a recursive ancestor re-read,
and a specialized callback. Trap, effect, laziness and layout coverage: an
effect after the call, an out-of-bounds future probe, an out-of-bounds update,
a 4 KiB allocation after an accepted handoff, an empty buffer, a byte-range
failure, an unselected arm whose effect must not run, and a zero-slot record.

## Gates

```text
./scripts/ci.sh                           596 tests; zero warnings; passed
./scripts/ci.sh release                   596 tests; zero warnings; passed
./scripts/sanitize.sh                     274 tests; no findings; passed
./scripts/fuzz-v5.sh --seed 61001         821 programs; 1754 native builds;
                                          divergences 0; non_resource 0; rule_3 0
./scripts/fuzz-v5.sh --seed 83003         821 programs; 1754 native builds;
                                          divergences 0; non_resource 0; rule_3 0
application-v5/verify.py                  2815 checks; 0 inconclusive; passed
application-v5/verify.py --group original  610 checks; 0 inconclusive; passed
neetcode150/verify.py tuned                1070 checks; 0 inconclusive; passed
neetcode150/verify.py natural              1070 checks; 0 inconclusive; passed
core-memory-study/audit_depth.py           36/36 nondivergent; 0 failed
```

Both seeds: 112 escalated comparisons, 76 resolved exactly, 36 inconclusive, all
of them the pre-existing `unbounded_stack_*` E008 depth families; zero E013 and
zero native-only persistent resource outcomes. Each of the 29 new
`g1_transfer_*` families executed once per seed, so the differential campaign
covers R2's positive and negative shapes under unbounded instrumentation.
`FAMILY_COUNT` rises 59 → 88. 35 intrinsics; no syntax, type, default-profile or
earlier-profile change; no runtime C change.

## R3: measured, refused, handed off

R3 was investigated at its witness and **deliberately not shipped**. The
measurement is recorded in ADR 049's dated R3 section and summarised here.

`course-schedule` copies 800,000 bytes twice per relaxation, at spans 710..727
(`counts`) and 750..760 (`queue`), so repairing one field caps the gain near 50%
against an 85–100% forecast. Reading the emitted callee rather than inferring it:
both child updates already emit `nil_set_unique`, and each child carries exactly
two roots at its update — the parent field edge plus the projection — because
redundant re-projections are already rooted and retired after their scalar reads.
The only missing fact is the parent field-edge surrender, and
`loop_storage::field_transfer` already implements that primitive for a
Concat/`UpdateField` builder chain.

The fields are not symmetric. `queue` is never re-projected after its update, so
an edge surrender alone would be sound, but its update sits inside a selected
lazy region where ADR 038/039 reconciliation applies. `counts` is scalar-read
twice *after* its update through different `Field` values of the same parent
field, so it needs field-path aliasing of re-projections plus snapshots across a
parent → field → index path — new analysis, not a predicate relaxation.

R3's preregistered precondition, "a record whose last logical use is
reconstruction", does not hold here for either field: the parent stays live to
instruction 15 through sibling `tail` and `counts` reads while the updates are at
5 and 10 and the reconstruction is at 16. That is the same composition gap this
ADR recorded for R2. Shipping only the `queue` half would modify record root
groups inside a lazy region while leaving the program a performance miss, so it
was refused rather than part-proved.

## Remaining work

Course schedule stays at 200.886× and the natural AVOIDABLE total is unchanged.
Map-value and record-buffer-row extraction remain deferred. Heap and spiral have
no R2 mechanism and keep their published limits. The cheapest places to widen R2
are the two named summary precision gaps: intrinsic result provenance and
region results naming an enclosing local.
