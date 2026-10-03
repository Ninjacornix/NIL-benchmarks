# Keyed-value scaling

Run from the NIL workspace, after initializing the benchmark submodule:

```sh
benchmarks/paired/.venv/bin/python benchmarks/application/keyed/run.py \
  --output /tmp/nil-keyed-scaling --repeats 9
```

The existing compiler's expr-v5 O2 driver compiles two checked programs. `insert`
builds a byte-keyed integer map using canonical decimal keys and returns its size.
It includes formatting, hashing, geometric growth, root tracking and process
startup. `repack` grows one owned byte-string map value by one byte on each update;
it intentionally measures the disclosed different-length replacement cost.
`repack-held` alternates a one/two-byte value for 1,000 updates with an unrelated
4 KiB/64 KiB/1 MiB value retained in the map. This exposes whole-map repacking
without constructing a large replacement argument on each iteration.
One warmup is excluded; every sample verifies the exact scalar output. No CPU
isolation, timer subtraction or input reuse trick. The script also probes four
entry-count boundaries; these do not establish a universal maximum for maps with
other key/value lengths or extra live roots. Sources and measurement script are
MIT licensed under the benchmark repository's LICENSE.
