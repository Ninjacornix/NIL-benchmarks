# Round 24 — guarded stacks, simultaneous chains, checked std expansion

**Natural qualification is 19/150; tuned is 23/150.**
The cross-region tree/course/BST copy cliffs remain. Do not credit tuned
rewrites as natural-code gains. No held-out problem was attempted. This report
states all timings, including misses; density and frozen sources are unchanged.

## Decisions and findings

[Part A](../2026-10-09/ROUND24_A.md) admits ADR 047 guarded stacks and resource
classification. RT-1’s 200,000-call unbounded repro now exits with clean E008 at
O0/O2; the large-record ASan witness passes. Guard-page faults only are caught;
genuine non-stack bad accesses remain crashes. Default stack 32 MiB, configurable
with `--stack-size` / `Options.stack_bytes`; reference/bounded depth 16,384.
E008/E013 are ordinary resource outcomes; negative lengths are exact E014.
POSIX native support is required; local evidence is arm64 macOS, not a claim
of independent Linux/x86 validation. This is neither concurrency nor a sandbox.

[Part B](ROUND24_B.md), preregistered ADR 048, evaluates all contiguous-chain
operands left-to-right before writes, with zero syntax/token cost. Writes commit
in source order; duplicate targets use the last value. Grouping is transparent;
bindings, projections, calls and control results are boundaries. Selected lazy
arms only execute their own operands. This deliberately changes v5 fault/effect
order; earlier profiles keep eager order. The two documented fuzz changes are
E014→E012 (`g2_byte_trap_first`) and E013→E012 (`g2_quota_before_read`).
CI found a record-field append proof regression, fixed by following the result’s
sole use rather than requiring adjacency; alias/escape guards remain intact.

Part C follows the 2026-10-10 ADR 040 amendment, committed as `9ac7c62` before
code. Small flat leaf bodies (<=8 instructions, one Buffer/Bytes parameter/result)
may use SSA arguments repeatedly or leave them unused. Already-evaluated caller
argument expressions are never duplicated. Index/Replace/Length/Binary/Compare
and Buffer/Bytes/Concat/Slice instructions clone in order with original spans.
No std-name matcher; no new ownership assertion. HIR revalidates before normal
root/last-use/alias proofs. Bounded calls remain; lazy-region work stays inside
its region. Calls/regions/aggregates/effects inside a candidate body stay conservative.

First full CI found a leftover exact-E013 test assumption, not a non-resource
compiler divergence: expanded code succeeded by avoiding allocation. Converted
tests accept success only against a fresh larger-limit reference, including
effects/bytes, while still requiring actual E013 to be clean. A host-produced
keeping index retains `nil_set` before `nil_out`; the 36 MiB alias witness reports
clean E013 @63..68 at O0 and O2 under a 64 MiB guard. Its small counterpart
preserves the original payload. The failed pre-conversion log is archived too.

Intrinsics remain 35. Std swap/pop remain NIL-source definitions. Their call
costs remain 6/6 and 4/4 cl100k/o200k; functional exchange 9/9, slice 10/10.

## Std/caller parity (25 rotating repetitions)

Milliseconds, min / median / max. All timed outputs checked.

| Type / operation | Part B std median | Part C std | Equivalent caller | Std/caller | Forecast <=1.10 |
|---|---:|---|---|---:|---|
| bytes swap | 23.710 | 6.129 / 6.308 / 14.315 | 6.120 / 6.316 / 19.105 | 0.999× | met |
| bytes pop | 12.901 | 6.483 / 6.906 / 14.881 | 6.425 / 7.245 / 19.290 | 0.953× | met |
| buffer swap | 23.945 | 6.300 / 6.557 / 15.260 | 6.302 / 6.554 / 19.003 | 1.001× | met |
| buffer pop | 13.369 | 7.008 / 7.496 / 14.075 | 6.879 / 7.476 / 20.236 | 1.003× | met |

## Natural cliffs and qualification (15 repetitions)

| Program | Part B natural median | Part C natural | C++ | Ratio | Tuned median |
|---|---:|---|---|---:|---:|
| balanced-binary-tree | 1492.409 | 1473.136 / 1481.530 / 1535.497 | 12.980 / 13.332 / 13.895 | 111.13× | 27.121 |
| course-schedule | 4527.249 | 4168.343 / 4315.198 / 5693.032 | 21.585 / 22.244 / 25.139 | 193.99× | 41.367 |
| last-stone-weight | 54.093 | 52.425 / 53.104 / 56.352 | 10.427 / 10.674 / 11.740 | 4.98× | 24.964 |
| spiral-matrix | 27.611 | 27.061 / 27.424 / 27.631 | 7.125 / 7.272 / 7.584 | 3.77× | 24.746 |
| validate-binary-search-tree | 1429.602 | 1369.223 / 1411.189 / 1506.524 | 12.305 / 12.697 / 14.292 | 111.14× | 23.502 |

Natural/tuned before Round 24: 19/22. Part B: 19/23. Final measured: 19/23.
Every admitted source remains unchanged and passes all correctness paths. Timing
qualification near 3× can fluctuate; source/IR changes and noise must be distinguished.
Full 29-program timings, source hashes, RSS and charge receipts are in JSON.

## Controls and RSS

Same clang/O2, whole-process warm timings, rotating 25 repetitions, run alone
after correctness and the Part B census completed. Counter binaries excluded.
Baseline is an archive of Part B `838d683`, not an earlier Round 23 binary.

| Control | Part B archive | Part C | C++ |
|---|---|---|---|
| append | 4.248 / 4.450 / 6.352 | 4.284 / 4.449 / 5.783 | 3.170 / 3.408 / 5.160 |
| scan | 7.257 / 7.427 / 7.879 | 7.242 / 7.489 / 8.043 | 9.643 / 9.887 / 10.877 |
| transform | 35.263 / 41.922 / 55.827 | 34.649 / 39.003 / 52.334 | 12.597 / 17.117 / 43.074 |
| true 16 MiB scan | 6.695 / 6.970 / 7.155 | 6.742 / 7.016 / 7.237 | 9.024 / 9.267 / 9.591 |

Historical scan is **17 MiB**; the extra explicit 16 MiB row is separate, not
a replacement that flatters the old result. Append 1 MiB, transform 16 MiB.
Transform output is byte-exact and a double transform round-trips.

| Natural cliff | NIL median RSS MiB | C++ MiB | Ratio |
|---|---:|---:|---:|
| balanced-binary-tree | 6.281 | 11.203 | 0.561 |
| course-schedule | 15.469 | 13.312 | 1.162 |
| last-stone-weight | 3.766 | 4.516 | 0.834 |
| spiral-matrix | 4.625 | 6.094 | 0.759 |
| validate-binary-search-tree | 5.500 | 8.656 | 0.635 |

## Final copy census

O0 native mechanisms joined to reference observations, strict classifications
include retention; payload-only sensitivity is retained in JSON. Do not claim
these are O2 surviving copies. Fuzz census fixtures differ from randomized Hosts.
Oversize native trace joins and resource exclusions are listed per fixture.

| Scope | Programs | Events | Bytes | Required bytes | Avoidable bytes | Resource exclusions |
|---|---:|---:|---:|---:|---:|---:|
| application | 68 | 8,034 | 157,626 | 26,078 | 131,548 | 0 |
| neetcode-natural | 29 | 3,920,307 | 400,057,040,260 | 240,000,675,731 | 160,056,364,529 | 0 |
| neetcode-tuned | 29 | 3,420,177 | 60,208,452 | 3,060,795 | 57,147,657 | 0 |
| fuzz-24411 | 773 | 5,009 | 58,755,379 | 58,723,200 | 32,179 | 49 |
| fuzz-24412 | 773 | 5,010 | 58,749,236 | 58,723,200 | 26,036 | 49 |

| Frozen scope | Round 23 B2 bytes | Part B | Final |
|---|---:|---:|---:|
| application | 157,613 | 157,626 | 157,626 |
| neetcode-natural | 400,057,333,597 | 400,057,040,260 | 400,057,040,260 |
| neetcode-tuned | 60,501,789 | 60,208,452 | 60,208,452 |

## Differential counts

All 773 indexed families per seed, including 32 chain and eight new checked-leaf
families. O0/O2 comparisons include code/span, host output, output files and input
preservation before resource classification. Either resource outcome reruns BOTH
paths with memory, reference depth and native stack scaled jointly 4×; fresh Hosts.

| Seed | Programs / builds | Escalations | Resolved matches | Persistent resources | Non-resource divergences / rule-3 failures |
|---|---|---:|---:|---:|---|
| 24411 | 773 / 1658 | 112 | 76 | 36 | 0 / 0 |
| 24412 | 773 / 1658 | 112 | 76 | 36 | 0 / 0 |

| Reference outcome | 24411 | 24412 |
|---|---:|---:|
| E008 | 18 | 18 |
| E009 | 14 | 14 |
| E012 | 40 | 40 |
| E013 | 38 | 38 |
| E014 | 16 | 16 |
| E015 | 12 | 12 |
| E016 | 15 | 15 |
| E017 | 10 | 10 |
| E018 | 11 | 11 |
| E019 | 3 | 3 |
| E020 | 6 | 6 |
| E021 | 35 | 35 |
| E022 | 3 | 3 |
| OK | 552 | 552 |

| Persistent family / direction | 24411 | 24412 |
|---|---:|---:|
| `unbounded_stack_large_record:both:reference=E008:native=E008` | 12 | 12 |
| `unbounded_stack_mutual:both:reference=E008:native=E008` | 10 | 10 |
| `unbounded_stack_mutual:reference-only:reference=E008:native=OK` | 2 | 2 |
| `unbounded_stack_sequence:both:reference=E008:native=E008` | 12 | 12 |

Source diversity: 765/765 distinct hashes; union 875, intersection 655.
Every family count and original resource/escalation direction is retained in JSON.
The old 88 E013 comparisons: ten negative-length comparisons now exact E014;
two later-operand traps now exact E012 under ADR 048; the remaining 76 resolve
at 4×. None are silently dropped. No persistent native-only E013 is accepted.

## Gate receipts

```text
./scripts/ci.sh                         579 passed; zero warnings
./scripts/ci.sh release                 579 passed; zero warnings
./scripts/sanitize.sh                   267 passed; no unexpected ASan/UBSan finding
./scripts/fuzz-v5.sh --seed 24411 --out /tmp/nil-round24-c-fuzz-24411
./scripts/fuzz-v5.sh --seed 24412 --out /tmp/nil-round24-c-fuzz-24412
                                       full coverage; 0 non-resource divergences
python3 benchmarks/corpora/application-v5/verify.py --output /tmp/nil-round24-c-corpus.json
python3 benchmarks/corpora/application-v5/verify.py --group original --output /tmp/nil-round24-c-original.json
                                       2,815 / exactly 610; frozen inputs unchanged
python3 benchmarks/corpora/neetcode150/verify.py --verified-only --jobs 1 --candidate-dir /Users/ninjacornix/NIL/benchmarks/core-generalize-study/natural --output /tmp/nil-round24-c-natural.json
python3 benchmarks/corpora/neetcode150/verify.py --verified-only --jobs 1 --output /tmp/nil-round24-c-tuned.json
                                       1,070 each; 29 programs
python3 benchmarks/core-memory-study/audit_depth.py --out /tmp/nil-round24-c-depth
python3 benchmarks/core-memory-study/audit_read_order.py --out /tmp/nil-round24-c-read --require-parity
python3 benchmarks/core-generalize-study/measure_controls.py --repeats 25 --baseline-compiler /tmp/nil-round24-c-baseline/target/release/nil --baseline-revision 838d683 --output /tmp/nil-round24-c-controls.json
python3 benchmarks/core-generalize-study/measure_controls.py --only scan --scan-bytes 16777216 --repeats 25 --baseline-compiler /tmp/nil-round24-c-baseline/target/release/nil --baseline-revision 838d683 --output /tmp/nil-round24-c-scan16.json
python3 benchmarks/core-generalize-study/measure_cohort.py --repeats 15 --output /tmp/nil-round24-c-cohort.json
python3 benchmarks/core-memory-study/measure_updates.py --repeats 25 --output /tmp/nil-round24-c-updates.json
python3 benchmarks/core-generalize-study/reference_profile.py --copies --working-tree --output /tmp/nil-round24-c-overlay
python3 benchmarks/core-generalize-study/copy_census.py --overlay /tmp/nil-round24-c-overlay --scope <scope> --native --output <receipt.json>
```

Archive: `~/.local/share/nil/round24-chains/final/`; hashes in JSON. Retained resource/failure
fuzz cases remain in the named output directories. No credentials or generated
binaries committed. All compiler/std source changes are local Conventional Commits.
Nothing pushed.

## Remaining limits

General G1/path correlation remains deferred: the BST keeping scalar observation
crosses a sequence-valued lazy region whose union retains the original. This is
outside existing replay proofs; no narrower recognizer is substituted. Record-buffer
swap/pop remains E007 pending child-edge proofs. Large/recursive/aggregate/effectful
leaf bodies are not expanded; bounded builds deliberately retain calls. This goal
does not fix all collection builders, checked update vectorization or the remaining
C++ gaps. Stack exhaustion depth is environment-dependent, not an exact promise.

## IR and audit evidence

The four measured swap/pop entry functions each had one source-callee call before
expansion and none afterwards. Bounded-mode retention and alias-copy cases are
asserted by the checked-leaf tests. Before/after IR and hashes are archived and
included in `inline_ir` in the JSON receipt. Append, scan and transform emitted
modules are byte-identical against the Part B archive (`control_ir` receipt).

Depth audit: 36/36, zero failed comparisons or native signals. I/O audit:
14 families, 168 comparisons, 72 exact and 96 ordinary-resource inconclusives,
zero diagnostic divergences. This audit retains resource-only cases rather than
claiming 168 exact results. Expanded source bodies do not change std spellings:
swap remains 6 tokens and pop 4 on cl100k/o200k; intrinsic enum remains 35.

Frozen corpus contracts, fixtures, goldens, baseline sources and NIL solutions
have no diff against the starting benchmark revision. The NeetCode verifier
only adopts resource classification and resolves candidate paths; no oracle changes.
Gate runs used the archived working-tree compiler patch before its local commits;
the tested compiler/fuzzer source is unchanged by the subsequent documentation work.
