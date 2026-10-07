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
