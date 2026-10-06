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
