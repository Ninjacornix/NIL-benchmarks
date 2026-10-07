# Round 21: natural programs, copies, memory and limits

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
binaries are separate from timing/RSS binaries. Peak observed live capacity is
sampled after complete reconciliations, excluding transient retain-before-drop
counts. It is not RSS, allocator overhead, or the prospective copying reservation.
The reported headroom ratio is observed live charge divided by the existing
64 MiB limit. The collector may retain unrooted physical storage, so RSS can exceed
this live accounting. Historical-control measurements must also be reported.

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
