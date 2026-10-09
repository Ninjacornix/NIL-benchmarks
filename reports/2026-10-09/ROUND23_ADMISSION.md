# Round 23 B4 — failed depth/stack admission

**No B4 compiler fix shipped.** The committed audit finds 11/36 exact comparisons,
19 signal-11 crashes and six rejected bounded depth-1024 builds. The large-record
case also crashes in bounded O0, confirmed separately as ASan stack-overflow.
This supersedes any inference that bounded execution already protects all frames.
Round 23 remains incomplete; compiler source is unchanged from gated B3.

## Reproduce

```sh
cargo build --workspace --release --locked --offline
python3 -m unittest discover -s benchmarks/core-memory-study -p 'test_*.py'
python3 benchmarks/core-memory-study/audit_depth.py --out /tmp/nil-depth-admission-new
```

Audit output: `11/36 exact; 25 failed`, exit **1**. The 13 offline harness tests
pass; they validate observation integrity, not native stack safety. Raw requests,
binaries, diagnostic stderr and sources are outside git. Summary/status/source
hashes and command receipts are in [ROUND23_ADMISSION.json](ROUND23_ADMISSION.json).

Three sources: reported literal 200,000-depth byte recursion, mutual byte
recursion, and recursion carrying a 3,840-slot record made of fifteen fixed
256-element arrays. Actual evaluator and backend APIs use configured depths
32/256/1024, bounded/unbounded builds, O0/O2. Reference always reports E008;
no process signal, build rejection or sanitizer finding is translated to E008.

| Family | Bounded 32 O0/O2 | Bounded 256 O0/O2 | Bounded 1024 O0/O2 | Unbounded 32/256/1024 O0/O2 |
|---|---|---|---|---|
| Reported literal | E008/E008 | E008/E008 | Build rejected | Signal 11 throughout |
| Mutual recursion | E008/E008 | E008/E008 | Build rejected | Signal 11 throughout |
| Large record | E008/E008 | Signal 11/E008 | Build rejected | Signal 11 throughout |

The large recursive frame measures 63,952 bytes at O0 versus 2,272 at O2;
entry measures 32,944 versus 112. These are object machine-frame measurements
with `"warn-stack-size"="0"`, not estimates of LLVM allocas and not a final
linked bound. The entry depth guard runs after the machine prologue. Large O0
frames exhaust the host stack before reaching depth 256. Bounded O2 and reference
agree on `E008 @13903..13911`. The instrumented bounded O0 case reports ASan
stack-overflow and exits on signal 6, not an acceptable depth diagnostic.

A private-stack, pre-call headroom implementation still needs a complete bound
through runtime helper chains, record children, entry and sanitizer-added frames.
Logical depth must also survive source-call inlining and guarded scalar replay.
ADR 046's admission rule prohibits a guessed stack size or treating arbitrary
signals as stack exhaustion. The bound has not been established; no partial
entry-counter patch was shipped. Default-fuzzer COV-1 remains unmet.

## Every resource-inconclusive family

Archived B3 seeds 23601/23602: 88 comparisons each, 44 families at O0/O2. Of all
176 comparisons, 172 have E013 on both paths at the same span. Four have reference
E013 and native success (`inline_push_quota`). The successful byte result is
verified exactly: 33,554,393 zeros, byte 1, newline. Native IR selects unique
concat while reference allocation may require a second full capacity; different
storage needs are permitted ordinary resource behavior. Output files match in
all archived final O2 observations. The source/output hashes and spans for every
comparison are in the JSON.

No signal, malformed diagnostic, sanitizer report or other conflicting code was
found within this E013 subset. This does not validate suffixes which never run
after resource failure. Negative-length inputs also use E013, and therefore lose
semantic-coverage claims under the all-E013 exception. Per-attempt O0 file bytes
were checked in the original fuzzer but not separately archived; the retrospective
file comparison sees only final O2 bytes. The independent depth failures above
are not included in these inconclusives.

| Family index | Family | Seed 23601 comparisons | Seed 23602 comparisons | Native result at O0/O2 |
|---:|---|---:|---:|---|
| 10 | `base_negative_buffer_length` | 2 | 2 | E013 / E013 |
| 11 | `base_64m_bytes_constructor` | 2 | 2 | E013 / E013 |
| 29 | `base_negative_bytes_length_and_bad_fill` | 2 | 2 | E013 / E013 |
| 92 | `parsebuf_quota_priority` | 2 | 2 | E013 / E013 |
| 120 | `map_quota_boundary` | 2 | 2 | E013 / E013 |
| 128 | `map_constructor_quota` | 2 | 2 | E013 / E013 |
| 129 | `map_byte_constructor_quota` | 2 | 2 | E013 / E013 |
| 130 | `map_put_quota` | 2 | 2 | E013 / E013 |
| 131 | `map_key_result_quota` | 2 | 2 | E013 / E013 |
| 132 | `map_lookup_result_quota` | 2 | 2 | E013 / E013 |
| 162 | `each_ignored_value_quota` | 2 | 2 | E013 / E013 |
| 224 | `record_live_quota` | 2 | 2 | E013 / E013 |
| 235 | `record_map_quota` | 2 | 2 | E013 / E013 |
| 248 | `plugin_live_quota` | 2 | 2 | E013 / E013 |
| 261 | `plugin_equal_bounds_order` | 2 | 2 | E013 / E013 |
| 262 | `plugin_argument_quota_order` | 2 | 2 | E013 / E013 |
| 278 | `collection_negative_length` | 2 | 2 | E013 / E013 |
| 279 | `collection_quota` | 2 | 2 | E013 / E013 |
| 284 | `collection_live_children_quota` | 2 | 2 | E013 / E013 |
| 291 | `collection_zero_quota` | 2 | 2 | E013 / E013 |
| 305 | `layout_nested_zero_negative` | 2 | 2 | E013 / E013 |
| 317 | `bulk_quota_failure` | 2 | 2 | E013 / E013 |
| 325 | `field_append_quota_alias` | 2 | 2 | E013 / E013 |
| 329 | `nested_builder_quota` | 2 | 2 | E013 / E013 |
| 341 | `module_live_quota` | 2 | 2 | E013 / E013 |
| 343 | `module_quota_boundary` | 2 | 2 | E013 / E013 |
| 364 | `host_env_quota` | 2 | 2 | E013 / E013 |
| 381 | `host_directory_quota` | 2 | 2 | E013 / E013 |
| 402 | `hof_quota` | 2 | 2 | E013 / E013 |
| 428 | `std_callback_quota` | 2 | 2 | E013 / E013 |
| 447 | `transfer_quota_partial` | 2 | 2 | E013 / E013 |
| 464 | `reconcile_quota_failure` | 2 | 2 | E013 / E013 |
| 470 | `inline_push_quota` | 2 | 2 | OK / OK; reference E013 |
| 639 | `binding_live_quota` | 2 | 2 | E013 / E013 |
| 655 | `g2_quota_before_read` | 2 | 2 | E013 / E013 |
| 660 | `g2_allocation_barrier` | 2 | 2 | E013 / E013 |
| 702 | `io_quota_real_read` | 2 | 2 | E013 / E013 |
| 704 | `io_quota_before_late_fault` | 2 | 2 | E013 / E013 |
| 705 | `io_buffer_retention` | 2 | 2 | E013 / E013 |
| 706 | `io_record_child` | 2 | 2 | E013 / E013 |
| 707 | `io_record_buffer_child` | 2 | 2 | E013 / E013 |
| 708 | `io_map_and_child` | 2 | 2 | E013 / E013 |
| 709 | `io_selected_lazy` | 2 | 2 | E013 / E013 |
| 710 | `io_callee_retention` | 2 | 2 | E013 / E013 |

## Refreshed existing gates (same B3 compiler source)

| Command | Exit | Tests | Findings |
|---|---:|---:|---|
| `./scripts/ci.sh` | 0 | 551 | Zero warnings |
| `./scripts/ci.sh release` | 0 | 551 | Zero warnings |
| `./scripts/sanitize.sh` | 0 | 250 | No suite ASan/UBSan findings |

Raw log hashes and invocation timestamps are in the JSON. The **new targeted
ASan stack-overflow finding still fails admission**; passing existing suites
does not erase it. No B4 compiler change was made. Earlier B3 corpus/fuzz gates
therefore cover identical compiler source, but their missing E008 coverage is
explicit. Nothing was pushed.
