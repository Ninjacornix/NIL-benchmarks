# Expr-v5 local modules: unified loader, measured cost

General modules now use the existing source-plugin loader. Allocation, host
effects, local recursion and transitive imports are supported without an opaque
runtime boundary. Imported exports become ordinary typed HIR calls. Existing
borrow-only plugins remain restricted. **No intrinsic growth: 32 → 32.**

This is a capability result, not a density win. The two small real split programs
cost **33–39 additional tokens including the manifest**, across four tokenizers.
Single-file sources are unchanged; 69 before/after LLVM modules are byte-identical.
No model inference occurred. The prior generation result remains unfavourable.

## Preregistration and semantics

Main commit `b1946a6` accepted [ADR 032](../../../docs/adr/032.md) before compiler
commit `65c972f`; benchmark commit `8b3e0e2` contains the naming measurement first.
The manifest grammar, entry point, visibility, cycle policy, lifted contracts,
quota/lifetime rationale and ADR 026 classification were settled before code.

`nil-module 1` uses numeric `id`, relative `source`, `export OP LOCAL_LABEL`, and
optional relative `import MANIFEST`. `!plugin(ID,OP,args...)` is the existing
export-reference spelling. Imports are direct visibility edges; transitive
exports are not re-exported implicitly. Shared canonical paths load once.
Root function 0 remains the default entry, and imported labels are private.
Import cycles are rejected, including cross-module mutual recursion; local self/
mutual recursion is allowed. All records still come from the root registry.

Flattening into ordinary calls makes the existing whole-program borrowing,
liveness, reuse, root tracking and quota implementation apply unchanged. No
annotation grants purity. Allocating/effectful imports retain conservative roots;
nonallocating scalar/sequence-returning calls can retain the existing proofs.
A native test proves the borrowed scan has no root frame **before LLVM inlining**,
while an allocating counterexample retains one. No arena, runtime or proof code
was changed. Module calls use ordinary caller fuel/depth, whereas existing borrow
plugins keep atomic caller accounting. The 64 MiB limit is unchanged.

## Naming measured on the unchanged corpus

`benchmarks/module-study/naming.py` counts hypothetical qualification of every
local call in the 66 original source files; it is not a verified rewrite.
Whole-source token differences, with no special tokens:

| Cut | Programs / calls | Gemma | Qwen | cl100k | o200k |
|---|---:|---:|---:|---:|---:|
| Original | 24 / 30 | +122 | +151 | +151 | +150 |
| External | 42 / 298 | +1296 | +1515 | +1483 | +1497 |
| Combined | 66 / 328 | +1418 | +1666 | +1634 | +1647 |

Average contextual overhead is 4.32–5.08 tokens per call, and qualifying all calls
would add 11.2–17.3% combined. Therefore only imported references are qualified.
Local positional calls and all single-file tokens remain unchanged. An audit found
no quoted call-like strings mistakenly included by the measurement regex.
Pinned Gemma/Qwen GGUF vocabularies were loaded with `vocab_only=True`, not for
inference; llama-cpp-python 0.3.16 and tiktoken supply the four real tokenizers.
[Per-source counts and vocabulary identities](../../module-study/naming.json).

## Two real programs and sharing cost

Alternate `count_newlines` and `sum_integers` entry files share `reports.nil`.
The library exports both algorithms and keeps its common formatter private.
All original sources, baselines, tasks, oracles and goldens remain unchanged.
The existing harness gained an optional manifest list feeding both evaluator
and native builds; the default path remains unchanged.

```text
modules/verify.py:
count_newlines: PASS reference 5, native O0/O2 10
sum_integers:   PASS reference 5, native O0/O2 10
MODULE_TOTALS: reference_checks=10 native_checks=20 all_passed=true
```

These 30 additional checks reuse each frozen task's inputs and unchanged golden.
The documented examples also ran: CLI outputs 2 and 3; files contain `2\n` and
`42\n`. They are alternate solutions, not new tasks or inflated adaptation counts.

Each file is tokenized separately; shared library source is charged once across
both entry files. The residual includes factoring the formatter into a function.
A negative residual is a saving; no saving is hidden behind free manifest tokens.

| Tokenizer | Original source | Split source bundle | Reference spelling | Sharing/refactor delta | Manifest | Complete delta |
|---|---:|---:|---:|---:|---:|---:|
| Gemma | 125 | 137 | +8 | +4 | 27 | +39 |
| Qwen | 97 | 105 | +10 | -2 | 25 | +33 |
| cl100k | 96 | 104 | +10 | -2 | 25 | +33 |
| o200k | 94 | 104 | +10 | 0 | 25 | +35 |

Small sharing does not amortize export/manifest cost. Charging the entire library
separately to each entry is larger still: 137/143 Gemma, 108/114 Qwen and 107/113
cl100k/o200k for newline count/integer sum. Unused imported functions are validated
and emitted; there is no frontend dead stripping in this prototype.
[Exact split counts](v5-modules-split-tokens.json),
[verification](v5-modules-split-verification.json).

## Final validation and fuzz coverage

Final code is committed as `65c972f`, `7f4c58a`, `1d25537`; optional corpus integration
as benchmark `d2ea3fb`, pinned by main `f6ef1f0`. All commands exited zero:

| Command | Actual result |
|---|---|
| `./scripts/ci.sh` | 385 tests, 0 failures, 0 warnings |
| `./scripts/ci.sh release` | 385 tests, 0 failures, 0 warnings |
| `./scripts/sanitize.sh` | 150 tests across all seven suites, no ASan/UBSan finding |
| `verify.py --output /tmp/nil-modules/corpus-all.json` | 2775 checks, 66 NIL programs, 13 unsupported |
| `verify.py --group original --output /tmp/nil-modules/corpus-original.json` | original 610 checks separately passed |
| `modules/verify.py --output /tmp/nil-modules/split-verification.json` | 30 additional reference/native checks |

Corpus totals: reference 553, native O0/O2 1106, Python 558, C++ 558. Original
cohort: reference 120, native 240, Python 125, C++ 125. A frozen-file comparison
confirms 264 task/oracle/golden/source files unchanged. CI adds 17 Rust tests to
the starting 368: compiler 7, CLI 1, native 8, generator 1.

```sh
./scripts/fuzz-v5.sh --seed 1729 --cases 356 --out /tmp/nil-modules/fuzz-1729
./scripts/fuzz-v5.sh --seed 8675309 --cases 356 --out /tmp/nil-modules/fuzz-8675309
./scripts/fuzz-v5.sh --seed 5130572 --cases 356 --out /tmp/nil-modules/fuzz-5130572
```

Each run compared 356 generated programs at O0/O2: **1068 programs / 2136 native
builds, zero divergences**. Each seed hit the same observed runtime-code counts:

| Outcome | Per seed | All three |
|---|---:|---:|
| OK | 258 | 774 |
| E009 | 2 | 6 |
| E012 | 19 | 57 |
| E013 | 27 | 81 |
| E014 | 6 | 18 |
| E015 | 5 | 15 |
| E016 | 12 | 36 |
| E017 | 4 | 12 |
| E018 | 6 | 18 |
| E019 | 3 | 9 |
| E020 | 6 | 18 |
| E021 | 5 | 15 |
| E022 | 3 | 9 |
| E024, compile-only module mutations | 9 | 27 |

E024 cases compile twice to compare diagnostics; they are not counted as native
programs. Each seed's `call_families` reports 24 executable module families plus
nine graph failures: missing/duplicate exports/imports/IDs, cycle, unknown version,
noncanonical ID and missing function. Executable families cover local-name
collisions, transitive imports, allocation, returned aliases, loop state, records/
record buffers, host effects, file pipelines, laziness, recursive held sequences,
borrowed plugins and quota boundaries. Shapes are fixed templates with randomized
sequence arguments/file bytes, not exhaustive proofs of every possible program.
The existing broad adversarial families continue to run. No divergence or
sanitizer defect was found.

During implementation, review caught a root-local call potentially resolving to
an imported private relocated label; local calls are now checked before linkage,
with a regression test. One development limit test accidentally exercised exactly
the legal aggregate limit; it was corrected to exceed it by one byte. The final
full gates above run the corrected test. No runtime correctness finding was hidden.
[Command summaries, log hashes, all code/family counts](v5-modules-validation.json).

## Single-file performance controls

Measured only after CI, sanitizers, corpus and fuzzing finished. Existing benchmark
entry points, 25 samples after one warmup, rotating NIL/C++/Python order, whole
processes on Apple M2/macOS, Clang 21, Python 3.12.11. Compilation and correctness
verification excluded, warm files, no fsync or CPU isolation. Every sample checks
outputs; append contents, arbitrary-byte scans and double-transform round trips
also pass. No compiler/runtime optimization was made this round.

| Workload | Historical NIL ms | Current NIL median [min,max] ms | C++ ms | Python ms |
|---|---:|---:|---:|---:|
| Append 1 MiB | 22.850667 | 22.899 [22.073,23.411] | 4.970 | 44.150 |
| Newline scan 16 MiB | 7.598667 | 7.728 [7.365,8.158] | 10.274 | 24.311 |
| Transform 16 MiB | 36.669625 | 36.819 [35.635,42.178] | 14.603 | 810.374 |

Historical values are the preceding debt report, not claimed as paired runs this
session. Differences are +0.2%, +1.7%, +0.4%, inside current sample ranges, with
**byte-identical LLVM IR and unchanged runtime/backend sources**. There is no
observed architectural regression. Finite noisy whole-process timing alone does
not prove a universal speed guarantee. All 66 existing corpus sources plus these
three controls emit byte-identical before/after LLVM IR.

```sh
./scripts/bench.sh runtime --full --workloads --workload append --workload newlines --repeats 25 --output /tmp/nil-modules/performance-workloads
./scripts/bench.sh runtime --full --application --repeats 25 --output /tmp/nil-modules/performance-transform
```

[Raw samples and methodology](v5-modules-workloads.json),
[transform samples/stages](v5-modules-transform.json),
[69 exact IR hashes](v5-modules-single-file-ir.json).

## Remaining blockers and limits

**`multi_file_fixture` does not become supported.** It labels `ex_grep`'s runtime
upstream text files/flags; the frozen corpus only provisions `input.bin`, and no
baseline adapter exists either. Source modules cannot supply those missing runtime
fixtures. No oracle was altered or packed emulation substituted. There remain
13 unsupported tasks (12 external), named explicitly:

| Task | Remaining catalogue blocker |
|---|---|
| env_lookup | environment |
| ex_accumulate | higher-order functions |
| ex_alphametics | verified search/JSON adapter (historical maps_records label) |
| ex_dot_dsl | nested graph-attribute representation/adapter (maps_records) |
| ex_anagram | Unicode |
| ex_bob | Unicode |
| ex_bank_account | concurrency |
| ex_camicia | game/deck-state adapter (nested_collections) |
| ex_diffie_hellman | entropy |
| ex_forth | verified dictionary/interpreter adapter (dynamic_dictionary) |
| ex_gigasecond | calendar |
| ex_grep | runtime multi-file fixtures/adapter |
| ex_hangman | reactive callbacks |

These are capability **and adapter** gaps, not thirteen theoretical impossibility
claims. Modules themselves are deliberately restricted: acyclic imports, root-owned
nominal registry, local source only, bounded graph, local source offsets rather than
file-qualified diagnostics. Allocating/effectful calls retain conservative machinery.
No native loading/sandbox claim, packages, remote fetching or stable ABI is added.
Existing alias-copy/keyed-repack/allocating-region limits and the commutative bulk
matcher limitation remain unchanged. No follow-up capability starts automatically.

All changes are logical local Conventional Commits. Nothing was pushed, including
the benchmark submodule. Remote tracking refs remain the starting values recorded
in the validation receipt. See [main validation guide](../../../docs/validation/V5_MODULES.md)
for exact rerun commands and archive details.
