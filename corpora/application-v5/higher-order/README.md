# Static higher-order corpus addition

`programs/ex_accumulate.{nil,py,cpp}` implement the unchanged Exercism accumulate
contract and five selected canonical fixtures, including the held-out nested
accumulate with a captured prefix. Provenance/licence remain in the frozen
external manifest and canonical JSON (Exercism MIT); newly authored solutions
are covered by this corpus's MIT licence. No existing program, baseline, task,
fixture, oracle or golden is rewritten.

The fixture adapter translates the canonical pseudocode strings to statically
known callables; it does not implement arbitrary runtime source evaluation. NIL
uses separate typed numeric and Text-record HOFs; nested accumulation passes the
captured prefix as an explicit Text argument. ASCII conversion and the restricted
unescaped-string JSON adapter suffice for the frozen fixtures; this is not a
Unicode/JSON library claim. The other three languages' arbitrary execution and
collection features are not being added to NIL by this reference.

Run `verify.py --task ex_accumulate --output /tmp/accumulate.json`: five reference,
ten native O0/O2 and five checks in each baseline, 25 total. `--group all` includes
it; `--group original` intentionally preserves the historical 610-check cohort
(24 old supported NIL solutions and the original 25 Python/C++ baselines).
New environment and accumulate NIL checks are in the full run. This group
clarification changes the verifier selection, never the oracle or expected value.

`ex_reactive` is absent from the frozen manifest. `ex_hangman` remains unsupported:
its reactive-integration requirement is not established by statically known
callback arguments or a sequential transcript. No task is removed or substituted.
