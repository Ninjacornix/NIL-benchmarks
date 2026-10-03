# Expr-v5 token attribution and preregistered disposition

**Decision before implementation: keep the surface unchanged this round.** The
measured surplus is not explained by unchanged loop operands or repeated type
signatures. The largest costs belong to explicit scalar algorithms. No proposed
surface fix has a justified saving large enough to address that cause. This is an
analysis outcome, not a claim that immutable values inevitably cost more tokens.

Source density remains separate from total model tokens including repairs. The
prior generation study remains unfavourable: NIL 0/24, Python 11/24. No inference
was performed in this analysis.

## Frozen population and method

Use all 32 currently supported external pairs; retain all 18 external unsupported
tasks. Baseline: `V5_KEYED_DENSITY.json`, NIL 5686 versus Python 5036 cl100k tokens,
+650 (+12.91%). Original 24 and every source, task, oracle and golden remain frozen.
The same four pinned vocabularies used by density.py are used here, vocabulary-only.

`attribution.py` assigns source bytes using lexical tokens, Python AST/tokenize,
and balanced NIL loops. Headers include the entire declaration through `=`/`:`;
they include function names/parameter names on Python and typed/numeric arity on
NIL. Calls to declared Python functions and positional NIL functions are user
calls; Python builtins/methods and NIL `!` names are intrinsic names. This avoids
manufacturing a NIL naming surplus by classifying every Python call as an identifier.

Loop delimiters cover NIL `@(`, `;`, `)` and Python for/while keywords. Index/bound
covers simple scalar NIL comparisons and +/-1 step of a condition-referenced state;
Python range target/iterable or while comparison. Complex predicates remain lexical.
Bare step identifiers exactly matching their state position are unchanged-state.
Everything else is operators, separators, literals, names, keywords or whitespace.
Initializers and other step computations remain lexical, not assumed removable.
These are source roles, not counts of equivalent machine operations.

Token pieces must reconstruct every ASCII source byte; Gemma's one synthetic
leading space is removed from the first piece, not from its token count. No special
tokens are added. Each token contributes exactly one to the ledger. Primary ranking
uses rational byte-overlap shares, ignoring whitespace in mixed tokens. This avoids
crediting all of BPE token `,a` to the comma. Whole-token maximum-overlap assignment,
first-byte tie break, is retained as sensitivity analysis. Exact rational sums, all
four tables and per-task counts are in `V5_ATTRIBUTION.json`. Printed rounding may
leave a last-decimal discrepancy; exact fractions sum to each measured gap.

Repeated expressions are an orthogonal property of already classified bytes, not
another additive category: counting them again would double-count. The overseer's
243/7268 textual-repeat ceiling is 3.3% over the combined set, not a measured saving
on these 32 tasks. Sharing also depends on scope, laziness and trap/effect ordering.
No binding saving is claimed from that number.

## Ranked cl100k attribution

| Category | NIL | Python | NIL − Python |
|---|---:|---:|---:|
| numeric_literal | 592.000 | 198.000 | +394.000 |
| operator | 701.367 | 375.629 | +325.738 |
| separator | 1193.250 | 872.737 | +320.513 |
| signature | 713.000 | 395.000 | +318.000 |
| loop_delimiters | 202.333 | 27.000 | +175.333 |
| loop_index_bound | 242.500 | 87.500 | +155.000 |
| call_identifier | 158.000 | 43.800 | +114.200 |
| boolean_literal | 45.767 | 2.800 | +42.967 |
| unchanged_state | 40.000 | 0.000 | +40.000 |
| comment | 0.000 | 0.000 | +0.000 |
| text_literal | 503.617 | 536.100 | -32.483 |
| intrinsic_name | 431.667 | 468.566 | -36.900 |
| identifier | 832.500 | 973.235 | -140.735 |
| keyword | 0.000 | 387.800 | -387.800 |
| whitespace | 30.000 | 667.833 | -637.833 |
| **Exact total** | **5686** | **5036** | **+650** |

The numeric surplus is real, not whitespace or arbitrary separator ownership:
NIL uses 592 numeric tokens, Python 198. Among classified numeric occurrences,
NIL has 190 zeros and 169 ones versus Python's 42 and 53; numbers in signatures
and classified loop bounds/steps are excluded. Values/index arithmetic, nested
scalar conditions, literal tables and explicit traversal account for the cost;
most such constants are already one token, so a shorter spelling cannot help.
Text literals actually favour NIL (−32.483 fractional tokens). Intrinsic names
also favour NIL (−36.900); shortening names is not justified by this ranking.

Grade school (+249), Connect (+151), and ETL (+123) contribute 523 of the net650
surplus (80.5%); all tasks remain in the measurement. Reading both sources shows:

- Grade school: Python sorts tuples and compares byte names directly; NIL scans an
  offset buffer repeatedly, finds fields and factors a lexicographic comparison
  into positional helpers. Maps removed duplicate tracking, not the sort/comparator.
- Connect: Python has paired coordinates, a stack, a set and a neighbour table;
  NIL uses flattened indices, union-find and calls through five-state helpers.
- ETL: Python uses JSON decoding/encoding; NIL explicitly locates quotes, parses
  fields and formats deterministic output. This is a frozen finite transport
  oracle, not a claim of implementing arbitrary JSON in NIL.

This evidence attributes costs to the current implementations and missing
algorithm/data abstraction. It does **not** prove minimum possible program size,
or that mutation is required. A different correct algorithm may improve density;
it must be separately authored and oracle-verified before being called a saving.

## Ranked remediation and predictions, BEFORE implementation

| Rank | Candidate | Gemma saving | Qwen | cl100k | o200k | Disposition |
|---|---|---:|---:|---:|---:|---|
| 1 | Address scalar algorithm expansion (comparison/sorting, coordinate traversal, parsing/formatting) | Not justified | Not justified | Not justified | Not justified | Separate semantic-design decision; no invented forecast |
| 2 | Reference an earlier identical complete signature using hypothetical `^a=` | 78 | 32 | 32 | 32 | Do not implement: only 4.9% of cl100k gap |
| 3 | Empty loop step means unchanged positional state | 131 | 9 | 9 | 9 | Do not implement: only 1.4% of cl100k gap |
| 4 | Local bindings for textual duplicates | No defensible executable forecast | — | — | — | Scope/effects required; overseer ceiling insufficient |
| 5 | Intrinsic/identifier shortening | Not pursued | — | — | — | Names already favour NIL; no justified target |

The two surface forecasts are reproducible whole-source retokenizations, not
assigned-category totals. Signature candidate references the earliest declaration
with **identical full header**, including result; only longer headers change.
Empty-step candidate deletes only bare state operands, preserving comma positions.
Neither candidate is valid under the current compiler: these are lexical forecasts,
**not verified programs**, and do not enter the corpus or adaptation export. There
are 77 unchanged operands in 56 loops; BPE merges most with their commas, explaining
why deleting 77 identifiers saves only nine tokens. Connect's signature proposal
saves 18 cl100k tokens, not the entire observed signature cost.

Per-task forecasts and counterfactual source are frozen in `V5_SURFACE_FORECASTS.json`.
No task was selected/dropped for a forecast. Combined proposals are NOT assumed
additive: tokenizer merges can interact. Each standalone candidate remains far short
of650; adding grammar/model-training obligations for these small savings is not
justified when the largest algorithm costs remain untouched.

**Implementation gate:** no change this round. Actual implemented saving: **0** for
all tokenizers. Forecast-versus-executable savings for these unimplemented spellings
is **not applicable**, not a successful validation of their semantics. Reverify and
retokenize the unchanged corpus, and run all requested correctness/performance
controls before final reporting. No existing program's meaning changes.

Recommend a separate decision on reusable comparison/sorting and typed field/tuple
iteration, evaluated on these same immutable tasks. Do not infer from this ledger
that explicit-state semantics must be abandoned. There is no demonstrated
semantic-preserving surface remedy for the largest cause within this round.

## Reproduce

From NIL root (initialized submodule and its pinned Python environment):

```sh
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/attribution.py \
  --density benchmarks/reports/2026-10-03/V5_KEYED_DENSITY.json \
  --output /tmp/nil-attribution/analysis
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/remediation.py \
  --output /tmp/nil-attribution/analysis
benchmarks/paired/.venv/bin/python -m unittest discover \
  -s benchmarks/corpora/application-v5/tests
```

The full raw ledger includes every token's byte offset, piece hex, category and
byte votes; keep it outside the checkout to avoid committing a 10MB regenerated
trace. The committed summary preserves per-task/per-category exact fractions and
pinned versions. The unit suite exercises boundary merges, reconstruction failure,
Gemma prefix, nested positional states, quoted delimiters, call categories and both
counterfactual transforms. No Rust dependency or inference context is created.
