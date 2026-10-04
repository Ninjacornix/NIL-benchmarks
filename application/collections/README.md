# Record-buffer scaling

Run `paired/.venv/bin/python application/collections/run.py --repeats 25 --output /tmp/nil-record-scaling`
from the benchmark checkout. O2 native whole-process timings include startup;
one warmup is discarded, all outputs checked, raw samples and source hashes retained.
No CPU isolation. No reference-evaluator speed or cross-language performance claim.
Scalar builders/replacements, dynamic-child builders/replacements and deliberately
live aliases are separated. The latter two expose conservative transitive-root/copy
costs instead of claiming every nested pattern is linear. Boundary probes use
16-byte scalar rows and the unchanged 64 MiB live-capacity limit.

Timed builders and replacements finish with an all-row checksum, so verification
checks row contents rather than merely the container length. The nested builder
includes a byte literal in each iteration; nested replacement reuses the existing
child, separating allocation from conservative root-transfer costs. Nested builders and
aliased curves stop at 16k to measure their quadratic cost explicitly. The
nonallocating nested update continues through 1 Mi rows; it reuses one child.

`--workload nested-build-shared` isolates growth with one shared child allocation
from `nested-build`, which creates one live byte allocation per record. This
control separates increasing live-arena traversal costs from collection length
alone. Both preserve immutable child aliases; no lifetime proof is relaxed.

The shared-child control also proved quadratic at 1k/4k, so its final range stops
at 16k like the fresh-child shape. An initial oversized 64k/256k control was
stopped after this evidence; this changes timing practicality, not the reuse or
lifetime proof. Report both the root-transfer cost and live-arena traversal cost.
