# Standing generation eval — preregistration

ADR 037 governs this frozen matrix. See experiment.json and split.json. This is a
tracking metric, not a compiler or release gate. No model result exists yet.

The Claude arm uses claude-sonnet-5-5, high effort, USD 50 total notional cap,
24 held-out tasks, two replicates and three total attempts. DEV is disjoint;
only the first committed dev task is used for pipeline confirmation. Four existing
few-shot examples stay fixed. JSON-placeholder tasks without an explicit contract
are listed as exclusions; the cohort does not establish general task coverage.

The transport must prove tool/MCP/hook/session/repository isolation before live
inference. Backend usage is authoritative; tiktoken screens are separate. Raw
requests/responses and generated candidates remain outside version control.

## Run

Use the existing paired Python environment (Python 3.12, tiktoken 0.12.0); no new
dependencies. From the parent checkout:

```sh
./scripts/gen-eval.sh --mock --phase dev --output /tmp/nil-gen/mock-dev
./scripts/gen-eval.sh --mock --phase held-out --output /tmp/nil-gen/mock-matrix
./scripts/gen-eval.sh --phase dev --output /tmp/nil-gen/dev
# Only after a successful real DEV run (includes two prefix accounting probes):
benchmarks/paired/.venv/bin/python benchmarks/generation/standing/forecast.py --dev /tmp/nil-gen/dev
# Review/commit generation/standing/cost-forecast.json in the benchmarks branch.
./scripts/gen-eval.sh --phase held-out --prior /tmp/nil-gen/dev --output /tmp/nil-gen/held-out
```

Each invocation writes raw requests/responses/candidates outside Git and publishes
summary JSON/Markdown under `reports/<UTC date>/`. Mock files are prominently
labelled; their usage/solutions are synthetic, never evidence of model ability.
The fixed existing reference answers are read only by mock/leakage auditing.

The standing adapter reuses application/run.py's source extraction and repair
conversation, application/oracle.py's reference/native/Python verification and
sandbox, and corpus task loaders/expected outputs. Its driver is separate because
the frozen original runner hard-codes four tasks, two Ollama profiles and a seed
matrix; modifying it would compromise replication of historical studies. The
original Ollama command and experiment remain unchanged.

The unit suite covers repaired attempts, missing usage, infrastructure, tools,
MCP/hooks, pin mismatch, split leakage and spend reservation. Native compilation
rates are N/A for Python. Source feature labels are descriptive associations, not
causal attribution. TCR is undefined at zero solves; missing usage is unknown.
Task-cluster paired bootstrap retains both replicates and every failed repair;
undefined resamples are counted, not assigned zero. Prefix-amortized input is a
scenario based on two measured backend counts, not provider billing or tiktoken.

## Round 15 environment block

CLI 2.1.291 is installed with Claude.ai subscription auth; API-key environment is
absent. The network-disabled initialization probe failed before any model request:
`EPERM: operation not permitted, open '/tmp/claude-501'`. Empty tools/MCP/hook
isolation could not be proved. No capable-model result or post-DEV cost forecast
exists. Do not remove the sandbox to make the command run: supply a CLI/auth
configuration that initializes inside the documented isolation, or propose an
explicitly audited fix to the global temporary-state dependency. Model availability
itself was not tested; no alternate model or Ollama inference was substituted.
