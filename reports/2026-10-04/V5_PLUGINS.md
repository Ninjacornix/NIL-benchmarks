# Expr-v5 plugin boundary: measured prototype

## Finding and scope

**The static, compiler-visible boundary preserves borrowing/reuse proofs. The migrated
bulk equality algorithm regresses materially: 7.232 → 16.859 ms (2.33x) at O2 and
7.360 → 96.522 ms (13.12x) at O0 on 16 MiB.** Do not call this a production-ready
replacement for optimized `memcmp`. The repeated-call workload improves at O2,
while O0 adds about 4–5 ns per call. These are effective workload deltas, not isolated
dispatch overhead: algorithm, instrumentation and optimizer differences are included.

ADR 029 was committed first (`eea2e10`). Version 1 links validated local NIL providers
into typed HIR; it is **not a native/dylib ABI**. Only derived nonallocating/non-host
`borrow` providers are admitted. Types include all existing scalars, fixed arrays,
sequences/maps and nested nominal records, within current collection limits.
No raw address escapes; arena ownership/quota remain unchanged. No sandbox claim.
Allocating/host providers, recursive providers and arbitrary foreign code are deferred.

One migration: sequence equality leaves evaluator/runtime implementations and becomes
provider HIR. `!equal` and legacy HIR input remain compatible adapters; direct generic
`!plugin(0,0,...)` works too. Intrinsic enum count stays 32; executable core implementations
become 31 plus one adapter. One new plugin-only operation: immutable `Packet.count`
update retaining nested dynamic fields, with a worked local manifest.

## Boundary measurement

Apple M2, macOS 27 arm64, Apple Clang 21; exact versions, hashes and all 25 samples
in [boundary JSON](V5_PLUGIN_BOUNDARY.json). Before compiler `c4ffcfb`, after
`54a03db`; one warmup, paired alternating before/after execution, whole-process wall
clock, verified stdout every run, no CPU isolation. Builds exclude timed execution.
Functional/sanitizer/fuzz gates finished before these serial measurements. Inputs and
source hashes are frozen in JSON; no compiler or fixture tuning during timing.

`hot` has 16,777,216 changing-byte comparisons on a one-byte scratch sequence
(logical iteration scale, not a 16 MiB working set); output 65536. `hot-file` actually
reads/scans 16 MiB, with 16,777,217 comparisons including the last byte; same output.
`whole-file` reads the same 16 MiB file twice and compares once; result true.

| Workload | Opt | Before ms | After ms | Ratio | Effective delta ns/call |
|---|---|---:|---:|---:|---:|
| hot | O0 | 1493.176 | 1572.914 | 1.053 | 4.753 |
| hot | O2 | 374.048 | 324.553 | 0.868 | -2.950 |
| hot-file | O0 | 1919.354 | 1989.575 | 1.037 | 4.185 |
| hot-file | O2 | 433.580 | 396.647 | 0.915 | -2.201 |
| whole-file | O0 | 7.359 | 96.522 | 13.115 | 89162250.000 |
| whole-file | O2 | 7.232 | 16.859 | 2.331 | 9627042.000 |

Bulk regression is attributable to portable element-by-element HIR equality replacing
C `memcmp` (bytes), rather than lost arena proofs. The reads and program sources are
unchanged. Recommendation: retain an optimized compiler-visible lowering for hot bulk
algorithms before adopting this migration in production, or keep that optimized
implementation in core until such a verified boundary exists. Do not infer that opaque
native plugins are fast from this experiment: no native foreign ABI was measured.
Static body visibility works for hot calls; portable library algorithms can still lose.

## Proof and IR evidence

[Before IR](V5_PLUGIN_BEFORE.ll), [after IR](V5_PLUGIN_AFTER.ll). The hot module has
one root frame and 11 static root stores both before and after; its loop still calls
`nil_set_unique` once and never `nil_set`. The provider itself has zero root frames/stores.
`hot-file` likewise retains 2 frames/28 stores and unique replacement; whole-file
retains 1 frame/6 stores. No new conservative root penalty. Provider functions are not
forced `alwaysinline`; O0 retains the call (`otool` shows `bl _nil_plugin0_fn0`,
recorded in receipts). Borrowing is established by validated HIR
analysis independently of LLVM inlining, and allocating/effectful counterexamples are
rejected. The native test `plugins.rs` also checks rootless pure caller IR and append reuse.

## Existing controls (25 repeats)

All outputs verified, byte transform exact and double-transform round-trip checked.
Same established full-workload harness, whole-process medians in ms; raw samples and
source hashes in [workloads](V5_PLUGIN_WORKLOADS_CONTROL.json),
[transform](V5_PLUGIN_TRANSFORM_CONTROL.json), [keyed](V5_PLUGIN_KEYED_CONTROL.json).

| Workload | Size/iterations | NIL ms | C++ ms | Python ms |
|---|---:|---:|---:|---:|
| append | 10,000 | 2.759 | 2.436 | 14.653 |
| append | 40,000 | 3.534 | 2.516 | 15.710 |
| append | 160,000 | 5.953 | 2.796 | 18.755 |
| append | 640,000 | 16.061 | 3.941 | 32.718 |
| append | 1,048,576 | 24.616 | 5.019 | 44.015 |
| newlines | 4,096 | 2.663 | 2.586 | 15.062 |
| newlines | 1,048,576 | 2.908 | 2.981 | 15.140 |
| newlines | 16,777,216 | 7.581 | 10.215 | 24.147 |
| transform | 4,096 | 2.641 | 2.535 | 14.494 |
| transform | 1,048,576 | 4.919 | 3.330 | 63.340 |
| transform | 16,777,216 | 35.357 | 13.179 | 795.218 |

Previous records-round NIL controls: scan16MiB 7.573, append1MiB 24.626,
transform16MiB 34.991 ms; now 7.581, 24.616, 35.357. Changes are +0.11%, -0.04%,
+1.05%, respectively. These nonisolated separate sessions do not establish a regression.
NIL still loses to C++ on append and transform; the migration did not remove those costs.

| Keyed workload | Iterations | NIL ms |
|---|---:|---:|
| insert | 1,000 | 2.593 |
| insert | 4,000 | 2.684 |
| insert | 16,000 | 4.264 |
| insert | 64,000 | 10.499 |
| record-insert | 1,000 | 2.552 |
| record-insert | 4,000 | 2.837 |
| record-insert | 16,000 | 4.482 |
| record-insert | 64,000 | 11.193 |
| record-append | 10,000 | 3.750 |
| record-append | 40,000 | 16.864 |
| record-append | 160,000 | 401.630 |

Integer-map quota ceiling remains 262,145 entries; Pair scalar-record map remains
262,144 (262,145 fails E013). Record-field appending remains superlinear; this known
aggregate liveness boundary was not changed. JSON retains all repack/held-alias samples.

## Correctness receipts and limits

[Command receipts](V5_PLUGIN_VALIDATION.txt): CI debug/release each **331 tests**,
zero warnings; ASan/UBSan **116 tests**, clean (existing macOS LeakSanitizer exclusion).
[Three fuzz seeds](V5_PLUGIN_FUZZ.json): **792 programs / 1,584 O0/O2 builds**, zero
divergences. Per seed: OK190 E0092 E01214 E01317 E0145 E0154 E01610 E0173 E0184
E0192 E0205 E0215 E0223. Each of 24 new plugin/equality families appears per seed,
including typed record aliases, loops/calls, lazy traps/effects, quota retention and
reclamation. E008 caller-budget tests and E024 source/manifest failures are separate
unit/mutation coverage, not counted as runtime fuzz codes. This is bounded randomized
family generation, not exhaustive provider verification or a security audit.

[Full corpus](V5_PLUGIN_VERIFICATION.json): **2,625 checks**, 61 supported/14 unsupported;
[original](V5_PLUGIN_ORIGINAL.json): **610** separately pass. Tasks, oracles, goldens,
reference sources and baselines unchanged; no density improvement or new model-efficiency
claim. Earlier unfavourable generation result remains. Corpus receipts precede the final
stdlib generic-alias test addition, which does not alter its compatibility-source path.

No sanitizer bug or differential divergence was found. Review caught a test-coverage
mistake: initial budget testing used the unbounded default; it now explicitly tests
bounded eight-step success and seven-step E008 at O0/O2. The material algorithm regression
above is a real finding, not suppressed because correctness gates passed.

## Reproduction

See [harness instructions](../../application/plugins/README.md),
[authoring guide](../../../docs/architecture/PLUGINS.md) in the parent repository,
and ADR 029. Reports record local dirty documentation/untracked harness state honestly;
compiler code revision is explicit. No binaries, large inputs or raw scratch directories
are committed. All changes are local; neither repository was pushed.
