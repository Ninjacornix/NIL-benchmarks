# Standing generation eval: closed as partial (2026-10-06)

**Preliminary, incomplete evidence. No held-out run completed.** The campaign was closed by
maintainer decision: models are not trained on NIL, so spec-only generation cost is not a
project requirement. These numbers measure an *untrained* frontier model reading the spec
in context; they say little about a model trained on NIL.

Model `claude-sonnet-5-5`, effort high, Claude Code 2.1.291 via Claude Pro OAuth token
(notional cost), OS-sandboxed, no tools/MCP/hooks, fresh session per request.

## Runs

| Run | Attempts | Notional USD | Stopped by |
|---|---:|---:|---|
| DEV 1 | 0 | 0.00 | invalid token file (browser auth code saved instead of token) |
| DEV 2 | 3 | 0.26 | complete; superseded by cap amendment (plan hash) |
| DEV 3 | 3 | 0.05 | complete; all three arms correct on attempt 1 |
| Held-out 1 | 10 | 0.89 | per-attempt output overrun halted campaign (harness bug) |
| Held-out 2 | 30 | 2.01 | safety refusal classified as infrastructure (harness bug) |
| Held-out 3 | 38 | 2.32 | CLI output-limit error on a 656-token residual attempt |
| **Total** | | **5.53** | |

Held-out 3 was preregistered as the analysis run (ADR 037); it did not complete.

## Held-out 3, partial (descriptive only)

| | Python | NIL spec-only | NIL spec + examples |
|---|---:|---:|---:|
| Trials | 10 | 11 | 11 |
| Solved | 10 | 10 | 10 |
| Solved first attempt | 9 | 8 | 8 |
| Median output tokens / trial | 384 | 2,372 | 1,173 |
| Total output tokens | 5,697 | 45,360 | 41,106 |
| Median input tokens / request | 671 | 19,213 | 19,882 |
| Output tokens per correct solution | 570 | 4,536 | n/a (unknown usage on blocked attempt) |
| Total tokens per correct solution | 1,344 | 33,397 | n/a |
| Refusals | 0 | 1 | 0 |

Held-out 2 (9 trials per arm, superseded) shows the same pattern: Python 9/9, NIL spec 8/9,
NIL examples 9/9.

## Reading

1. **Learnable from the spec.** An untrained frontier model solved 10/11 per NIL arm
   from the published spec, against 0/24 for 4B/7B local models earlier.
2. **Not token-efficient for an untrained model.** NIL needs the ~19k-token spec in
   context and 3-6x more reasoning output than Python. Both are unfamiliarity costs that a
   trained model would largely not pay; final program size is the training-invariant part
   and is measured separately by the density studies.
3. **Hard tasks dominate cost.** `ex_dominoes` in NIL used 15-18k reasoning tokens per
   attempt and failed in both NIL arms, including one `reasoning_extraction` refusal on a
   CLI auto-continuation.

## Known design limits (if the eval is ever resumed)

- An 8,192-token per-attempt cap is below Sonnet's reasoning on hard NIL tasks; the CLI
  then auto-continues past `max_tokens`, which triggered one safety refusal.
- A residual trial budget can produce degenerate attempts (656 tokens). Skip attempts
  below a minimum budget, or end the trial.
- The CLI's own output-limit error is not yet classified as a failed attempt.
- `generation/standing` tests publish mock reports into `reports/<date>/`; they should
  write only to temporary directories.
