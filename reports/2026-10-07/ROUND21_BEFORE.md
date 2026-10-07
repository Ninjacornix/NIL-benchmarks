# Round 21: frozen-source qualification and memory before changes

**Natural qualification is 19/150; tuned qualification is 22/150.** Performance rewrites account for all three additional qualifications. All 29 admitted natural sources pass the same 1,070 correctness checks; the 114 unattempted problems remain held out. No compiler changes have been made.

Natural sources are byte-exact from benchmarks `6fd268d`. Fifteen rotating warm repetitions per arm, one excluded warmup, largest unchanged fixture per problem; three separate macOS `/usr/bin/time -l` runs supply RSS. C++ uses the existing same-algorithm source and the same Clang O2. Every run checks output and input bytes. Raw logs remain under `/tmp/nil-round21/`; adjacent JSON retains samples, source hashes and machine/compiler metadata.

| Problem | Natural min/median/max ms | Natural/C++ | Tuned/C++ | Natural RSS MiB / C++ ratio | Live / reservation % of 64 MiB |
|---|---:|---:|---:|---:|---:|
| 3sum | 832.630/853.768/895.606 | 7.81 | 7.80 | 18.47 / 0.16 | 40.66/81.29 |
| balanced-binary-tree | 1526.559/1570.207/2588.600 | 107.64 | 1.94 | 7.69 / 0.69 | 7.15/7.15 |
| best-time-to-buy-and-sell-stock-with-cooldown | 8.904/9.300/9.614 | 1.84 | 1.80 | 2.77 / 0.87 | 1.19/1.77 |
| car-fleet | 18.359/18.824/19.334 | 0.82 | 0.82 | 4.00 / 0.50 | 3.58/4.77 |
| coin-change | 3.862/4.101/4.533 | 1.44 | 1.44 | 2.38 / 0.99 | 1.19/2.38 |
| contains-duplicate | 9.988/10.297/10.753 | 1.57 | 1.56 | 3.14 / 0.81 | 1.30/2.14 |
| course-schedule | 7217.616/7482.260/7844.882 | 327.59 | 1.86 | 16.95 / 1.27 | 15.50/15.50 |
| gas-station | 13.310/13.596/13.974 | 2.22 | 2.21 | 3.72 / 0.82 | 2.38/3.25 |
| generate-parentheses | 26.524/26.592/26.859 | 8.11 | 8.12 | 3.00 / 1.26 | 0.91/1.82 |
| insert-interval | 43.838/44.102/45.034 | 2.53 | 2.54 | 5.39 / 0.35 | 3.95/5.51 |
| kth-largest-element-in-an-array | 13.403/13.508/13.668 | 1.62 | 1.62 | 3.88 / 0.99 | 2.38/3.58 |
| last-stone-weight | 26577.202/26904.111/29021.458 | 2155.55 | 157.85 | 6.83 / 1.51 | 4.77/7.15 |
| letter-combinations-of-a-phone-number | 224.716/225.524/227.305 | 36.14 | 31.25 | 2.78 / 0.66 | 1.95/3.91 |
| longest-repeating-character-replacement | 11.227/11.840/12.189 | 3.13 | 3.12 | 1.88 / 0.96 | 0.15/0.30 |
| longest-substring-without-repeating-characters | 8.398/8.883/9.570 | 2.39 | 2.35 | 1.73 / 0.89 | 0.16/0.16 |
| maximum-subarray | 9.962/10.295/10.843 | 1.59 | 1.57 | 2.80 / 0.77 | 1.19/1.85 |
| median-of-two-sorted-arrays | 10.093/10.599/11.028 | 1.53 | 1.52 | 3.50 / 0.89 | 1.79/2.38 |
| meeting-rooms | 21.553/22.281/23.610 | 0.88 | 0.87 | 5.19 / 0.62 | 3.58/4.77 |
| min-cost-climbing-stairs | 8.946/9.691/9.998 | 1.70 | 1.68 | 2.77 / 0.87 | 1.19/1.77 |
| plus-one | 23.671/24.166/24.884 | 3.77 | 3.78 | 3.45 / 0.86 | 3.58/3.58 |
| reverse-integer | 30.161/30.757/31.168 | 2.31 | 2.29 | 3.95 / 0.53 | 3.15/5.10 |
| reverse-linked-list | 32.910/33.246/33.855 | 2.64 | 2.64 | 4.14 / 0.50 | 3.58/4.77 |
| search-in-rotated-sorted-array | 9.352/9.764/10.451 | 1.53 | 1.55 | 2.95 / 0.79 | 1.19/2.07 |
| single-number | 13.262/13.808/14.101 | 2.06 | 1.50 | 2.95 / 0.79 | 1.19/2.05 |
| spiral-matrix | 1414.429/1422.327/1592.862 | 158.81 | 3.04 | 6.11 / 1.00 | 4.76/4.76 |
| target-sum | 3.275/3.629/4.580 | 1.08 | 1.08 | 1.62 / 0.98 | 0.03/0.04 |
| valid-palindrome | 2.845/3.467/4.766 | 0.89 | 0.88 | 1.72 / 0.83 | 0.15/0.15 |
| valid-sudoku | 2.821/3.392/4.149 | 0.97 | 1.02 | 1.59 / 0.99 | 0.00/0.00 |
| validate-binary-search-tree | 1448.781/1467.230/1490.962 | 103.48 | 1.78 | 6.23 / 0.72 | 5.96/5.96 |

## Historical controls

| Workload | NIL min/median/max ms | C++ min/median/max ms | NIL/C++ | RSS NIL/C++ MiB | Live/reservation MiB |
|---|---:|---:|---:|---:|---:|
| append | 4.862/5.589/11.056 | 3.868/4.472/7.511 | 1.25 | 2.67/3.59 | 1.000/2.000 |
| scan | 8.104/8.792/9.426 | 10.779/11.526/12.184 | 0.76 | 18.61/18.61 | 17.000/17.000 |
| transform | 37.569/39.495/160.524 | 14.924/18.527/29.825 | 2.13 | 17.61/17.62 | 16.000/32.000 |

Twenty-five rotating warm repetitions; three separate RSS runs. The scan uses the exact historical fixture: `alpha,beta,gamma\n` is 17 bytes, making the input **17 MiB**, despite earlier 16 MiB labels. Append builds 1 MiB; transform processes 16 MiB. Transform output is byte-exact and double-transform round-trips. Its 39.49 ms median exceeds Round 20’s 36.04 ms by 9.6%; this unfavourable before measurement is retained, not declared noise. The 160.52 ms outlier is also retained. C++ transform is the existing application/transform.cpp baseline; older controls.cpp timings are not an identical baseline.

## What memory means

Live capacity is sampled by the reference evaluator after instruction-boundary liveness pruning. Prospective quota reservation is separately sampled at successful admission checks and includes reserve-as-if-copy. Neither is RSS, allocator overhead or a continuous physical-allocation peak. The isolated overlay manifest and patch hashes are recorded in JSON. Native root-charge telemetry is separately retained and **must not be treated as semantic liveness**: rootless scans keep the input alive without root bookkeeping (the native counter reports only 126 bytes there). These programs have no allocating observation after the input becomes rootless.

The worst reference reservation is 3sum at 81.29% of the current quota; its live charge is 40.66%. This distinguishes quota headroom from process RSS. No limit/default decision is inferred from RSS alone.

## Reproduction and remaining work

See `core-generalize-study/README.md` for commands. Natural verification: `TOTALS {"tasks":29,"verified_nil":29,"checks":1070,"passed_checks":1070}`. Kernel attribution tests: six passed, with exact cl100k/o200k sums.

These are Parts A2/A3 measurements, **not a completed Round 21**. The physical-copy census, C/D forecasts, ADR 043, ownership/copy hints, configurable limits and post-change gates remain outstanding. No implementation forecast or ownership success is claimed.
