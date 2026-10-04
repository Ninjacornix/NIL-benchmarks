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
checks row contents rather than merely the container length. Dynamic-child shapes
include byte literals in each iteration; their allocation/root cost is part of the workload.
