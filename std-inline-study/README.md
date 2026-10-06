# Round 18 controls

Original project-authored fixtures and runners, covered by this repository's MIT
license. No frozen corpus programs, tasks, baselines, or goldens are changed.
Python uses the standard library only. All outputs must be outside either checkout.
Use the same Clang for NIL and C++, O2, at least 25 measured repetitions. On this
macOS run C++ links libc++; Linux users may need to adjust that platform flag.

## Reproduce

Build the baseline compiler from main commit `8647ba7` in a separate local worktree,
and save its executable outside the checkout **before** building the final compiler.
The benchmark baseline is `0766a90`; these runners are on its descendant branch.
Replace `/tmp/nil-round18/nil-before` below with the saved baseline executable.

```sh
cargo build -p nil --release --locked --offline
python3 benchmarks/ownership-study/run.py --compiler /tmp/nil-round18/nil-before --output /tmp/nil-round18/before --repeats 25
python3 benchmarks/ownership-study/run.py --compiler target/release/nil --output /tmp/nil-round18/after --repeats 25
python3 benchmarks/std-inline-study/push.py --before /tmp/nil-round18/nil-before --after target/release/nil --output /tmp/nil-round18/push --repeats 25
python3 benchmarks/std-inline-study/maps.py --compiler target/release/nil --output /tmp/nil-round18/maps-final --repeats 25
python3 benchmarks/std-inline-study/profile_maps.py --compiler target/release/nil --output /tmp/nil-round18/map-profile
```

For a follow-up with revisions interleaved, reuse the prepared executables:

```sh
python3 benchmarks/std-inline-study/repeat.py --before /tmp/nil-round18/before --after /tmp/nil-round18/after --output /tmp/nil-round18/sort-repeat.json --control sort_source_65536 --control sort_source_1048576 --control sort_core_1024 --repeats 25
```

`--argv0 nil-control` holds argv[0] constant. The additional
`--same-executable-path /tmp/nil-round18/shared-executable` copies each executable
to one path before its timer, isolating launch-path effects. Run campaigns
sequentially: overlapping timing jobs invalidate their samples. Follow-ups are
reported separately rather than pooled or substituted for the original table.

`ownership-study/run.py` also accepts `--prepare-only` then `--run-only` for building
all controls before timing. Raw JSON contains every sample, min/median/max, and
proof/disassembly observations; expected output is checked each run. Push compares
identical predicates. Map insert includes startup/read/construction; other operations
subtract a paired construction sample and divide by three passes of N. Negative
marginal estimates are noise, not negative execution time. C++ does not implement
NIL's immutable aliases or storage quota. The ordered baseline matches the algorithm
class, not NIL's complete value semantics.

The profiling runner instruments an external copy of emitted C, checks checksums,
and records allocations/hash/probes/reuses/copies/quota admission. Timed runs use
the production runtime. The report distinguishes measured work from causal wall-time
percentages it cannot establish. See [preregistration](../ownership-study/ROUND18_MAP_PLAN.md)
and [the report](../reports/2026-10-06/ROUND18.md).
