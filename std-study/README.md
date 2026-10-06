# Round 14 source standard-library study

No model inference, corpus rewrite or changed oracle. Source std is shipped in the
parent repository's `std/`; these tools audit spelling, performance and rejected
migration prototypes. Compiler and benchmarks commits are local only.

From the parent checkout (Rust toolchain, Clang/LTO and the existing paired Python
environment required):

```sh
benchmarks/paired/.venv/bin/python benchmarks/std-study/naming.py
benchmarks/paired/.venv/bin/python benchmarks/std-study/run.py --repeats 25 --output /tmp/nil-std/performance
benchmarks/paired/.venv/bin/python benchmarks/std-study/candidate_audit.py --output /tmp/nil-std/candidate-audit
benchmarks/paired/.venv/bin/python benchmarks/std-study/copy_census.py --output /tmp/nil-std/census
```

Keep outputs outside the checkout. `run.py` builds the current release compiler,
compiles O2 controls, saves LLVM IR/disassembly and validates every timed output.
It uses one warm-up and at least 25 rotating, whole-process wall-time repetitions.
Cached 16 MiB input, subprocess startup and stdout capture are included. No CPU
isolation or confidence interval is claimed; min/median/max expose noise. Read
parent `docs/validation/V5_STD_SURFACE.md` for the results and historical controls.

The materialized map/filter controls compare equivalent caller-written loops;
filter is slow in both forms and parity does not establish C++-class performance.
The separate scan controls reproduce Round 13's map-reduce shape across a module.
The equality provider uses a different ID and mirrored comparisons; IR evidence
requires an actual bulk call, not merely its declaration. Vector flags inspect
entry disassembly, not unrelated runtime functions.

`find_candidate.nil`, `has_candidate.nil` and `parse_candidate.nil` are rejected
prototypes, not migrated or auto-loaded std. Their speed and quota/failure results
are retained. `candidate_audit.py` compares native core/prototype diagnostics at
O0/O2; shipped std additionally has reference/native tests and differential fuzzing.

The census is an origin-set fixed point over validated HIR. It counts static calls
returning a dynamically owned parameter updated by Replace/Concat/Put/Insert,
including projected fields. It excludes fresh builders. It is **not** a caller
uniqueness proof, dynamic frequency, or measurement of copies. The std probe and
unchanged comparator sort are reported separately from the 68 corpus programs.

This directory contains original project tooling and prototypes under this
repository's license. It contains no raw measured results, binaries or inputs.
