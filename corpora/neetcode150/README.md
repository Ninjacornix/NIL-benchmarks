# NeetCode 150 — Core 1.0 qualification

This is a new, original suite, not a copy of a coding site's tests. `tasks.json`
pins the public 150 names and 18 categories and specifies our own byte contracts.
`CENSUS.md` freezes the forecasts and two-per-category hash sample before NIL
solutions. ADR 041 in the compiler repository defines qualification.

Only factual public labels and identifier links are reused from the pinned
neetcode-gh metadata. We did not import problem statements, examples, tests or
solution code. All new contracts, generators, oracles and reference solutions are
original work under this repository's MIT license. The upstream sites' content
is not relicensed here. This suite is not endorsed by LeetCode or NeetCode.

Inputs are `input.bin`; solutions write `output.bin`. Output order, separators
and final newlines are part of each contract. Empty legal inputs and invalid
inputs must not be confused. The suite only feeds contract-valid inputs.
Largest fixtures and seeded generators are fixed before NIL authoring. Successful
NIL solutions must agree with the Python and C++ references in the reference
evaluator and native O0/O2. A census prediction is not a verified solution.

No generation, training or compiler modifications are part of this study. Raw
artifacts and unsuccessful candidates belong outside git. Source-density counts
are separate from failure-inclusive model tokens per correct program.

## Current status

The fixed 36-sample experiment admitted 29 byte-correct NIL programs. Seven fail
the validation budget and are not included as passing sources. After Round 20's
operator/binding rewrites, seven of the 29 miss the 3× C++ performance bound and
**twenty-two meet both gates** (nineteen at Round 19). The other 114 problems
are unattempted in NIL. See `STATUS.json`,
[the Round 19 measured report](../../reports/2026-10-07/CORE_1_0.md) and
[the Round 20 report](../../reports/2026-10-07/ROUND20.md). This suite is a
qualification yardstick, not an announcement that Core 1.0 is complete.
`FEATURE_AUDIT.json` corrects the overly narrow preregistered string-risk tags
without editing the original forecasts. `density-cuts/` holds the separately
reported full-program, kernel-only and minimal-I/O measurement copies; they do not
modify any frozen task, fixture, golden or baseline source.

## Run from the compiler repository root

```sh
python3 benchmarks/corpora/neetcode150/verify.py --baselines-only --all --output /tmp/core-baselines.json
python3 benchmarks/corpora/neetcode150/verify.py --verified-only --output /tmp/core-verified.json
python3 benchmarks/corpora/neetcode150/verify.py --verified-only --jobs 1 --timing-repeats 15 --output /tmp/core-performance.json
benchmarks/paired/.venv/bin/python benchmarks/corpora/neetcode150/density.py --verification /tmp/core-verified.json --output /tmp/core-density.json
python3 -m unittest discover -s benchmarks/corpora/neetcode150 -p 'test_*.py'
```

Require Clang, the pinned Rust toolchain and the existing benchmark Python
environment for tiktoken. No new dependencies. `NIL_CLANG` selects the same driver
for NIL and C++. Use `--jobs 1` for timing. Omitting `--verified-only` checks all
36 selected tasks and fails on the seven missing candidates; `--all` requests
all 150 and does not silently skip unauthored solutions. `--task <slug>` selects
an individual contract. `--candidate-dir <outside-checkout>` attempts failed or
new sources without admitting them to the verified corpus.

Inputs/goldens remain frozen. `--freeze` refuses to overwrite changed goldens.
All execution paths check byte output, returned length, unexpected effects and
unchanged input. A correctness pass without timing is `performance-pending`,
not qualification. Largest fixtures are realistic size envelopes, not exhaustive
worst-case shape coverage; a separately registered release audit is still needed.
