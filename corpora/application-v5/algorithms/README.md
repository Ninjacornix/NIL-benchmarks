# ADR 030 algorithm cohort

Four tasks derive their algorithm intent from pinned MIT TheAlgorithms/Python sources.
Each manifest entry records source revision/hash, rationale and adaptations. Task wording,
text I/O protocols, fixtures, oracles and solutions are original MIT contributions; retained
upstream license/attribution is in UPSTREAM_LICENSE. No upstream solution is copied.

The cohort was frozen before writing solutions or seeing token counts. Oracles run independently
of NIL storage; BST uses sorted multisets, interval merge uses endpoint sweep. These are native
structured-representation demonstrations, not a claim the algorithms were uncomputable with
flat integer encodings before ADR 030. The existing 75 tasks/oracles/goldens remain frozen.
Density must report these four separately, as well as the unchanged original and external cuts.

Supplement frozen fixtures with deterministic valid-domain randomized checks:
`paired/.venv/bin/python corpora/application-v5/algorithms/check_random.py --seed 30030 --cases 30 --output /tmp/nil-algorithm-random.json`.
This checks all three languages and both native NIL optimization levels, independently
of the density selection. It does not replace or edit frozen tasks/goldens.
