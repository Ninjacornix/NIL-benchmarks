# Round 18 map controls — preregistration

Before measurement, fixed matrix: insert, lookup hit, lookup miss, iterate and
existing-key update; binary 8-byte and 64-byte keys; 10k, 100k and 250k entries.
Compare NIL with the same Clang O2 C++ std::unordered_map and an insertion-ordered
dense-entry/linear-probing map using FNV-1a and <=0.5 load. No production map
redesign. Keys encode unique little-endian indices, deterministic padding; misses
flip the high index bit. All outputs have independent integer checksums.

NIL has no clock operation, so whole-process wall time is measured identically for
all runners. Insert reports total/N including key file read/startup. Other operations
run three full passes after construction; subtract a paired construction control
and divide by 3N. Report raw whole-process min/median/max too. Marginal ns is an
estimate, can be noisy/negative, and is not an isolated kernel measurement. C++
borrows views for queries; NIL slices copy keys. This difference must be disclosed,
not attributed entirely to hash/probing. No reserve on insertion baselines.

Forecasts (judgments, not results): NIL insert 0.5–5 microseconds/entry, short keys;
64-byte keys 1.5–4x short-key cost. Lookup 100–1500 ns/query including temporary key
allocation, iteration 50–1500 ns/entry, same-size update 0.2–4 microseconds. NIL
may trail C++ by 2–15x. Report every miss; no density/performance target.

**250k long keys likely fail E013**: rounded entry/key capacities approach a
33.55 MiB map, and original+prospective-copy reservations already exceed 64 MiB
before retained input or temporary keys. Do not increase the quota or trim this
matrix. Report trapped rows as unsupported at that size; C++ still measured.
Alias-free updates reuse only when capacity/value lengths are unchanged. Capacity
growth copies/rehashes; exact-live aliases intentionally copy.

Report deterministic FNV bytes processed and ordered-table probe counts in a
separate untimed diagnostic run if practical. A faster hash/Swiss-table index is
only a recommendation, based on long-key cost/probing and constraints on stable
order, deterministic hash and live-capacity quota. No third-party Rust dependency.

Implementation clarification before running: C++ hit/miss queries materialize
strings, matching NIL's copying slice more closely than the initially proposed
views (short strings may use C++ SSO). Ordered updates still use views. Both
baselines bulk-read the same key file. Probe counters and hash-only timings run
in a separate instrumented C++ binary, not the timed baseline. This is harness
construction before any results, not outcome-driven adjustment.
