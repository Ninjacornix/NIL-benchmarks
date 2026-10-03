# Expr-v5 numeric core: capability, determinism and density

Binary64, u64 and u128 unblock four frozen external tasks, increasing verified NIL
programs from 56 to **60** and reducing unsupported tasks from 19 to **15**
(14 external). They do **not** establish a density win over Python: the expanded
external cohort costs **4.2–12.4% more**, combined **1.2–8.4% more**, across four
real tokenizers. NIL uses 47–50% fewer source tokens than C++ externally.

**Source density is not total tokens to correctness.** The generation result remains
unfavourable (NIL 0/24 versus Python 11/24; see
[the generation report](../2026-10-03/V5_GENERATION.md)). No model inference,
training, syntax tuning, oracle/golden changes or existing baseline rewrites occurred.

## Core-versus-extension decision

[ADR 026](../../../docs/adr/026.md) was committed in main `1ab04a2` before any
implementation. Proof participation requires a compiler-visible contract, but is
not sufficient for a permanent core opcode. Fundamental type/value/control/storage
semantics belong in core; algorithms may migrate only to validated visible
lowerings preserving lifetimes, aliases, reuse, effects, quota and trap ordering.
Every existing intrinsic is classified. None migrates; no plugin ABI is frozen.
[ADR 027](../../../docs/adr/027.md) preregisters numeric contracts in the same
commit. No other widths, float collections, records or transcendental functions.

## Frozen-task delivery and limits

- Armstrong Numbers uses u128 for the pinned 108/127-bit inputs. Per-digit powers
  fit u128 for its up-to-39-digit domain; a cumulative wrap is detected, so a
  modular sum never masquerades as mathematical equality.
- Grains uses u64 for square 64's 2^63; invalid-square output remains `error`.
- Darts uses strict squared-radius binary64 comparisons, no sqrt/FMA.
- Complex Numbers implements the upstream-selected **real-part property**, not a
  full complex API or a complex/record type. It validates the real lexeme as f64
  and preserves the JSON number spelling. Numeric adapters cover the pinned
  minified JSON contracts, not arbitrary JSON formatting or schemas.

Support overlays and new solutions/baselines fill absent paths. Existing 24
programs, all frozen tasks/oracles/goldens and existing baseline sources are
unchanged. Lock tests verify their hashes. No task moved to supported until
reference evaluator **and native O0/O2**, Python and C++ passed the same oracle.

## Executable verification

```text
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/verify.py --output /tmp/nil-numeric/verification2.json
TOTALS {"tasks": 75, "nil_programs": 60, "unsupported": 15, "reference_checks": 515, "native_checks": 1030, "python_checks": 520, "cpp_checks": 520}
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/verify.py --group original --output /tmp/nil-numeric/original-verification.json
TOTALS {"tasks": 25, "nil_programs": 24, "unsupported": 1, "reference_checks": 120, "native_checks": 240, "python_checks": 125, "cpp_checks": 125}
```

All **2,585 checks** pass (515 reference, 1,030 native, 520 Python, 520 C++).
The **original 610** separately pass (120/240/125/125). The extra five checks are
for the original environment task’s baseline-only support, not an extra NIL example.
Verification stores every verdict and source fingerprint in
[V5_NUMERIC_VERIFICATION.json](V5_NUMERIC_VERIFICATION.json);
[V5_NUMERIC_ORIGINAL.json](V5_NUMERIC_ORIGINAL.json) stores the original cut.

## Four-tokenizer density

Same frozen tokenizer assets and tokenization protocol as the preceding study:
Gemma3 4B / Qwen2.5 7B vocabularies through llama-cpp-python 0.3.16,
tiktoken 0.12.0 cl100k/o200k, no special tokens and no inference context.
Official Qwen tokenizer 0.22.1 cross-check: 182 comparisons, zero mismatches.
[V5_NUMERIC_DENSITY.json](V5_NUMERIC_DENSITY.json) records pinned model hashes,
versions, every source hash, bytes/characters, per-task counts and all losses/ties.
[V5_NUMERIC_TOKENS.csv](V5_NUMERIC_TOKENS.csv) contains the complete long table.

```text
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/density.py --verification /tmp/nil-numeric/verification2.json --output /tmp/nil-numeric/density
paired task count: 60; adaptation JSONL export count: 60
```

| Cut | Tokenizer | NIL | Python | C++ | NIL/Python gap | NIL/C++ reduction |
|---|---|---:|---:|---:|---:|---:|
| original (24) | gemma3_4b | 2144 | 2227 | 5454 | -3.73% | 60.69% |
| original (24) | qwen2.5_7b_instruct | 1634 | 1728 | 4235 | -5.44% | 61.42% |
| original (24) | cl100k_base | 1582 | 1705 | 4217 | -7.21% | 62.49% |
| original (24) | o200k_base | 1571 | 1712 | 4238 | -8.24% | 62.93% |
| new_external (36) | gemma3_4b | 7541 | 6711 | 14256 | +12.37% | 47.10% |
| new_external (36) | qwen2.5_7b_instruct | 5826 | 5468 | 11381 | +6.55% | 48.81% |
| new_external (36) | cl100k_base | 5647 | 5387 | 11335 | +4.83% | 50.18% |
| new_external (36) | o200k_base | 5640 | 5411 | 11378 | +4.23% | 50.43% |
| combined (60) | gemma3_4b | 9685 | 8938 | 19710 | +8.36% | 50.86% |
| combined (60) | qwen2.5_7b_instruct | 7460 | 7196 | 15616 | +3.67% | 52.23% |
| combined (60) | cl100k_base | 7229 | 7092 | 15552 | +1.93% | 53.52% |
| combined (60) | o200k_base | 7211 | 7123 | 15616 | +1.24% | 53.82% |

| Cut | NIL bytes/chars | Python bytes/chars | C++ bytes/chars |
|---|---:|---:|---:|
| original | 3310/3310 | 6746/6746 | 17283/17283 |
| new_external | 11407/11407 | 20835/20835 | 45628/45628 |
| combined | 14717/14717 | 27581/27581 | 62911/62911 |

### Before/after without cohort confusion

The same 56 pre-existing solutions/counts have **zero movement**; this is a
four-task expansion, not compression of previously solved programs. The original
24 remain exactly unchanged. The external paired cohort grows 32→36; combined
56→60. Compare with [the preceding report](../2026-10-03/V5_ALGORITHMS.md):

| Tokenizer | External Python gap, before→after | Combined Python gap, before→after |
|---|---:|---:|
| gemma3_4b | +12.31% → +12.37% | +8.10% → +8.36% |
| qwen2.5_7b_instruct | +6.16% → +6.55% | +3.23% → +3.67% |
| cl100k_base | +5.00% → +4.83% | +1.91% → +1.93% |
| o200k_base | +4.35% → +4.23% | +1.17% → +1.24% |

Gemma/Qwen widen slightly; cl100k/o200k narrow externally. Combined cl100k
also widens slightly, o200k narrows slightly. None establishes an advantage.

| Newly supported task | Gemma NIL/Py/C++ | Qwen NIL/Py/C++ | cl100k NIL/Py/C++ | o200k NIL/Py/C++ |
|---|---:|---:|---:|---:|
| ex_armstrong_numbers | 183/116/337 | 140/90/273 | 120/90/268 | 121/91/269 |
| ex_complex_numbers | 82/87/227 | 60/64/174 | 57/64/174 | 57/64/175 |
| ex_darts | 145/137/306 | 122/115/241 | 110/111/237 | 110/111/237 |
| ex_grains | 98/109/258 | 77/87/200 | 72/86/198 | 73/86/199 |

Armstrong loses to Python on every tokenizer. Complex real-part and Grains win on
all four. Darts loses on Gemma/Qwen, wins by just one token on cl100k/o200k.
All four beat C++, including its headers/I/O. Do not hide these differing outcomes.
The 60 exported examples remain adaptation **seeds**, not a training-scale corpus;
hundreds to thousands of diverse, independently verified programs and held-out
families would be needed to explore adaptation, with no promised minimum or gain.
The corpus is a nonrandom, partial-API Exercism sample with locally written
references and finite upstream fixtures; no population inference is justified.


## Numeric semantics and strict-FP evidence

[Specification](../../../docs/language/EXPR_V5.md#scalar-numeric-types-adrs-026027):
identical-type arithmetic only, unsigned modular arithmetic, explicit checked
conversions E021, explicit integer-only low-bit truncation, numeric parsing E022.
Binary64 division by zero produces infinity/NaN; integer division still traps E009.
All NaNs canonicalize to `0x7ff8000000000000`; signed zeros compare equal but bits,
format and division distinguish them. Byte-keyed maps remain unchanged: floats are
not map keys; explicitly formatted signed-zero strings are distinct byte keys.

Primitive arithmetic rounds each operation to nearest/ties-even with gradual
underflow. No FMA, fast math, reassociation or approximate reciprocal. All three
Clang stages explicitly use these flags at O0 and O2 (the latter also uses LTO):

```text
-fno-fast-math -fno-associative-math -fno-reciprocal-math -ffp-contract=off
```

Actual logged O2 IR invocation (temporary paths are intentionally ephemeral):
```text
-flto -fno-fast-math -fno-associative-math -fno-reciprocal-math -ffp-contract=off -O2 -Wno-override-module -x ir -c /var/folders/82/vv914qlx6gq32dyd34vnfg4w0000gn/T/.nil-llvm-22974-1/module.ll -o /var/folders/82/vv914qlx6gq32dyd34vnfg4w0000gn/T/.nil-llvm-22974-1/module.o
```
The same log includes runtime-C and link invocations. `contraction_is_disabled_for_multiply_then_add`
checks `(1+2^-27)*(1-2^-27)-1` returns +zero bits at O0/O2; a fused `mul_add` returns
nonzero (−2^-54). Emitted IR contains `fmul`/`fadd`, no fast/contract/reassoc/arcp
flags and no FMA intrinsic. This witness would fail if an FMA were formed; flags
are checked through the recorded invocations, not inferred from timing.

Float text uses a fixed scientific 17-significant-digit contract, not shortest:
reference Rust formatting and C `snprintf` normalize exponents identically.
Decimal parsing uses the complete specified ASCII grammar, Rust conversion versus
C `strtod`, both under nearest/ties-even; malformed/noncanonical text fails E022.
Overflow/underflow yield IEEE infinity/zero/subnormals. Every resulting NaN is
canonical. No approximate comparison and no transcendental operations ship.

### Bit-exact tests and limitations

- Explicit NaN/signaling-payload normalization, ±zero, ±infinity, subnormal,
  min-normal and largest positive/negative finite patterns.
- 269 special/random patterns, each formatted and parse-round-tripped at O0/O2:
  1,076 native executions with exact text/bit assertions.
- 128 random operand pairs across all four float arithmetic operations at both
  levels: 1,024 native bit-pattern comparisons.
- Exact halfway decimal cases, extreme exponents, nonfinite/range conversion
  rejection, valid conversion boundaries, checked versus truncating integers,
  unsigned ordering/wrap/division, typed calls and loop state, lazy trap/effect
  avoidance and live-capacity admission for numeric formatting.
- Numeric source mutations exercise malformed spellings/widths/conversions;
  HIR tests reject noncanonical NaN and out-of-range unsigned constants.

This is sampled parity on Apple M2/macOS with Apple Clang 21 and Rust 1.98.1,
not exhaustive proof of libc decimal conversion on every supported platform.
No observed rounding/text discrepancy required dropping an operation. Platform
ports must pass these exact gates; tests must not substitute approximate equality.

## Correctness gates and findings

[Verbatim command output](V5_NUMERIC_VALIDATION.txt) records every check and the
Clang argument lists. Debug and release CI each pass **283 tests**, strict Clippy
has no warnings. Sanitizers pass **88 tests**: application 37, keyed 32, numeric 19;
`float-cast-overflow` is explicitly added to ASan/UBSan. A supplemental run checks
new valid float-to-integer boundaries under the same sanitizer wrapper. The wrapper
instruments IR, runtime C and linking. LLVM conversion guards are tested before
fptosi/fptoui; sanitizer success alone is not proof that a poison-forming cast was
unreachable. Leak checking remains disabled because macOS LeakSanitizer is absent.

A real regression was found and fixed: adding a u128 directly to the syntax enum
increased recursive debug-parser frame alignment enough to overflow before the
nesting diagnostic. Syntax constants now store two u64 words; HIR remains u128.
The pre-existing nesting-limit test and new numeric nesting checks pass. Three
initial native-test fixtures used the forbidden explicit default `:i` annotation;
these fixtures were corrected, not the grammar. The initial Grains corpus adapter
also confused a loop-local state position with the outer parameter; its source was
corrected against the unchanged oracle. A stale corpus support-count assertion was
updated from 32/18 to 36/14; lock/oracle tests are unchanged. The unit log’s two
`FAIL copy_file/python` lines are deliberate negative controls; all 22 tests pass. No sanitizer finding
or reference/native divergence occurred. No compiler/runtime behavior was weakened.

### Differential campaigns

Three final seeded runs each compare 208 generated programs with reference +
in-memory Host and native O0/O2: **624 programs / 1,248 native builds / zero
divergences**. Float results are exposed as canonical `!bits` u64 values and
compared exactly; formatting compares exact bytes. Existing file/stdout/trap
comparisons remain. [Full family/code/mutation counts](V5_NUMERIC_FUZZ.json).

| Seed | Programs | Native builds | E009 | E012 | E013 | E014 | E015 | E016 | E017 | E018 | E019 | E020 | E021 | E022 | OK |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 5130572 | 208 | 416 | 1 | 13 | 12 | 5 | 3 | 9 | 3 | 3 | 1 | 4 | 5 | 3 | 146 |
| 1729 | 208 | 416 | 1 | 13 | 12 | 5 | 3 | 9 | 3 | 3 | 1 | 4 | 5 | 3 | 146 |
| 8675309 | 208 | 416 | 1 | 13 | 12 | 5 | 3 | 9 | 3 | 3 | 1 | 4 | 5 | 3 | 146 |

Each of 40 numeric call families is hit once per seed, covering special values,
raw random arithmetic, unsigned wrap/order, checked/truncating and mixed-width
conversions, parse/format, typed callees, loop state and laziness. Existing 104
alias/call/map/sort/iteration families also run once per seed. Mutation counts are
reported only when a mutation actually changes source. These are directed families
with small randomized operands, not a large-coverage stochastic campaign; the
independent arithmetic/format bit-pattern tests strengthen the small random sample.
Preliminary runs are retained outside the checkout; final runs include the updated
intrinsic reporting and numeric mutations. Nothing is claimed from unexecuted seeds.


## Performance controls (all measured, no retuning)

Same whole-process methodology/scripts as APPLICATION_BUILDERS and the preceding
algorithm round, Apple M2, macOS 27, Apple Clang 21, Rust 1.98.1, Python 3.12.11.
Serial runs after CI/sanitizer/fuzz jobs were idle: one warmup, nine retained
samples, median, rotating NIL/C++/Python order for application workloads. Cached
file I/O, no fsync/CPU isolation. Builds and correctness verification excluded.
No claim of kernel-only speed or controlled regression significance. Manifests
truthfully record dirty documentation/report/submodule worktrees; compiler/runtime
code was committed at main `5c27724`, corpus at benchmark `7ee204b`.

```text
./scripts/bench.sh runtime --full --workloads --workload newlines --workload append --repeats 9 --output /tmp/nil-numeric/controls-workloads
Benchmark artifacts: /private/tmp/nil-numeric/controls-workloads
./scripts/bench.sh runtime --full --application --repeats 9 --output /tmp/nil-numeric/controls-transform
Benchmark artifacts: /private/tmp/nil-numeric/controls-transform
benchmarks/paired/.venv/bin/python benchmarks/application/keyed/run.py --output /tmp/nil-numeric/controls-keyed --repeats 9
```

| Workload | Size / iterations | NIL ms | C++ ms | Python ms | NIL/C++ |
|---|---:|---:|---:|---:|---:|
| append | 10,000 | 2.9185 | 2.4623 | 14.8187 | 1.185 |
| append | 40,000 | 3.4485 | 2.5312 | 15.2915 | 1.362 |
| append | 160,000 | 6.0188 | 2.8095 | 18.8349 | 2.142 |
| append | 640,000 | 15.5827 | 3.8130 | 32.3186 | 4.087 |
| append | 1,048,576 | 24.1527 | 5.0556 | 44.7058 | 4.777 |
| newlines | 4,096 | 2.5204 | 2.4941 | 14.2201 | 1.011 |
| newlines | 1,048,576 | 2.8043 | 2.9383 | 14.8685 | 0.954 |
| newlines | 16,777,216 | 7.9075 | 10.3787 | 24.3261 | 0.762 |
| transform | 4,096 | 2.6905 | 2.5197 | 14.6076 | 1.068 |
| transform | 1,048,576 | 4.9989 | 3.4267 | 63.8719 | 1.459 |
| transform | 16,777,216 | 45.8465 | 20.8672 | 858.4732 | 2.197 |

Append content is verified, newline inputs include binary bytes, and all transform
outputs are byte-exact with double-transform round trips. NIL loses to C++ on all
append and transform sizes and on the 4 KiB scan; it wins the two larger scan
sizes. NIL beats Python on these controls; Python uses `bytes.count` for scans and
an explicit byte loop for transform, as before. No algorithm/baseline was changed.

| Control | Previous NIL ms | Current NIL ms | Previous C++ ms | Current C++ ms |
|---|---:|---:|---:|---:|
| Scan 16 MiB | 7.6435 | 7.9075 | 10.2557 | 10.3787 |
| Append 1 MiB | 26.1005 | 24.1527 | 5.6141 | 5.0556 |
| Transform 16 MiB | 38.2516 | 45.8465 | 15.4776 | 20.8672 |

Absolute scan time rises 3.5%, append falls 7.5%, transform rises **19.9%**. C++
transform rises 34.8%; NIL/C++ transform ratio improves from 2.47x to 2.20x.
Retained 16 MiB transform samples range 36.70–49.68 ms for NIL and 12.40–27.31 ms
for C++. These noisy whole-process results do **not** justify attributing the
absolute increase to numeric support or asserting a statistically established
absence of regression. No resampling was selected to improve the headline.
Read-only/read-write/transform stage medians (independent runs, not additive):

| Input bytes | Read only ms | Read/write ms | Transform ms |
|---|---:|---:|---:|
| 4,096 | 3.5408 | 3.4881 | 2.6905 |
| 1,048,576 | 2.7127 | 3.4417 | 4.9989 |
| 16,777,216 | 6.2391 | 22.4653 | 45.8465 |

Map insertion curve (whole-process, includes formatting and hash growth):

| Entries | Previous ms | Current ms |
|---:|---:|---:|
| 1,000 | 3.9521 | 5.0780 |
| 4,000 | 2.9635 | 3.3125 |
| 16,000 | 4.6063 | 4.3833 |
| 64,000 | 11.2968 | 10.4308 |

Startup noise dominates small insert counts; no claim of monotonic timings there.
The unchanged 262,145-entry ceiling is reconfirmed: 262,144 and 262,145 succeed,
262,146 and 524,288 fail E013. No capacity/quota/map-layout code changed. Existing
byte-value repacking remains a disclosed copying limitation (64,000 updates:
82.45 ms); this round does not solve views, borrowing or allocating-work cliffs.
[Full workload samples/provenance](V5_NUMERIC_WORKLOADS_CONTROL.json),
[transform samples/profiles](V5_NUMERIC_TRANSFORM_CONTROL.json),
[keyed samples/boundary](V5_NUMERIC_KEYED_CONTROL.json) retain every result.

## Local delivery

Logical Conventional Commits, no pushes in either repository. ADRs precede type,
frontend/reference, strict codegen, differential and corpus implementation commits.
Earlier profiles/default, 64 MiB live-capacity quota, byte/bounds checks, map limits,
immutable alias behavior and existing intrinsic contracts remain unchanged.
