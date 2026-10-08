# Round 21: natural programs, copies, memory and limits

## Round 22: repaired fuzz scope

`fuzz_check.rs` supplies the generated entry's actual `(v,s,s,s)` types, using
`[3,-2,9]`, `abc 12`, `input.bin`, and `output.bin`. The fixed census fixture is
1024 bytes (four repetitions of 0–255), not the randomized differential campaign
fixture. Denial, deterministic random seed, environment and directory fixtures
are explicit. Providers use the campaign's existing `compile_case` loader.
Both ordinary and instrumented helpers must agree; native O0 additionally compares
diagnostic codes, stdout, output file and input preservation. E006 aborts rather
than counting an entry mismatch as successful coverage. Fuzz census uses bounded
execution (100,000 steps, 256 calls) because some generated programs never finish.
Application and NeetCode mechanism censuses remain O0 unbounded.

```sh
python3 reference_profile.py --copies --output /tmp/nil-round22-overlay
python3 copy_census.py --overlay /tmp/nil-round22-overlay --scope fuzz:22001 \
  --native --output /tmp/nil-round22-fuzz-22001.json
python3 copy_census.py --overlay /tmp/nil-round22-overlay --scope fuzz:22002 \
  --native --output /tmp/nil-round22-fuzz-22002.json
```

Before ownership changes, both seeds execute all 644 families with no skipped or
unjoinable fixture: 5,240 / 4,983 native payload copies, 88,110,864 / 88,114,519
bytes. Exact category and diagnostic counts are in
`reports/2026-10-07/ROUND22_CENSUS_BEFORE.json`. The existing application and
natural/tuned NeetCode baselines are carried forward with their original receipts;
they were not rerun for this harness-only fix. Raw telemetry stays outside git.

This study does not attempt the 114 held-out NeetCode problems. `natural/` contains
29 byte-exact admitted Round 19 programs from benchmarks commit `6fd268d`.
`NATURAL.json` freezes their hashes alongside the tuned Round 20 hashes. Natural
sources must never be rewritten for performance; correctness corrections require
an explicit separate record. No existing corpus source, oracle or golden changes.

Run from the compiler repository root:

```sh
python3 benchmarks/core-generalize-study/freeze_natural.py
benchmarks/paired/.venv/bin/python -m unittest discover \
  -s benchmarks/core-generalize-study -p 'test_*.py' -v
benchmarks/paired/.venv/bin/python benchmarks/core-generalize-study/attribution.py \
  --output /tmp/nil-round21/attribution.json
python3 benchmarks/corpora/neetcode150/verify.py --verified-only --jobs 1 \
  --candidate-dir "$PWD/benchmarks/core-generalize-study/natural" \
  --output /tmp/nil-round21/natural-correctness.json
python3 benchmarks/core-generalize-study/measure_cohort.py --repeats 15 \
  --output /tmp/nil-round21/cohort-before.json
```

Build `core_check` through `benchmarks/support.py` before using the measurement
runner; the verification command does that. Run measurements alone, not alongside
CI, fuzzing or corpus verification. The whole-process timing rotates natural,
tuned and C++ runs, excludes one warmup, and verifies every result against the
unchanged golden. RSS uses three separate `/usr/bin/time -l` executions per arm
(macOS reports bytes). Qualification is at most 3x the same-session C++ median.
Report natural qualification as the headline and tuned qualification separately.

`measure_clang.py` is a measurement-only wrapper that instruments the compiler's
**temporary generated C runtime**, not any checked-in compiler file. Counter
binaries are separate from timing/RSS binaries. Native observed root charge is sampled after complete reconciliations. It is
**not semantic liveness or quota headroom**: rootless scans retain their input
without rooting it. `reference_profile.py` builds a hashed isolated reference
checkout outside git, sampling instruction-boundary live capacity and prospective
quota reservations separately. `profile_reference_cohort.py` and
`profile_reference_controls.py` run unchanged fixtures through that overlay.
All instrumented results must match the ordinary oracle. Historical control
measurements, including their actual input byte counts, are separately reported.

The exact token ledger reuses the application-corpus byte-overlap classifier on
the unchanged Round 20 kernel-only sources. Every source hash and token count
must match the published density table. Categories partition the total; syntax
inside helpers remains counted and is not duplicated in a "helper" category.
Conditionals include NIL `?:` and Python `if/elif/else`. Binding semicolons are
not loop-region delimiters. Token categories describe spelling costs, not proven
removable costs or model efficiency. No syntax change is proposed this round.

The physical-copy/semantic-observation census is a separate deliverable; these
RSS and token tools do **not** implement it. A root count, static last use or
runtime memcpy counter alone is insufficient to classify future observations.
Do not publish any of those as a completed avoidable-copy census.

## Copy census (Part A1)

`reference_profile.py --copies --output <dir>` builds an isolated version-tracking
overlay outside git: a hashed shadow checkout, a site-labelled measurement HIR, a
reference-evaluator storage trace and an instrumented native runtime. No
checked-in compiler file changes.

```sh
benchmarks/paired/.venv/bin/python benchmarks/core-generalize-study/reference_profile.py \
  --copies --output /tmp/nil-copy-overlay
benchmarks/paired/.venv/bin/python benchmarks/core-generalize-study/verify_copy_overlay.py \
  --helper /tmp/nil-copy-overlay/helper/target/release/reference-profile \
  --output /tmp/nil-tracker-checks.json
benchmarks/paired/.venv/bin/python benchmarks/core-generalize-study/copy_census.py \
  --overlay /tmp/nil-copy-overlay --scope neetcode-natural --native \
  --output /tmp/nil-census-natural.json
```

`--scope` takes `application`, `neetcode-natural`, `neetcode-tuned` or
`fuzz:<seed>`. The three required scopes are the 68 application programs, both
admitted NeetCode cohorts, and every generated family for two seeds.

`copy_ledger.py` is the frozen coverage ledger. Every kind an overlay can emit
must appear in it with a group, and every owning-storage site found by inspection
must appear either there or in `EXCLUDED` with a reason, so a payload copy cannot
be hidden by relabelling it construction. An event kind missing from the ledger
raises and aborts the census; it is never silently AVOIDABLE. `test_copy_ledger.py`
scrapes both overlays and fails if the ledger and the hooks drift apart in either
direction.

Groups: `PAYLOAD_COPY` (duplicates an existing logical value's payload),
`CONSTRUCTION`, `INPUT_DECODE`, `OUTPUT_MATERIALIZE`, `GROWTH_RELOCATION`. Only
`PAYLOAD_COPY` carries the REQUIRED/AVOIDABLE headline, because it is the only
group a generalized ownership analysis could remove. Growth relocation counts a
*certain* reallocation only: the hooks compare physical capacity before and after
and stay silent when nothing moved.

Two metrics are published. `strict` marks a copy REQUIRED when the source version
has any later observation; `payload_only` requires a later observation that reads
element payload. **AVOIDABLE means "no later observation under this metric", not a
proof that the copy is removable**; scheduling can also remove copies inside the
REQUIRED set.

Version IDs are monotonic and assigned at construction and functional update.
Addresses are private lookup keys and are never serialized, so a late read of an
old snapshot cannot be attributed to a newer version that reused its address.
`verify_copy_overlay.py` runs 18 adversaries covering live, dead and
metadata-only old values, slices, selected and unselected lazy arms, returned
aliases, fixed arrays, map key and value arguments, map-owned index and entry
copies, and map value materialization, each checked against the ordinary
evaluator and native O0/O2.

Integrity: the census accepts a program's events only after the instrumented and
ordinary runs agree on exit code, stdout, output bytes and preserved input. The
native census is a **native O0 unbounded mechanism census** joined to reference
versions by site and occurrence. O0 preserves the emitter's copy decisions, which
is what the census measures; it does not claim which copies survive the O2
pipeline. The join is fail-closed: an unknown site, operand role or source version
aborts that fixture and is recorded, never counted as AVOIDABLE. The join streams
the large reference site file and keeps only the rows the small native trace
needs, so the largest qualification fixtures stay in the census.

Fuzz scope sources come from the fuzzer's own `Case::new` with the campaign's
per-case seed derivation, so the census covers exactly the generated programs.
Their input is the census's own deterministic fixture, not the fuzz oracle's
randomized host; the report states that.

## Earlier tooling

The physical-copy/semantic-observation census is a separate deliverable; the
RSS and token tools below do **not** implement it. A root count, static last use
or runtime memcpy counter alone is insufficient to classify future observations.
Do not publish any of those as a completed avoidable-copy census.

### Round 22 tracker correction

Repeated unchanged record programs exposed three drifting reference classifications
(432 bytes total in the application scope). Sequence and empty-map constructors
had not registered births: their private address could inherit an expired record's
version. Decoded aggregate constructors had the same missing hook. The overlay now
registers every such allocation immediately; this changes no checked-in compiler
or execution semantics. The coverage test checks both sequence constructors, the
map constructor and decoded records/arrays; the synthetic tracker regression
checks reused addresses across allocation kinds. The corrected application reference
ledger changes four classifications (528 bytes) against the carried baseline,
including the three initially observed drifting events. Three repeated golden runs each
of BST, BFS and interval merge have identical event classifications after the fix.

Use the same corrected instrumentation on historical and current compilers:

```sh
python3 benchmarks/core-generalize-study/reference_profile.py --copies \
  --revision 92d62b3 --output /tmp/nil-round22-corrected-before-overlay
python3 benchmarks/core-generalize-study/reference_profile.py --copies \
  --output /tmp/nil-round22-corrected-after-overlay
```

Run the repeated golden stability check with:

```sh
python3 benchmarks/core-generalize-study/verify_copy_stability.py \
  --helper /tmp/nil-round22-corrected-after-overlay/helper/target/release/reference-profile \
  --output /tmp/nil-round22-stability.json
```

The original preregistered baseline is retained. Corrected before/after category
counts are labelled retrospective measurement repairs, not revised forecasts.
Fuzz census remains bounded to 100,000 steps; it measures the compatibility path,
not G2's unbounded replay. The differential campaign and separate replay controls
exercise unbounded G2. O0 copy counts describe emitter decisions, not O2 physical
traffic after LLVM optimization.

### Interleaved historical compiler controls

Use the same runner with a separately built historical compiler to rotate old,
current and C++ executions within each repetition. Both compiler path and revision
are required together; binary hashes are recorded. Counter runs remain separate.

```sh
python3 benchmarks/core-generalize-study/measure_controls.py --repeats 25 \
  --baseline-compiler /path/to/compiler-built-from-92d62b3 \
  --baseline-revision 92d62b3 --output /tmp/nil-round22-controls-paired.json
```

`--compiler` plus `--compiler-revision` can instead measure a historical compiler
alone. These options change no workload, fixture, source or correctness oracle.
