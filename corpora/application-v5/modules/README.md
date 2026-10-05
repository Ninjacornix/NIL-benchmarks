# Alternate source-module corpus solutions

`count_newlines.nil` and `sum_integers.nil` implement existing original tasks with
one shared `reports.nil-module`/`reports.nil` library. The third function is private.
The original programs, tasks, baselines, oracles and goldens remain unchanged.
These alternate sources inherit this corpus's MIT licensing and provenance.
They are not new task statements or additional adaptation positives.

```sh
# Run from NIL root; initialized benchmark submodule and its Python env required.
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/modules/verify.py --output /tmp/module-corpus.json
benchmarks/paired/.venv/bin/python benchmarks/module-study/split_tokens.py --output /tmp/module-tokens.json
```

Verification reuses the existing application harness and checks each frozen input
plus its unchanged golden in the reference evaluator and native O0/O2. The harness's
optional `manifests` argument feeds both paths; its default condition is unchanged.
Sharing is counted once across both programs. Per-program totals also charge the
whole imported library, including unused functions, and manifest tokens separately.
Raw source density cannot establish generation/repair efficiency.

`multi_file_fixture` is the historical blocker label for external `ex_grep`.
Its JSON inputs name upstream text files, but the frozen host fixture contract only
provisions `input.bin`. This source module system does not provision those runtime
files or supply the missing grep adapter. It remains unsupported; no golden is
changed and no packed substitute is claimed. All 13 prior unsupported tasks remain.
