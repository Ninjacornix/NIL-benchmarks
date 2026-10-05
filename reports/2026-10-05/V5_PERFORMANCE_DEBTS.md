# Expr-v5 performance debts: proved bulk lowering and builder reuse

The equality regression is repaired through **provider-body recognition, not a
provider-name/ID exception**. Direct dead-field append and single-use fresh/shared
record-buffer construction become approximately linear in the measured range.
Nested field updates through a still-live record buffer, genuine alias copies and
keyed payload repacking remain conservative and superlinear; their curves are below.

No language surface, types, intrinsics, dependencies, tasks, oracles, goldens or
baseline sources changed. Intrinsic variants stay 32. Earlier/default profiles and
64 MiB accounting are unchanged. No density measurement or model inference ran.
All main/submodule commits are local; nothing was pushed.

[Receipts](V5_DEBTS_RECEIPTS.txt), [fuzz codes/families](V5_DEBTS_FUZZ.json),
[corpus checks](V5_DEBTS_VERIFICATION.json), [original cohort](V5_DEBTS_ORIGINAL_VERIFICATION.json),
[ADR 031](../../../docs/adr/031.md) and [proof/diagnosis notes](../../../docs/validation/V5_PERFORMANCE_DEBTS.md).

## Methodology and provenance

Apple M2/arm64, macOS 27, Apple Clang 21. O2/LTO unless labelled O0; strict
existing FP flags remain. Whole-process warm wall time includes startup, allocation,
I/O and checked operations; compile time excluded. One warmup, 25 samples; paired
old/new and root-context comparisons alternate order. Existing cross-language
controls rotate languages and verify every output, including binary contents and
double-transform round trips. There is no CPU isolation or claim of statistical
population performance. Small changes need confirmation; large scaling changes
are robust. Historical medians are from the collections report, not a matched
hardware-frequency guarantee. Raw samples and hashes accompany every table.

Starting compiler is a frozen binary built at 21db415. The delivered code includes
52e6fd0 (flat-arena policy); later commits only publish evidence. Reference and native
paths still run the same typed HIR. Existing source hashes match the prior corpus
verification exactly. New nested-field code is a diagnostic workload, not a new
corpus task or an edited baseline.

## Bulk equality and third-party applicability

The compiler proves a complete, guarded unit-stride equality scan: lengths equal,
index starts at zero, equality starts true, condition tests index below length then
previous equality, body compares exactly both indexed elements and advances by one,
finish returns the accumulator, length mismatch returns false. Every executed
instruction is accounted for, including dead reads. Altered bounds/steps/exit
values, extra trapping accesses, calls and unproved shapes use ordinary lowering.
A source-authored provider loaded under ID 19 / operation 4 receives the same
optimization. The recognizer never examines names, IDs or paths; it matches a HIR
DAG and ignores spans and independent instruction order. This is a narrow compiler
idiom optimization, not a promise that arbitrary plugin algorithms become bulk calls.

Borrow/effect proofs still come from the validated body. The reference interprets
that body; native uses a private nonallocating length guard plus `memcmp`. Only
Bytes and i64 Buffer qualify: byte/integer equality has unique bit representations.
Lengths and immutable state prove both full payload ranges accessible. Empty and
length-mismatch cases access no payload; there is no observable short-circuit trap
or effect to lose. Caller argument order and instruction/depth accounting stay intact.

| 16 MiB whole-file equality | Before ms | After ms | Historical pre-plugin ms |
|---|---|---|---|
| O0 | 96.153 | 7.738 | not recorded |
| O2 | 16.974 | 7.220 | 7.230 |


O2 improves by 57.5%. This is a read+read+compare workload, not pure dispatch latency.
The optimized loop call changes from `nil_plugin0_fn0` to `nil_bulk_compare`;
root-call counts are unchanged. Near-miss providers retain their original checked
loop. See [IR evidence](V5_DEBTS_IR.txt) and the named plugin parity tests.

## Why record-field append depended on the comparison

The old aggregate retained its field while a projection added another root, so
runtime uniqueness correctly rejected concat reuse. At 160k, the same IR and all
three runtime controls execute 320,003 allocations/frees, 480,000 copies,
12,800,240,000 copied bytes and 799,998 list visits, **zero child-row visits**.
At 10k/40k they copy 50,015,000 / 800,060,000 bytes: quadratic work.
Instrumented copy components account for roughly 291–313 ms at 160k; instrumentation
perturbs compilation, so it is attribution, not headline timing.
[Component output](V5_DEBTS_COPY_COMPONENT.json) preserves those counts.

To isolate the comparison-dependent difference, compile the frozen starting IR/C
with ONLY `NIL_RECORD_BUFFERS` toggled. Both executions are sound for this flat
workload; no actual child rows appear. The generic root SCC leaves 53 out-of-line
retain/drop sites; specialization leaves zero. Root/copy compilation context alone
reproduces the loss; it is not additional child traversal or changed copied bytes.
Exact CPU/cache-cycle attribution beyond this intervention was not established and
is not asserted. We fix the structural copying rather than choosing generic root
calls for every program and reintroducing the ordinary append penalty.

| Iterations | Specialized-root ms | Generic-root ms |
|---|---|---|
| 10000 | 3.745 | 3.802 |
| 40000 | 17.159 | 17.371 |
| 160000 | 392.798 | 342.808 |


[Controlled macro experiment](V5_DEBTS_ROOT_CONTEXT.json) includes identical IR hash
and alternating samples. The direct field proof transfers only the overwritten
field's root to its projection. It requires one concat/result consumer, immediate
overwrite, no later old-field access/escape, and no allocation until any final
other-field read. Other field/caller/arena-parent aliases still count; runtime
uniqueness and copy-equivalent quota reservation still guard mutation.

## Builder curves: paired starting compiler versus delivered compiler

| Workload | N | Before ms | After ms |
|---|---|---|---|
| record-append | 10000 | 3.694 | 2.655 |
| record-append | 40000 | 17.089 | 3.649 |
| record-append | 160000 | 396.653 | 7.568 |
| nested-build | 1000 | 8.350 | 2.400 |
| nested-build | 4000 | 106.717 | 3.053 |
| nested-build | 16000 | 1649.040 | 4.588 |
| nested-build-shared | 1000 | 6.348 | 2.318 |
| nested-build-shared | 4000 | 65.214 | 2.760 |
| nested-build-shared | 16000 | 1004.796 | 3.960 |
| nested-field | 10000 | 4.196 | 3.890 |
| nested-field | 40000 | 18.702 | 18.119 |
| nested-field | 160000 | 357.479 | 355.158 |


Larger delivered-only points (no extrapolated before numbers):

| Workload | N | After ms |
|---|---|---|
| record-append | 256000 | 9.910 |
| nested-build | 64000 | 8.892 |
| nested-build | 256000 | 28.995 |
| nested-build-shared | 64000 | 6.205 |
| nested-build-shared | 256000 | 18.040 |


[All builder samples](V5_DEBTS_BUILDERS.json). Small points include ~2–3 ms startup;
large fresh/shared and direct-field points have approximately linear scaling.
Retaining the single-use concat state avoids dropping/re-retaining all existing
child edges at every backedge. Temporaries still follow ordinary last-use roots.
Copies still occur for active aliases, including fields in a retained parent buffer.
The nested-field curve remains quadratic: its parent edge keeps the old child alive
until row replacement. Existing direct-field proofs cannot remove that edge or
exclude aliases in another row. A deeper row/field-path proof is needed; none was
assumed or silently relaxed here.

## Arena-policy failures found by the controls, and fixes

The first policy swept only at physical exhaustion. It fixed fresh construction
but accumulated dead large payloads: keyed repack 64k rose 74.495 → 155.793 ms,
and nested-field 40k rose 19.210 → 59.754 ms. These real regressions are preserved
in [failed keyed policy](V5_DEBTS_EXHAUSTION_ONLY_KEYED.json) and
[failed builder policy](V5_DEBTS_EXHAUSTION_ONLY_BUILDERS.json), not counted as final.

Collecting when garbage reaches `max(64 KiB, live / 4)` keeps sweep spacing geometric
for growing live graphs while promptly releasing copied large payloads. Physical
arena capacity is still bounded by 64 MiB, including dead entries; before any
reservation exceeding that cap, collection yields the same live set used by the
old eager policy. The semantic live/copy-reservation rule is unchanged.

Applying that scheduling to flat programs still cost ordinary append ~6% in a
[40-repeat paired test](V5_DEBTS_BOUNDED_FLAT_APPEND.json) (23.851 → 25.271 ms). The final policy therefore uses the
existing validated whole-program type proof: no record buffers means no transitive
heap child edges, so eager flat-arena reclamation remains. Child-aware/mixed programs
use the bounded deferred policy. This is type-driven, not a benchmark-name exception.
Final controls below supersede all earlier policy timings.

## Established controls, every historical comparison

| Control | Historical NIL ms | Delivered NIL ms | C++ ms | Python ms |
|---|---|---|---|---|
| append 1 MiB | 24.764 | 22.851 | 5.055 | 44.388 |
| newline scan 16 MiB | 7.836 | 7.599 | 10.113 | 24.087 |
| transform 16 MiB | 37.922 | 36.670 | 13.240 | 770.448 |


Append curve and scan sizes, with unchanged baselines:

| Workload / size | Historical NIL ms | NIL ms | C++ ms | Python ms |
|---|---|---|---|---|
| append / 10000 | 2.853 | 2.878 | 2.534 | 14.742 |
| append / 40000 | 3.519 | 3.490 | 2.625 | 15.669 |
| append / 160000 | 6.071 | 5.729 | 2.873 | 18.934 |
| append / 640000 | 16.157 | 14.936 | 4.083 | 32.737 |
| append / 1048576 | 24.764 | 22.851 | 5.055 | 44.388 |
| newlines / 4096 | 2.551 | 2.573 | 2.445 | 14.262 |
| newlines / 1048576 | 2.890 | 2.906 | 2.892 | 15.094 |
| newlines / 16777216 | 7.836 | 7.599 | 10.113 | 24.087 |


File transform and stages:

| Bytes | Historical full NIL ms | Read-only ms | Read+write ms | NIL full ms | C++ ms | Python ms | Round trip |
|---|---|---|---|---|---|---|---|
| 4096 | 2.651 | 2.402 | 2.454 | 2.698 | 2.537 | 14.512 | True |
| 1048576 | 5.143 | 2.528 | 2.962 | 5.121 | 3.413 | 65.010 | True |
| 16777216 | 37.922 | 5.154 | 12.001 | 36.670 | 13.240 | 770.448 | True |


Keyed paths (all sizes, including remaining repacking limits):

| Workload | Iterations / held bytes | Historical ms | Delivered ms |
|---|---|---|---|
| insert | 1000 | 2.520 | 2.672 |
| insert | 4000 | 2.723 | 2.706 |
| insert | 16000 | 4.352 | 4.289 |
| insert | 64000 | 10.633 | 10.545 |
| repack | 1000 | 2.666 | 2.634 |
| repack | 4000 | 2.856 | 2.806 |
| repack | 16000 | 7.063 | 6.941 |
| repack | 64000 | 74.495 | 73.922 |
| repack-held | 4096 | 2.508 | 2.594 |
| repack-held | 65536 | 3.922 | 3.913 |
| repack-held | 1048576 | 22.191 | 22.637 |
| record-insert | 1000 | 2.535 | 2.707 |
| record-insert | 4000 | 2.836 | 2.791 |
| record-insert | 16000 | 4.547 | 4.436 |
| record-insert | 64000 | 11.469 | 11.246 |
| record-append | 10000 | 3.609 | 2.591 |
| record-append | 40000 | 16.948 | 3.535 |
| record-append | 160000 | 409.224 | 7.027 |


Collection paths, including genuine alias copies:

| Workload | Elements | Historical ms | Delivered ms |
|---|---|---|---|
| build | 1000 | 2.651 | 2.492 |
| build | 4000 | 2.486 | 2.396 |
| build | 16000 | 3.216 | 2.975 |
| build | 64000 | 5.666 | 5.066 |
| build | 256000 | 15.748 | 13.422 |
| build | 1048576 | 56.659 | 47.891 |
| update | 1000 | 2.478 | 2.506 |
| update | 4000 | 2.257 | 2.245 |
| update | 16000 | 2.377 | 2.331 |
| update | 64000 | 3.124 | 2.774 |
| update | 256000 | 4.903 | 4.674 |
| update | 1048576 | 12.880 | 12.579 |
| nested-build | 1000 | 8.312 | 2.344 |
| nested-build | 4000 | 107.222 | 2.626 |
| nested-build | 16000 | 1663.409 | 3.971 |
| nested-build-shared | 1000 | 6.329 | 2.330 |
| nested-build-shared | 4000 | 65.535 | 2.469 |
| nested-build-shared | 16000 | 1008.033 | 3.262 |
| nested-update | 1000 | 2.540 | 2.470 |
| nested-update | 4000 | 2.353 | 2.337 |
| nested-update | 16000 | 2.839 | 2.781 |
| nested-update | 64000 | 4.706 | 4.706 |
| nested-update | 256000 | 12.473 | 12.434 |
| nested-update | 1048576 | 44.356 | 44.327 |
| alias-build | 1000 | 2.694 | 2.663 |
| alias-build | 4000 | 4.678 | 4.815 |
| alias-build | 16000 | 53.996 | 48.287 |


[Controls and baseline samples](V5_DEBTS_WORKLOADS.json), [transform stages](V5_DEBTS_TRANSFORM.json),
[keyed curves](V5_DEBTS_KEYED.json), [collection curves/boundaries](V5_DEBTS_COLLECTIONS.json).
Construction 4,194,300 / replacement 2,097,148 / append 2,097,146 scalar rows still
succeed; each next value traps E013. Integer/scalar-record map ceilings remain
262,145 / 262,144; next insert traps. No limit was raised. The benchmark verifies
byte-exact transform output and a double transform returning the original input.

## Validation after the last runtime change

- `./scripts/ci.sh`: 368 tests; strict Clippy, zero warnings.
- `./scripts/ci.sh release`: 368 tests, zero warnings.
- `./scripts/sanitize.sh`: 142 tests across all six suites, O0/O2; no ASan/UBSan findings.
  macOS LeakSanitizer is disabled as documented: this is not a leak-freedom claim.
- Seeds 1729 / 8675309 / 5130572: 332 programs + 664 native builds each;
  **996 programs / 1,992 native builds, zero divergences**. Each hits all 12 new
  bulk, 6 field-transfer and 6 nested-builder families; all 268 named families
  occur once per seed, plus 64 other construction/effect cases. Full mutation and
  call-family counts are in the JSON receipt.
- Frozen corpus: 2,775 checks (553 reference + 1,106 native O0/O2 + 558 Python +
  558 C++). Original cohort separately 610. 79 tasks / 66 supported / 13 unsupported,
  unchanged; all recorded source hashes identical to prior verification.

| Code | Seed 1729 | Seed 8675309 | Seed 5130572 |
|---|---|---|---|
| E009 | 2 | 2 | 2 |
| E012 | 18 | 18 | 18 |
| E013 | 25 | 25 | 25 |
| E014 | 5 | 5 | 5 |
| E015 | 4 | 4 | 4 |
| E016 | 10 | 10 | 10 |
| E017 | 3 | 3 | 3 |
| E018 | 5 | 5 | 5 |
| E019 | 3 | 3 | 3 |
| E020 | 6 | 6 | 6 |
| E021 | 5 | 5 | 5 |
| E022 | 3 | 3 | 3 |
| OK | 243 | 243 | 243 |


Named tests cover independent third-party lowering, bounds/stride/result near
misses, dead pre-guard reads, alias/partial/length/extreme-i64 comparison, field
caller/other-field aliases, old reads and allocation-before-other-field reads,
shared/fresh retained children, lazy traps and quota failures. Both native
optimization levels match the reference. Fuzz and sanitizers found no correctness
bug this round; the performance controls found the two sweep-policy regressions
above, which were fixed and followed by full reruns. One superseded campaign's
last seed was terminated (exit 143) and retried; it was never counted as a pass.

## Remaining accepted limits

The three original debts shrink: bulk equality is restored; direct dead-field
append and single-use fresh/shared builders are linear in the measured range.
Still conservative: child append through a live parent-buffer row (measured above),
genuinely aliased builders (measured alias curve), allocating nested regions/calls
outside the retention proof, and size-changing keyed payload repacking. The
reference evaluator traverses live graphs and is an oracle, not a fast backend.
Mixed record-buffer programs still pay child-aware accounting; no universal C++
parity is claimed. No claim is made that every provider algorithm is recognized.

## Reproduction

Freeze/build the old compiler from 21db415 in a separate local worktree (initialize
its pinned submodule if Cargo requires example files). Build current compiler with
`cargo build --release -p nil --locked --offline`. Pass the frozen binary to the
paired tools; do not use a current binary relabelled as old. Exact executed commands
are in the receipts. Representative commands:

```sh
python3 benchmarks/application/plugins/run.py --before-compiler /tmp/nil-before/target/release/nil --before-revision 21db415 --workload whole-file --repeats 25 --output /tmp/nil-equality
python3 benchmarks/application/collections/root_context.py --compiler /tmp/nil-before/target/release/nil --repeats 25 --output /tmp/nil-root-context
python3 benchmarks/application/collections/debt_curves.py --before-compiler /tmp/nil-before/target/release/nil --repeats 25 --output /tmp/nil-builders
python3 benchmarks/application/collections/debt_diagnosis.py --repeats 9 --output /tmp/nil-copy-components
python3 benchmarks/application/collections/run.py --repeats 25 --output /tmp/nil-collections
python3 benchmarks/application/keyed/run.py --records --repeats 25 --output /tmp/nil-keyed
./scripts/bench.sh runtime --full --workloads --workload append --workload newlines --repeats 25 --output /tmp/nil-workloads
./scripts/bench.sh runtime --full --application --repeats 25 --output /tmp/nil-transform
```

The root-context assembly inspection uses macOS `otool`. The original component
counter experiment also requires pre-change field IR to reproduce the old work
counts; running it with the optimized compiler intentionally counts fewer copies.
These are compiler/runtime experiments, not additions to the adaptation corpus.

