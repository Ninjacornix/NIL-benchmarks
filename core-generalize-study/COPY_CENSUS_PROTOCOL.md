# Copy census: observation and physical storage are separate

Part A1 remains incomplete until both reference and native storage events have
been classified against future **reference-semantic** observations. Do not use
root counts or a pointer-only memcpy trace as a substitute.

## Frozen definitions

- Count owning buffer, record and map storage reconstructions, including COW,
  slice/concat source payloads and map rebuilds. Record construction, input
  decoding, output materialization and growth relocation are separately grouped;
  they must not disappear from a total by changing the group labels.
- A copy is `REQUIRED` under the requested metric if the source's **logical
  version** is observed at a later semantic instruction; otherwise `AVOIDABLE`.
  This label is not a theorem that the physical copy is indispensable. Scheduling
  reads or deferring writes can remove copies in the REQUIRED group too.
- Distinguish payload observations from metadata-only observations. Publish the
  strict "any later observation" result and the payload-only sensitivity result.
  Passing, returning or storing an alias propagates its version; it does not
  itself read payload. The actual caller/host/result sink records observation.
- Assign monotonically increasing version IDs at construction and functional
  update, independent of addresses. Addresses may be reused after collection,
  and in-place updates reuse an address for a different logical version. Never
  serialize pointer addresses into reports.
- Track record children and map values, including a child held through a parent,
  calls, returns, loop state and selected lazy arms. Unselected arms generate no
  events. Effects and traps retain their original order.
- Join native physical events to the corresponding semantic operation/version.
  Keep the compiler's ownership and rooting proofs intact in measurement builds;
  classify from a reference trace, not from native root-count heuristics.
- Growth relocation is distinct from immutable-value copying. `realloc` can move
  virtual mappings without copying physical payload. Report explicit moves and
  uncertain relocation bytes separately instead of inventing a memcpy count.
- Report representation differences: Rust record `Value` cells and native packed
  slots have different physical widths. Count actual representation bytes per
  path, not a shared width chosen to make them look comparable.

## Integrity checks before accepting results

The instrumented and ordinary paths must agree on returned values, byte output,
stdout, input preservation and diagnostic code/span. Assert every counted event
has a source version and a known category; `UNCLASSIFIED` is a failed census,
not silently AVOIDABLE. Native telemetry inserted before optimization must also
account for copies that LLVM eliminates; a forced tracing memcpy must not be
presented as an original physical copy.

Minimal tracker tests include: observed old value after an update; dead old
value; returned alias; record child; lazy selected/unselected arms; pointer reuse;
in-place version change; read snapshots; and host observations. In particular,
a late read of an old snapshot must not be attributed to the newer version that
now occupies the same address.

Scope: all 68 application programs, admitted natural and tuned NeetCode cohorts,
and every full-family generated program from two seeds. Fixtures and semantic
oracles stay unchanged. Compiler sources stay untouched: instrumentation must be
an isolated, hashed overlay or a temporary generated-runtime transformation.

## Current tools

`reference_profile.py` measures liveness/reservations, **not copies**. The native
`measure_clang.py` measures observed root charge, **not semantic liveness**:
rootless nonallocating scans keep data alive without maintaining an arena root.
The measurements demonstrated this on the historical 17 MiB newline fixture.
Neither is a completed physical-copy census.
