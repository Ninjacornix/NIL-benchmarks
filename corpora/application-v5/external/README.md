# Frozen external task selection

Fifty exercises are selected mechanically: the first alphabetically sorted directories
with canonical-data.json in Exercism problem-specifications at revision
`9943fd751b684ba1a6a8673c3700a6e79c10a808`. This selection was frozen before authoring references, classifying NIL
support or measuring token counts. No selected task may be dropped. Each task is
externally derived; adapted transport, new fixtures and reference implementations
will be authored here. The original 25 in-house tasks remain separate and unchanged.

Canonical data is reproduced under MIT with Exercism's copyright notice and license
in EXERCISM_LICENSE. selection.json includes immutable source URLs, hashes and
instructions where available. Existing exercise semantics motivate every adaptation;
any narrowed domain/API must be disclosed, not represented as the entire upstream
exercise. Unsupported capabilities remain in the task list.

This alphabetical single-source sample removes discretionary task picking but does
not make the sample statistically representative. Alphabetical clustering, upstream
curriculum bias, locally authored solutions/adapters and finite tests remain limits.
No model inference or compiler changes are authorized by this experiment.

## Frozen adaptation scope

Each task targets the first property declared by its first canonical leaf case;
all cases for that property are retained, excluding UUIDs explicitly superseded
by `reimplements`. This is a mechanical API-component sample, **not full exercise
coverage**. Transport/error formatting is disclosed per task. The original 25-task
manifest, oracles, literal goldens and all 74 sources remain byte-identical.
`build_manifest.py` reproduces the new byte transports and expected-value maps
from pinned upstream data; it does not use any authored reference solution.

The new oracle is a finite canonical input/expected-output lookup, with UUIDs and
SHA-256 provenance. It rejects unknown inputs rather than inventing outputs. It
is executable for these fixtures, not a general algorithmic oracle. Broader hidden
and randomized fixtures are future work. Where only one upstream input exists,
the verifier's appended golden repeats it; counts are execution checks, not counts
of independent cases.

Classification before token counting: 31 new supported properties, 19 retained
unsupported. Width review exposed upstream 108/127-bit Armstrong cases; retained
and marked unsupported. The invalid-binary wording was corrected to match already
frozen null outputs. No expected value or source case was changed for either fix.

Unsupported includes hard missing operations/contracts and adapter/library gaps.
Map/tree/calendar/dictionary tasks can potentially be emulated in bytes/i64; their
status means no verified adapter exists here, not theoretical unexpressibility.
This affects the density denominator and must be reported prominently.

The 31 supported references are locally authored, not upstream solutions. Python
uses standard-library operations where applicable; new C++ uses clang-format
23.1.2 (LLVM style, four spaces, 100 columns). Neither tasks nor sources may be
rewritten after counts are observed. Two first NIL algorithms exceeded unchanged
100,000-step limits: coin-change DP and Hex flood sweeps. Branch-and-bound and
union-find replacements pass the same fixtures. A separate 3,125-state comparison
checks the book-store grouping formula against independent subset DP; this is
additional algorithm evidence, not 3,125 NIL native execution checks.

## Reproduce

From the compiler checkout:

```sh
benchmarks/paired/.venv/bin/python -m unittest discover -s benchmarks/corpora/application-v5/tests -v
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/verify.py --group original --output /tmp/nil-external/original.json
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/verify.py --output /tmp/nil-external/verification.json
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/density.py --verification /tmp/nil-external/verification.json --output /tmp/nil-external/density
```

The existing native O0/O2, in-memory Host, Clang/Python runners, quota, 100,000-step
and 256-call limits are reused unchanged. Unsupported rows remain blank, never
zero-token solutions. The original self-authored 24, the new supported external
properties, and their combined paired set must be separately reportable.
