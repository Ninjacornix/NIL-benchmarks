# Inferred root ownership (Round 25)

This study extends the existing `core-generalize-study` measurements; it does
not replace its oracle, copy ledger, frozen natural sources, or qualification
rule. ADR 049 in the compiler repository preregisters R1 (selected-region
continuations), R2 (caller/callee handoff), and R3 (record child extraction).
Report each class separately; an unimplemented class has no claimed gain.

Run correctness gates first. Run timing/RSS alone, with no CI, fuzz, or census
running concurrently. Raw artifacts belong outside the checkout.

```sh
python3 benchmarks/core-generalize-study/measure_cohort.py --repeats 15 \
  --output /tmp/round25/cohort.json
python3 benchmarks/core-generalize-study/measure_controls.py --repeats 25 \
  --compiler "$PWD/target/release/nil" --compiler-revision '<candidate>' \
  --baseline-compiler /absolute/path/to/preserved-round24-nil \
  --baseline-revision 929527d --output /tmp/round25/controls.json
python3 benchmarks/root-ownership-study/measure_auxiliary.py \
  --baseline /absolute/path/to/preserved-round24-nil \
  --output /tmp/round25/auxiliary.json
python3 benchmarks/core-generalize-study/reference_profile.py --copies \
  --working-tree --output /tmp/round25/overlay
python3 benchmarks/core-generalize-study/copy_census.py \
  --overlay /tmp/round25/overlay --scope neetcode-natural --native \
  --output /tmp/round25/census-natural.json
```

Repeat census scopes for `application`, `neetcode-tuned`, and two `fuzz:<seed>`
values. The census uses O0 and bounded fuzz execution; report this explicitly
rather than equating its copy count with optimized unbounded execution. Keep
excluded resource/trace-cap fixtures named. The historical scan fixture is
17 MiB; additionally measure a true 16 MiB scan with `--only scan --scan-bytes
16777216`. Never label the historical fixture as 16 MiB.

`measure_auxiliary.py` measures whole-process frontend plus IR emission, not
Clang/backend compilation. It alternates preserved/current compilers, excludes
one warmup, and times the largest application source. The reference heap
control runs the unchanged largest Last Stone Weight fixture once in isolation,
verifies its output, and reports an explicit timeout if it does not finish.
