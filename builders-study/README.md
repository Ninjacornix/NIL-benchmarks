# Builder (filter) diagnosis, Round 17

Variants isolating the conditional-builder cost behind ADR 038. `v*` keep even bytes,
`w*` keep bytes < 128 (both 50% of a 16 MiB 0..255 cycle). Each run checks output
against a Python-computed expectation.

    cd benchmarks/builders-study
    python3 -c "open('input.bin','wb').write(bytes(range(256))*65536)"
    ../paired/.venv/bin/python bench.py v1_hand v2_helper v3_std w1_inline_once w2_helper_once w3_inline_twice

Findings before ADR 038 (overseer machine, median of 12): v1 536, v2 273, v3 273,
w1 537, w2 538, w3 538 ms. Every `a<128` shape costs the same; the fast even-byte helper
result is a layout-sensitive LLVM optimisation. Reducing root stores to plain stores
(unsafe experiment, reverted) gave ~70 ms; inlining the one-element concat store gave
409 ms on w1. `input.bin` is generated, not committed.
