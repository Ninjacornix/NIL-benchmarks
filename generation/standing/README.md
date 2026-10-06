# Standing generation eval — Claude Pro transport

ADR 037 and its Round 15b addendum govern the frozen experiment. No capable-model
result exists. The earlier EPERM was a transport defect: Claude's own state ignored
TMPDIR. This revision supplies CLAUDE_CODE_TMPDIR in a sibling of the empty cwd.
Real CLI startup/auth/model availability must still be checked by the maintainer.

The exact model is `claude-sonnet-5-5`, effort high. Three unchanged arms:
Python, NIL spec-only, NIL spec plus four fixed independent examples. Twenty-four
held-out tasks, two replicates, three completed attempts per trial. Each request
allows 8,192 output tokens (including thinking), each trial 16,384. All arms share
these corrected limits. No generation had run before the cap amendment.

## Authentication and isolation

Provision a long-lived subscription token privately in
`~/.config/nil/claude-oauth-token`, mode 0600, owned by the current user. An alternate
path can be selected with `NIL_CLAUDE_OAUTH_TOKEN_FILE`. Never put the token on argv,
in a prompt, shell history or Git. The transport reads this file outside the OS
sandbox and forwards only `CLAUDE_CODE_OAUTH_TOKEN` into the CLI environment.
No API-key fallback, `--bare`, keychain access or real-home config exception.
Mock campaigns do not read token files or execute Claude.

Each CLI request gets a fresh private root containing sibling `cwd/`, `state/`
and `home/`. cwd remains empty. Strict empty tools/MCP, hooks disabled,
safe/restricted mode, no session persistence, replacement system prompt and denied
repository/keychain reads remain required. Every stream block is checked, including
error responses. Preflight denies networking entirely; passing it proves isolated
initialization, **not** a valid token, model access or a successful generation.
Actual CLI/profile enforcement requires the maintainer's local preflight; unit
mocks cannot prove kernel enforcement.

## Exact execution sequence (parent checkout)

Use the existing paired Python environment; no new dependency. Choose fresh output
paths outside Git. Do not change either repository revision during a campaign.

```sh
./scripts/gen-eval.sh --preflight --output /tmp/nil-gen-pro/preflight
./scripts/gen-eval.sh --phase dev --output /tmp/nil-gen-pro/dev
benchmarks/paired/.venv/bin/python benchmarks/generation/standing/forecast.py --dev /tmp/nil-gen-pro/dev
# Commit the observed forecast locally, BEFORE any held-out request:
git -C benchmarks add generation/standing/cost-forecast.json
git -C benchmarks commit -m 'docs(eval): forecast notional held-out cost'
git add benchmarks
git commit -m 'docs(eval): pin observed generation forecast'
./scripts/gen-eval.sh --phase held-out --prior /tmp/nil-gen-pro/dev --output /tmp/nil-gen-pro/held-out
# If DEV or held-out pauses at a subscription usage window, wait externally:
./scripts/gen-eval.sh --resume /tmp/nil-gen-pro/dev
./scripts/gen-eval.sh --resume /tmp/nil-gen-pro/held-out
```

Resume DEV before forecasting if DEV paused. Do not execute a resume for a completed
campaign. CLI exit 75 means known-accounting rate pause; exit 2 means another stop;
exit 0 means complete. Rate pauses are outside parse/solve denominators, but any
reported input/output/cost is retained in failure-inclusive totals and reduces the
remaining trial/campaign budget. No automatic retry. Unknown usage/cost, an
unresolved in-flight request, altered checkpoint, changed frozen hashes/revisions
or changed CLI blocks resume. Accounting probes resume too. Completed attempts and
repair history are never replayed. Every completed attempt is atomically checkpointed;
a pre-request checkpoint marks the in-flight invocation. The checkpoint is the
journal of record; attempts.jsonl is a rebuildable projection. SHA256 detects
accidental edits, not adversarial rewriting of a journal and its checksum.

The USD50 cap covers DEV, calibration and held-out combined. CLI USD1 budget plus
cumulative reservations guard each request; cost is **notional subscription usage**,
not an invoice. Soft CLI enforcement can overshoot after an API call: retain and
report that, then stop. Rate-paused invocations also count toward the global 443
invocation bound. The new worst-case output envelope is 2,424,832 tokens, 10.69x
old; a full matrix is not promised within USD50. No dollar usage forecast is invented:
the actual DEV mean/max cost forecast must be committed before held-out.

## Offline checks

```sh
benchmarks/paired/.venv/bin/python -m unittest discover -s benchmarks/generation/standing/tests -v
./scripts/gen-eval.sh --mock --phase dev --output /tmp/nil-gen-pro/mock-dev
./scripts/gen-eval.sh --mock --mock-rate-limit-after 2 --output /tmp/nil-gen-pro/mock-pause
# Previous command intentionally exits 75:
./scripts/gen-eval.sh --resume /tmp/nil-gen-pro/mock-pause
./scripts/gen-eval.sh --mock --phase held-out --output /tmp/nil-gen-pro/mock-matrix
```

Mocks read frozen reference solutions solely as stub responses; their solves,
usage and spend are synthetic, never model evidence. Tests use planted fake tokens
and mocked CLI subprocesses; they never read real subscription credentials. They
cover sibling-state startup, private-file checks, artifact-wide redaction, tools,
rate limits, interrupted requests, deterministic repair resume and accounting resume.

Reports: external output directory plus summary JSON/Markdown under
`reports/<UTC date>/[MOCK_]STANDING_GENERATION_PRO_<phase>.*`. Raw requests,
responses, candidates and private environments stay outside Git. No credentials or
raw transcripts belong in commits. The frozen application/Ollama runners, corpus,
oracles, split, few-shot selection and prompts are unchanged. Input counts are
backend fresh/cache usage; tiktoken source screens stay separate. Undefined TCR
and missing accounting remain unknown. Spec amortization is a measured-prefix
scenario, not actual subscription billing. Paired task bootstrap is retained.

## Budget amendment (2026-10-06, before any live generation)

Maintainer decision: total notional cap **USD 10** (was USD 50), and **one** held-out
replicate (was two): 24 tasks x 3 arms x 1 replicate = 72 trials, at most 216 held-out +
9 DEV + 2 calibration = **227** invocations. Attempts, effort, output caps, split, arms,
prompts and forecasts are unchanged. Earlier USD 50 / two-replicate / 443 figures above
are superseded. With one replicate, run-to-run variance is not measured.
