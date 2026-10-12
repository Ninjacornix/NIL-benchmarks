# natural-v2 — rewrites using sum and recursive types (ADR 050)

New measurement copies. The v1 cohort in `../natural/` is frozen and unchanged,
as are the NeetCode tasks, oracles and fixtures.

## Scope

Only programs whose v1 encodes *structure* as integer links with offset
arithmetic are candidates:

* `balanced-binary-tree` — v1 needs four functions: an explicit heap stack, a
  memo buffer and `a[3+3*k]` child arithmetic.
* `validate-binary-search-tree` — v1 is a single in-order loop over an explicit
  stack.

* `course-schedule` — v1 encodes adjacency as three parallel integer-link
  buffers. v2 uses a wrapper record, `record Row(to:v)` with `v[Row]`, which
  needed **no new feature**: ADR 030 already supplies nested sequences that way.

Deliberately excluded:

* `reverse-linked-list` — its `a[2+2*c]` offsets parse an index-linked *input
  format* that the Python and C++ references also parse. That is not a
  workaround, so there is nothing to remove.

Written naturally, without tuning for compiler behaviour.

## Result

Both programs differentially match v1 on all seven frozen fixtures through the
file entry, and six of seven pass at reference, O0 and O2.

**Neither qualifies.** The frozen `largest` fixture is a 100,000-node chain of
depth 100,000, and the qualification harness builds with `call_depth: 256`
(`benchmarks/helpers/core_check.rs`), so the natural recursive formulation
reports `E008 call depth limit exceeded` at O0 and O2 on that fixture. This is
why v1 simulates recursion with an explicit heap stack: recursive types remove
the encoding but not the reason for it.

`course-schedule` is the clearest negative result of the round. Its v2 is 26
kernel tokens shorter (−7.4%) and **3.75× slower**: 16,680.95 ms against v1's
4,448.40 ms on the largest fixture at O2, where C++ takes 22.55 ms, so
739.807× versus v1's 197.288×. Appending to a sequence held in a field of a
still-live record-buffer row remains quadratic (ADR 030's published debt),
while integer links prepend in O(1). O0 and O2 both pass every fixture; only
the reference evaluator exceeds its deadline on the largest one. The useful
work is therefore not a new type but proving in-place append for a child
inside a live row.

`kernels/` holds the kernel-cut copies counted in the token table, matching the
cut defined by `benchmarks/corpora/neetcode150/density-cuts/README.md`.

See `docs/ROUND26.md` in the compiler repository for the token and timing
tables and the full list of accepted limits.
