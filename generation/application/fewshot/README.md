# Fixed verified-example exposure

`experiment.json` was committed before inference. Select four original verified
NIL corpus programs by its fixed category/lexicographic rule, excluding evaluated
answers, reverse-case near-answers, the already-shown copy example and intrinsics
absent from the frozen reference. Sources/hashes are checked and their reference
and native O0/O2 oracles rerun before requests.

The control prompt is byte-identical to the original application study, including
its generic copy-file example. Treatment adds the same four worked task/program
pairs to every NIL task. The grammar specification is retained, not replaced.
All other request parameters, extraction, repairs, budgets and oracles are frozen.

This adapter calls `application/run.py`, reusing its complete inference/oracle/audit
loop. The only hooks are an explicit experiment definition, prompt factory and
extra provenance files. Default application behavior is unchanged. NIL-only
arms have no within-arm language bootstrap; the adapter pairs conditions itself.

For each pinned model, run the original NIL/Python control then NIL with examples:
72 trials total (24 NIL control, 24 NIL treatment, 24 unchanged Python baseline).
Python is a common rerun baseline, not a fictional second treatment. Models run
sequentially. Condition order is fixed and noted as a confidence limitation.
No smoke inference, substitution, automatic retry or prompt tuning. A complete
model-access failure produces an unavailable outcome, not fabricated usage.

```sh
# From the compiler checkout, using the pinned benchmark Python 3.12:
benchmarks/paired/.venv/bin/python -m unittest discover -s benchmarks/generation/application/fewshot/tests -v
benchmarks/paired/.venv/bin/python benchmarks/generation/application/fewshot/run.py --mock --output /tmp/nil-exposure-stub-NEW
# Start Ollama separately; exact local model digests must match experiment.json.
benchmarks/paired/.venv/bin/python benchmarks/generation/application/fewshot/run.py --output /external/path/nil-exposure-NEW
benchmarks/paired/.venv/bin/python benchmarks/generation/application/fewshot/run.py --report-only --output /external/path/nil-exposure-NEW
```

Reports show failure-inclusive input, output, repair output, output/total TCR,
solves and validity stages per model/condition/task; per-seed costs and paired
whole-task bootstrap are retained. `parse_pass`, `typecheck_pass`, `compile_pass`
are cumulative stage counts, not mutually exclusive categories. `outcomes` are
exclusive terminal attempt categories. Unknown is not treated as failed or passed.
Python has no static typecheck stage. A zero-solve TCR is null, not zero.
Raw exact requests/responses/candidates remain outside both repositories.
Mock provider usage is synthetic and must never appear as a model finding.
Four tasks, three seeds, two small quantized models and one exposure rule do not
establish broad model efficiency or prove that fine-tuning will succeed.
