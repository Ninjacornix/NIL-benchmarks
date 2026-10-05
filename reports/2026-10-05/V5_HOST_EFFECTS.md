# Expr-v5 host effects — verified delivery and limits

Environment, injectable randomness and sorted directory snapshots are implemented. **One task, not the target three, became verified: env_lookup.** Entropy/grep adapters are not counted as solves. No core language type, earlier profile or default changed. Nothing was pushed.

## Contracts and proof visibility

[ADR 033](../../../docs/adr/033.md) was committed as `ae34bfc` before implementation `1761538`. It classifies all 13 original gaps against ADR 026. The audited intrinsic enum count is **32 -> 35**, one contract each for env, random and directory; the preregistration arithmetic typo (33 -> 36) was corrected visibly in `19c21f8`. No library algorithm/type was added.

Env returns owned raw OS bytes (empty for absent or empty). Random returns u64, draws once per selected call, and is not cryptographic. SeededHost and native NIL_RANDOM_SEED use identical wrapping SplitMix64; OS seeding is lazy and injectable, not exempt from the oracle. Directory returns an owned MapI64 of basename -> 0 in unsigned-byte lexical order, excluding dot entries, including files/directories/symlinks. Existing map capacity and live-quota accounting apply. NUL/name errors precede denial, acquisition errors precede final quota admission. No recursive listing, metadata, recoverable I/O, env mutation or empty-vs-absent distinction.

All three are host effects and non-borrowing. Modules share the caller Host/arena; borrow-only providers reject them. Reference execution without Host remains E018. Stateful FileHost now uses FileHost::default(), documented as a Rust embedding API migration.

## Validation

Commands executed from the compiler repository; full logs are archived outside the checkout. [Receipts](V5_HOST_EFFECTS_VALIDATION.json) include log SHA-256 and complete per-family/per-code fuzz outcomes.

```text
./scripts/ci.sh                         PASS: 400 tests, no Clippy warnings
./scripts/ci.sh release                 PASS: 400 tests
./scripts/sanitize.sh                   PASS: 159 tests, all eight native suites
./scripts/fuzz-v5.sh --seed 5130572      PASS: 392 programs / 784 native builds / 0 divergences
./scripts/fuzz-v5.sh --seed 1729         PASS: 392 programs / 784 native builds / 0 divergences
./scripts/fuzz-v5.sh --seed 4294967295   PASS: 392 programs / 784 native builds / 0 divergences
```

The three seeded runs each exercised all 36 host families (108 total), including OS-byte env values, denial, name/path errors, random streams/calls/lazy arms/loop state, ordered/empty/1024-entry/unreadable directories and live-quota failures. Every generated program executes in reference and native O0/O2. Tests also check published RNG vectors, effect order, module/provider contracts, and named O0/O2 unavailable-entropy parity via a macOS sandbox that denies /dev/urandom. This sandbox is a test-only fault fixture, not a NIL security claim.

| Code | Seed 5130572 | Seed 1729 | Seed 4294967295 |
|---|---:|---:|---:|
| E009 | 2 | 2 | 2 |
| E012 | 19 | 19 | 19 |
| E013 | 29 | 29 | 29 |
| E014 | 6 | 6 | 6 |
| E015 | 8 | 8 | 8 |
| E016 | 13 | 13 | 13 |
| E017 | 10 | 10 | 10 |
| E018 | 9 | 9 | 9 |
| E019 | 3 | 3 | 3 |
| E020 | 6 | 6 | 6 |
| E021 | 5 | 5 | 5 |
| E022 | 3 | 3 | 3 |
| OK | 279 | 279 | 279 |

Findings: no compiler/runtime divergence or sanitizer finding. The first native filename fixture failed to create 0xff on this macOS filesystem; native non-UTF-8 environment values and injected unsigned-byte directory ordering are distinct evidence, not native filename coverage. The preliminary quota families were weak: reading the old length before allocation made the value dead. Final generation reversed that order, requires E013, and records both host_env_quota and host_directory_quota as E013 on every seed. The initial checker inherited unrelated environment variables after env was enabled; it now uses scrubbed fixture environments, including preflight. A sentinel audit passed on all five reference invocations, with 4 reference/8 native task checks. Minor test Clippy issues were fixed before final gates.

## Corpus coverage and remaining backlog

[Verification](V5_HOST_EFFECTS_CORPUS.json): **2,790 checks** = 558 reference + 1,116 native + 558 Python + 558 C++. 79 frozen tasks, 67 verified NIL solutions/export positives, 12 unsupported. [Original 610](V5_HOST_EFFECTS_ORIGINAL_610.json) retain 120 reference + 240 native + 125 Python + 125 C++; env adds only 5 reference/10 native. All [210 pre-existing contracts, baselines and solution files](V5_HOST_EFFECTS_FROZEN.json) were byte-identical to starting submodule 7490092. Tasks, goldens, oracles and baseline sources were not changed.

| Unsupported task | Placement | Actual remaining blocker |
|---|---|---|
| ex_accumulate | Core | Higher-order abstraction explicitly required |
| ex_bank_account | Core, defer | Concurrent execution/synchronization and arena proof |
| ex_hangman | Core callback contract + library | Published reactive integration requirement; sequential transcript is insufficient |
| ex_diffie_hellman | Core entropy delivered; harness follow-up | Frozen input is {}, golden is {"greaterThan":1,"lessThan":"p"}, not a concrete p/key property oracle; emitting that object would not verify randomness. Corpus checker entropy-fixture injection also remains to be integrated |
| ex_grep | Library/harness; core file access exists | Three canonical poem fixtures are checked in, but reference/native fixture mounting and JSON/flag adapter remain; directory listing is not grep |
| ex_anagram | Plugin/library | Unicode codec/normalization/algorithm |
| ex_bob | Plugin/library | Unicode classification tables/algorithm |
| ex_gigasecond | Plugin/library | Calendar arithmetic/formatting |
| ex_alphametics | Plugin/library | Verified constraint-search/JSON adapter |
| ex_dot_dsl | Plugin/library | Graph/attribute/serialization adapter; structured index storage is available |
| ex_camicia | Plugin/library | Deck/cycle simulation and JSON adapter |
| ex_forth | Plugin/library | Dictionary interpreter/parser adapter |

Frozen unsupported_reason fields in raw task/verification metadata describe the earlier round; the table above and ADR 033 are the current classification. No theoretical unexpressibility claim is made for unfinished encoded-data algorithms. Concurrency is explicitly deferred; higher-order gets its own core decision.

## Source density

**Raw source density is not total model tokens to correctness.** No inference ran here. The earlier failed generation/few-shot study remains the evidence for that thesis; zero NIL solves remain unfavourable. Unsupported tasks are excluded from paired density. All 66 old solutions/counts are unchanged. Adding one new paired task is a cohort change, not syntax improvement.

Full [per-task table](V5_HOST_EFFECTS_TOKENS.csv), [density/version metadata](V5_HOST_EFFECTS_DENSITY.json), and [67-example JSONL](V5_HOST_EFFECTS_ADAPTATION.jsonl).

| Cut | Tokenizer | NIL | Python | C++ | vs Python | vs C++ |
|---|---|---:|---:|---:|---:|---:|
| original (25) | gemma3_4b | 2161 | 2305 | 5642 | -6.25% | -61.70% |
| original (25) | qwen2.5_7b_instruct | 1646 | 1786 | 4378 | -7.84% | -62.40% |
| original (25) | cl100k_base | 1594 | 1763 | 4360 | -9.59% | -63.44% |
| original (25) | o200k_base | 1583 | 1770 | 4381 | -10.56% | -63.87% |
| new_external (42) | gemma3_4b | 10557 | 8041 | 16720 | +31.29% | -36.86% |
| new_external (42) | qwen2.5_7b_instruct | 8153 | 6564 | 13326 | +24.21% | -38.82% |
| new_external (42) | cl100k_base | 7946 | 6483 | 13280 | +22.57% | -40.17% |
| new_external (42) | o200k_base | 7935 | 6508 | 13347 | +21.93% | -40.55% |
| combined (67) | gemma3_4b | 12718 | 10346 | 22362 | +22.93% | -43.13% |
| combined (67) | qwen2.5_7b_instruct | 9799 | 8350 | 17704 | +17.35% | -44.65% |
| combined (67) | cl100k_base | 9540 | 8246 | 17640 | +15.69% | -45.92% |
| combined (67) | o200k_base | 9518 | 8278 | 17728 | +14.98% | -46.31% |

Original now means 25 (old 24 plus env); external remains 42/54 supported; combined is 67/79. On matched old cohorts, savings are exactly zero across all four tokenizers. Env alone costs NIL 17/12/12/12, Python 78/58/58/58 and C++ 188/143/143/143. External Python deficit remains 21.9–31.3%; combined is 15.0–22.9%, improved only by the added env pairing.

| Cut | NIL bytes/chars | Python bytes/chars | C++ bytes/chars |
|---|---:|---:|---:|
| original | 3341/3341 | 6995/6995 | 17902/17902 |
| new_external | 16822/16822 | 25088/25088 | 52943/52943 |
| combined | 20163/20163 | 32083/32083 | 70845/70845 |

Tokenizers and versions/digests are unchanged and recorded in JSON. 67 positives remain a small verified seed set, not a demonstrated fine-tuning-scale corpus. No syntax, tokenizer, baseline or task was tuned to improve counts.

## Performance controls

Apple M2/macOS, Clang 21, O2/LTO, 25 measured warm whole-process samples per language, one warmup, rotating language order; compilation excluded, output verified, no fsync or CPU isolation. Same commands/methodology as V5_MODULES and APPLICATION_BUILDERS. [Raw controls](V5_HOST_EFFECTS_CONTROLS.json), [transform/stages](V5_HOST_EFFECTS_TRANSFORM.json). Historical comparison is the preceding 25-repeat module round; variability does not establish a speedup from host effects.

| Workload | Historical NIL ms | NIL ms | NIL min–max ms | C++ ms | Python ms |
|---|---:|---:|---:|---:|---:|
| Append 1 MiB | 22.899 | 22.839 | 22.230–30.831 | 5.084 | 45.749 |
| Scan 16 MiB | 7.728 | 7.560 | 7.416–8.057 | 10.185 | 24.035 |
| Transform 16 MiB | 36.819 | 36.186 | 35.257–39.986 | 13.166 | 789.364 |

No observed control regression. NIL still loses append/transform to C++; these controls do not measure new host-operation throughput or establish general C++ parity. Append content and binary scan controls passed; transform output was byte-exact and double-transformed back to the original at 4 KiB, 1 MiB and 16 MiB. Quota remains 64 MiB; earlier storage/builder and opaque-provider limitations are unchanged. Host scratch/OS resources are outside the NIL value quota; native execution/FileHost remain trusted and unsandboxed.

## Reproduction

```sh
./scripts/ci.sh
./scripts/ci.sh release
./scripts/sanitize.sh
./scripts/fuzz-v5.sh --seed 5130572
./scripts/fuzz-v5.sh --seed 1729
./scripts/fuzz-v5.sh --seed 4294967295
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/verify.py --output /tmp/host-corpus.json
benchmarks/paired/.venv/bin/python benchmarks/corpora/application-v5/density.py --verification /tmp/host-corpus.json --output /tmp/host-density
./scripts/bench.sh runtime --full --workloads --workload append --workload newlines --repeats 25 --output /tmp/host-controls
./scripts/bench.sh runtime --full --application --repeats 25 --output /tmp/host-transform
```

With an expr-v5 program `:u64=!random()`, `NIL_RANDOM_SEED=0 ./program` printed `16294208416658607535`. Directory listing of the three poem fixtures plus their README returned 4. The working tree is committed locally on feat/application-core and exp/application-storage; origin refs remain unchanged. No approval was inferred to push.

Raw log/archive: `/Users/ninjacornix/.local/share/nil/benchmarks/archive/v5-host-effects-2026-10-05.tar.gz`. SHA-256: `3880625b2d27565271d6be7fe767cbd6d2cc7a4fea8ea2c9f98d00e4e70ba88d`.
