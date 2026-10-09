# Round 24 — guarded stacks and resource-audit admission

**Unfavourable first:** ownership cliffs remain: natural qualification is
19/150, tuned 22/150. Std swap/pop still miss caller parity. Thirty-six persistent
E008 comparisons per seed are inconclusive, not correctness successes. Linux
code paths are implemented but this admission is macOS arm64 only. Parts B/C are
not implemented; no ownership gain is attributed to stack machinery.

## Full differential campaigns

| Seed | Programs | Builds | Escalated | Resolved | Persistent E008 | Persistent E013 | Divergences |
|---|---:|---:|---:|---:|---:|---:|---:|
| 24201 | 733 | 1580 | 114 | 78 | 36 | 0 | 0 |
| 24202 | 733 | 1580 | 114 | 78 | 36 | 0 | 0 |

All 733 indexed families executed once per seed. Host stdout and files are compared on every original and escalated execution; successful return values have a separate native receipt.

### Original reference outcomes (each seed)

| Code | Programs |
|---|---:|
| E008 | 18 |
| E009 | 8 |
| E012 | 33 |
| E013 | 39 |
| E014 | 16 |
| E015 | 12 |
| E016 | 14 |
| E017 | 10 |
| E018 | 11 |
| E019 | 3 |
| E020 | 6 |
| E021 | 35 |
| E022 | 3 |
| OK | 525 |

### Original resource families (each O0/O2 comparison)

| Family / original direction and codes | Comparisons per seed |
|---|---:|
| `binding_live_quota:both:reference=E013:native=E013` | 2 |
| `bulk_quota_failure:both:reference=E013:native=E013` | 2 |
| `bytes_allocation_guard:both:reference=E013:native=E013` | 2 |
| `collection_live_children_quota:both:reference=E013:native=E013` | 2 |
| `collection_quota:both:reference=E013:native=E013` | 2 |
| `collection_zero_quota:both:reference=E013:native=E013` | 2 |
| `each_ignored_value_quota:both:reference=E013:native=E013` | 2 |
| `field_append_quota_alias:both:reference=E013:native=E013` | 2 |
| `g2_allocation_barrier:both:reference=E013:native=E013` | 2 |
| `g2_quota_before_read:both:reference=E013:native=E013` | 2 |
| `hof_quota:both:reference=E013:native=E013` | 2 |
| `host_directory_quota:both:reference=E013:native=E013` | 2 |
| `host_env_quota:both:reference=E013:native=E013` | 2 |
| `inline_push_quota:reference-only:reference=E013:native=OK` | 2 |
| `io_buffer_retention:both:reference=E013:native=E013` | 2 |
| `io_callee_retention:both:reference=E013:native=E013` | 2 |
| `io_map_and_child:both:reference=E013:native=E013` | 2 |
| `io_quota_before_late_fault:both:reference=E013:native=E013` | 2 |
| `io_quota_real_read:both:reference=E013:native=E013` | 2 |
| `io_record_buffer_child:both:reference=E013:native=E013` | 2 |
| `io_record_child:both:reference=E013:native=E013` | 2 |
| `io_selected_lazy:both:reference=E013:native=E013` | 2 |
| `map_byte_constructor_quota:both:reference=E013:native=E013` | 2 |
| `map_constructor_quota:both:reference=E013:native=E013` | 2 |
| `map_key_result_quota:both:reference=E013:native=E013` | 2 |
| `map_lookup_result_quota:both:reference=E013:native=E013` | 2 |
| `map_put_quota:both:reference=E013:native=E013` | 2 |
| `map_quota_boundary:both:reference=E013:native=E013` | 2 |
| `module_live_quota:both:reference=E013:native=E013` | 2 |
| `module_quota_boundary:both:reference=E013:native=E013` | 2 |
| `nested_builder_quota:both:reference=E013:native=E013` | 2 |
| `parsebuf_quota_priority:both:reference=E013:native=E013` | 2 |
| `plugin_argument_quota_order:both:reference=E013:native=E013` | 2 |
| `plugin_live_quota:both:reference=E013:native=E013` | 2 |
| `reconcile_quota_failure:both:reference=E013:native=E013` | 2 |
| `record_live_quota:both:reference=E013:native=E013` | 2 |
| `record_map_quota:both:reference=E013:native=E013` | 2 |
| `std_callback_quota:both:reference=E013:native=E013` | 2 |
| `transfer_quota_partial:both:reference=E013:native=E013` | 2 |
| `unbounded_stack_large_record:both:reference=E008:native=E008` | 12 |
| `unbounded_stack_mutual:both:reference=E008:native=E008` | 12 |
| `unbounded_stack_sequence:both:reference=E008:native=E008` | 12 |

### Persistent resources after joint 4x escalation (each seed)

| Family / direction and codes | Comparisons |
|---|---:|
| `unbounded_stack_large_record:both:reference=E008:native=E008` | 12 |
| `unbounded_stack_mutual:both:reference=E008:native=E008` | 10 |
| `unbounded_stack_mutual:reference-only:reference=E008:native=OK` | 2 |
| `unbounded_stack_sequence:both:reference=E008:native=E008` | 12 |

Source diversity: 725 / 725 distinct hashes; union 833, intersection 617. Seeds vary more than constants in some families, but many family shapes are intentionally fixed.

## Gate receipts

All commands ran on the final Part A implementation, before timing; no compiler
or fixture changed between gates. Logs/JSON and source hashes are archived outside
git at `~/.local/share/nil/round24-chains/part-a/`.

```text
./scripts/ci.sh                       563 passed; zero warnings
./scripts/ci.sh release               563 passed; zero warnings
./scripts/sanitize.sh                 259 passed; no ASan/UBSan finding
python3 benchmarks/core-memory-study/audit_depth.py --out /tmp/nil-round24-a-admission-depth
                                     36/36 nondivergent; 0 failed, 0 signals
python3 benchmarks/core-memory-study/audit_read_order.py --out /tmp/nil-round24-a-admission-read --require-parity
                                     14 families; 168 comparisons; 72 exact,
                                     96 resource-inconclusive; 0 divergence
python3 benchmarks/corpora/application-v5/verify.py --output /tmp/nil-round24-a-admission-corpus.json
                                     2,815 checks; 68 NIL programs; 0 inconclusive
python3 benchmarks/corpora/application-v5/verify.py --group original --output /tmp/nil-round24-a-admission-original.json
                                     exactly 610 checks; 0 inconclusive
python3 benchmarks/corpora/neetcode150/verify.py --verified-only --jobs 1 --candidate-dir /Users/ninjacornix/NIL/benchmarks/core-generalize-study/natural --output /tmp/nil-round24-a-admission-natural.json
                                     1,070/1,070 checks; 29 programs; 0 inconclusive
python3 benchmarks/corpora/neetcode150/verify.py --verified-only --jobs 1 --output /tmp/nil-round24-a-admission-tuned.json
                                     1,070/1,070 checks; 29 programs; 0 inconclusive
python3 -m unittest discover -s benchmarks -p test_resource_outcomes.py -v
                                     5 passed
./scripts/fuzz-v5.sh --seed 24201 --out /tmp/nil-round24-final-a-fuzz-24201
./scripts/fuzz-v5.sh --seed 24202 --out /tmp/nil-round24-final-a-fuzz-24202
                                     each 733 programs / 1,580 builds;
                                     zero non-resource divergences
```

The depth audit has 33 native E008 outcomes and three successful native O2
mutual-recursion runs; the reference depth guard fires in all 36. These are
explicitly resource-inconclusive. In particular the reported literal
`=#b(200000)` / `1:s=a<1?!bytes(1,0):!concat(b(a-1),!bytes(1,1))`
now exits 1 with `E008 call depth/stack exhausted` at O0 and O2, without a signal.
The bounded O0 large-record ASan witness and zero-slot variant are covered too.
`nm -u .../large-record-recursion/native-32-unbounded-O0` includes
`___chkstk_darwin`; large frames probe the guarded range. The genuine non-guard
bad-access regression still dies by signal, rather than becoming E008.

Negative-length families (`negative_buffer_length`,
`negative_bytes_before_fill_range`, `plugin_equal_bounds_order`,
`collection_negative_length`, `layout_nested_zero_negative`) now compare exact
E014 code/span at O0/O2. These account for the ten comparisons removed from the
historical 88 E013 total: 78 original E013 comparisons remain and all resolve
at joint 4x limits. No old E013 case was silently dropped.

## Isolated performance

Whole-process warm timings; same Apple Clang 21/O2; rotating order; 25 repeats
for controls/updates, 15 for each admitted problem. Timings and RSS use plain
binaries; charge counters run separately. The before binary is built from an
archive of **80e5cc6**, not an older B3 checkpoint. Source and binary hashes are
in the archived JSON. No CI, fuzz or corpus verifier ran alongside measurements.
Transform output is byte-exact and a double transform round-trips.

### Controls — min / median / max milliseconds

| Batch / workload | Before 80e5cc6 | Part A | C++ |
|---|---:|---:|---:|
| first / append | 4.593 / 5.114 / 6.393 | 4.857 / 5.249 / 6.401 | 3.624 / 4.271 / 5.671 |
| first / scan | 7.742 / 8.494 / 9.434 | 8.242 / 8.569 / 9.136 | 10.325 / 11.278 / 12.757 |
| first / transform | 36.182 / 41.203 / 54.722 | 36.217 / 45.596 / 54.780 | 13.942 / 23.829 / 34.941 |
| repeat / append | 4.877 / 5.209 / 7.245 | 4.501 / 5.233 / 6.759 | 3.821 / 4.279 / 6.216 |
| repeat / scan | 7.777 / 8.680 / 9.152 | 8.044 / 8.653 / 9.163 | 10.569 / 11.367 / 12.393 |
| repeat / transform | 35.532 / 37.110 / 64.808 | 35.917 / 37.605 / 59.551 | 13.283 / 14.945 / 30.117 |

Append builds 1 MiB; transform uses 16 MiB. The historical scan fixture is
**17 MiB**, not 16 MiB (`alpha,beta,gamma\n` repeated 1,048,576 times).
Do not mislabel that historical control. First-batch transform medians were
+10.7%, but paired bootstrap median-delta 95% interval was -0.52..6.30 ms and
minima were equal. The prespecified isolated repeat measured +1.3%; C++ also
moved 23.83 -> 14.94 ms. There is no reproduced >10% regression. Both batches
are retained; neither is excluded or averaged into a more favourable claim.

### Five natural cliffs — min / median / max milliseconds

| Problem | Natural Part A | Tuned Part A | C++ | Natural / C++ |
|---|---:|---:|---:|---:|
| balanced-binary-tree | 1484.652 / 1495.730 / 1581.632 | 26.692 / 28.351 / 30.412 | 13.209 / 14.117 / 21.493 | 105.95 |
| course-schedule | 4175.180 / 4256.664 / 4483.179 | 41.838 / 42.987 / 44.040 | 22.889 / 23.521 / 26.462 | 180.98 |
| last-stone-weight | 61.570 / 64.268 / 65.493 | 55.227 / 58.171 / 60.470 | 11.066 / 11.874 / 12.927 | 5.41 |
| spiral-matrix | 28.146 / 28.873 / 29.556 | 25.512 / 26.110 / 27.227 | 7.604 / 8.436 / 8.594 | 3.42 |
| validate-binary-search-tree | 1394.278 / 1413.920 / 1521.840 | 23.936 / 24.738 / 25.346 | 12.847 / 13.500 / 14.650 | 104.74 |

Natural/tuned qualification remains 19/150 and 22/150, matching the Part A
forecast. Largest-fixture measurements may cross the 3x boundary with noise;
the individual tuned spiral sample is 3.09x, not claimed as qualifying here.
The archived full 29-problem matrix carries all per-program verdicts and RSS.
No held-out problem was attempted and no natural/tuned source was edited.

### Std update boundary — min / median / max milliseconds

| Type / operation | Std | Checked caller | Ratio |
|---|---:|---:|---:|
| bytes / swap | 24.259 / 24.540 / 37.611 | 6.660 / 7.183 / 17.898 | 3.42 |
| bytes / pop | 13.176 / 13.935 / 25.498 | 7.668 / 7.982 / 18.458 | 1.75 |
| buffer / swap | 23.513 / 24.202 / 26.130 | 6.861 / 7.536 / 9.283 | 3.21 |
| buffer / pop | 13.580 / 14.106 / 22.032 | 7.799 / 8.431 / 18.582 | 1.67 |

This confirms the B3 forecast miss before Part C: call/root-frame overhead is
still present because linear source expansion excludes Index/Replace/Length/Slice.
The proposed fix is a general HIR leaf expansion before rooting, not a std-name
special case. No core placement or inlining change is made in Part A.

## Audit findings and accepted boundaries

- Fixed a Darwin alternate-stack restore error: SS_DISABLE still requires a
  valid ss_size. The original implementation could report startup E008 on success.
  Passing success tests and sanitizer gates now exercise restore/worker exit.
- Updated stale E013 negative-length expectations; the deterministic failure is
  deliberately E014 per the preregistered audit amendment.
- Result receipts separate successful return rendering from host stdout, so
  resource escalation cannot discard effects or confuse them with a return print.
- Unique concat already asserts rooted heap operands/synthetic stack temporaries
  before collection. The new heap-RHS/record-child growth regression passes at
  O0/O2 and under sanitizers; the assertion did not fire.
- Record-buffer swap/pop rejection is explicitly E007-tested. No child ownership
  proof is silently relaxed.
- Natural BST retention is a cross-region/path-correlation limitation: updates
  happen in a sequence-valued lazy arm, later reads in the opposite outer arm.
  Parent liveness unions the paths. The copies are avoidable on the executed
  path, but the current same-region scalar replay cannot retire that parent root.
  See ADR 047's diagnosis; no G1 work or narrow matcher was added.
- Two early contended fuzz attempts timed out on the sort-boundary family; serial
  final campaigns passed that same family. Timeouts were failures, not relabeled
  E013/E008. Those attempts are not counted as admitted campaigns.

Defaults: allocation guard 256 MiB, reference/bounded depth 16,384, native stack
32 MiB. Earlier source profiles and the default keep their non-resource behaviour;
stack handling is shared execution machinery. Intrinsic count stays 35.

## Peak RSS (three isolated samples per binary)

MiB from macOS `/usr/bin/time -l`; counter binaries excluded. Guarded stack
virtual reservation is not resident payload.

| Workload | Before RSS MiB | Part A RSS MiB | C++ RSS MiB |
|---|---:|---:|---:|
| append | 2.67 | 2.72 | 3.59 |
| scan | 18.61 | 18.66 | 18.61 |
| transform | 17.62 | 17.67 | 17.62 |

| Natural cliff | NIL RSS MiB | C++ RSS MiB | Ratio |
|---|---:|---:|---:|
| balanced-binary-tree | 6.28 | 11.20 | 0.56 |
| course-schedule | 16.20 | 13.31 | 1.22 |
| last-stone-weight | 3.77 | 4.52 | 0.83 |
| spiral-matrix | 4.62 | 6.09 | 0.76 |
| validate-binary-search-tree | 6.95 | 8.66 | 0.80 |

## Reproduction and next step

Run the gate commands above. For timings:

```sh
python3 benchmarks/core-generalize-study/measure_controls.py --output /tmp/round24-controls.json --repeats 25 --baseline-compiler ~/.local/share/nil/round24-chains/baseline-80e5cc6/target/release/nil --baseline-revision 80e5cc6
python3 benchmarks/core-generalize-study/measure_cohort.py --output /tmp/round24-cohort.json --repeats 15
python3 benchmarks/core-memory-study/measure_updates.py --output /tmp/round24-updates.json --repeats 25
```

Part A is complete. Commit locally, then preregister ADR 048 before implementing
simultaneous chains. Part C follows only after Part B gates. Nothing was pushed.
