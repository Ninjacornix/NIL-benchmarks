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

Deliberately excluded:

* `reverse-linked-list` — its `a[2+2*c]` offsets parse an index-linked *input
  format* that the Python and C++ references also parse. That is not a
  workaround, so there is nothing to remove.
* `course-schedule` — its adjacency needs sequences of sequences (`v[v]`),
  which is B3 and not implemented.

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

`kernels/` holds the kernel-cut copies counted in the token table, matching the
cut defined by `benchmarks/corpora/neetcode150/density-cuts/README.md`.

See `docs/ROUND26.md` in the compiler repository for the token and timing
tables and the full list of accepted limits.
