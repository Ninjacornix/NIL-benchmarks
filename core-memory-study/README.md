# Round 23: memory-model admission audit

This is the permanent **14-family parity regression gate** for the 2026-10-08
ADR 033/045 fail-fast amendment. A successful prefix beyond available payload must
produce E013 before a later E015. Earlier faults, dead allocations and unselected
arms remain controls. Historical Round 23 results recorded seven conflicting
families; those are retained in the earlier report, not accepted expectations.

All sources/fixtures here are originally authored and covered by this repository's
MIT license. No frozen corpus inputs, solutions or compiler sources are edited.

## Reproduce

From the parent NIL repository on macOS, with Rust/Clang installed:

```sh
cargo build --release --locked --offline -p nil -p nil-compiler -p nil-hir
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s benchmarks/core-memory-study -p 'test_*.py' -v
python3 benchmarks/core-memory-study/audit_read_order.py \
  --out /tmp/nil-round23-admission --repeats 3 --require-parity
```

The last command exits **1** when parity is violated. Every admission gate must
use `--require-parity`; successful runs report PARITY. Unexpected diagnostics, crashes, wrong spans, stdout or fault traces
fail in either mode. Rerun in a fresh output directory for independently archived
artifacts; results and executables stay outside git.

## Fault model and limits

`tools/nil-fuzz/fixtures/read_fault.c` in the parent repository is the shared
test-only interposer. This full audit exercises its Darwin path. It reads an ordinary, authored
4 KiB file and makes the next read at a specified byte offset return EIO. The
same fault position applies to Rust `File::read` and C `fread`; the latter is also
interposed because Darwin's internal libc read calls cannot be overridden by
interposing the public `read` alone. The fixture uses unbuffered, size-one reads;
its private FILE error/EOF flags are supplied by the Darwin headers. Other Rust
reads use the ordinary kernel read syscall. No compiler/runtime code is patched.
No fault library is linked into a production NIL executable.

This measures permitted partial-read failure behavior under deterministic fault
injection. It does **not** claim a hardware/disk failure was observed, does not
measure speed, and does not claim portability to Linux. Controls check successful
real-file reads without interposition, faults before quota, faults without live
quota pressure, dead allocations and unselected lazy arms. Every injected run
records bytes transferred and EIO returns: native can reject the prefix before
requesting the failing read. The reference uses the actual `FileHost`, not a
substitute in-memory Host or a simulated compiler result.

The matrix includes Bytes, Buffer, record-child, callee and selected-lazy retention.
Both bounded/unbounded native modes at O0/O2 are compared to the reference at the
same source/fixture/fault. The normal v5 generator also covers fourteen acquisition-fault families with
real native interposition and a prefix-failing in-memory reference Host. The audit
additionally exercises the actual reference FileHost and bounded/unbounded builds.

`report.json` contains commands, source/binary hashes, codes/spans, output bytes,
fault receipts and a raw artifact manifest. Native semantic failures are expected
here; an infrastructure failure is never counted as a language diagnostic.
