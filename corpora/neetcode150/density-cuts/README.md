# NeetCode source density: three cuts

These are new measurement copies, not edits to the frozen Python/C++ references
or their contracts, fixtures and goldens. They cover the same 29 admitted programs.
Source density is not total model tokens to a correct program, including repairs.

* **Full program:** the admitted NIL and historical standalone Python/C++ files.
  This reproduces Round 19, including its repeated Python `Numbers` reader.
* **Kernel only:** typed algorithm functions, all transitive algorithm helpers,
  signatures, required record/type declarations and imports. Byte decoding,
  encoding and file drivers are excluded in every language. NIL keeps its actual
  flat-buffer layout and metadata offsets; those are not hidden by a free adapter.
* **Minimal I/O:** new iterator/stream-based baseline programs. NIL already has
  compact file adapters, so this cut copies its admitted source unchanged.

`kernels/` contains the counted code. `kernel-host/` embeds those algorithms in
executable adapters; `minimal-io/` contains the standalone measurement copies.
Python and C++ kernels are the algorithm portions of their copied programs.
NIL kernels are renumbered positional functions extracted from the typed-result
copies; callback parameters are kept in their separate caret namespace. NIL
HOF kernels are instantiated and type-checked in their full host wrappers, which
are checked against frozen oracles. They cannot be checked as standalone entry
programs without a concrete callback; ordinary kernels also get a CLI check.
The named input/serialization inventory is in `MANIFEST.json`; `build.py` makes
the transformations reproducible.

Separating formatting changes the result representation of four NIL algorithms.
Intervals produce a flat integer buffer; parentheses/phone combinations expose
completed strings through static output callbacks. A materialized record-buffer
parentheses copy hit the reference timeout and is not included as verified. For 3sum's largest fixture, materializing 1,124,250 integer
triples exceeded the unchanged 64 MiB quota in reference and O0/O2. Its kernel
therefore streams typed triples through an explicit static callback; its formatter
is an adapter. The callback signature/state cost remains in the kernel count.
This is an interface distinction from the baseline kernels' materialized results,
not proof that one representation is cheaper under all output conventions.

```sh
python density-cuts/build.py
python density-cuts/verify.py --output /tmp/nil-cuts-verified.json
python density-cuts/measure.py --verification /tmp/nil-cuts-verified.json \
  --cohort-verification /tmp/nil-cohort-verified.json --output /tmp/nil-cuts.json
```

Run from `corpora/neetcode150/` with the benchmark Python environment. Verification
uses the same reference helper, native O0/O2, Python/C++ and byte-exact frozen
outputs as `verify.py`. It also rejects missing builds or mismatched source hashes.
No kernel result is counted as correct without its full wrapper passing.

These cuts expose driver sensitivity rather than replacing a generation study.
The algorithms were authored in-house, use different language-specific storage
representations, and are a selected 29-problem cohort, not an unbiased estimate
for all 150 problems. Existing licensing/provenance remains in the parent corpus.
