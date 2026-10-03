# Keyed-data follow-up on frozen external properties

Contracts, oracles, goldens and existing Python/C++ references are locked to
`6f735cc` by KEYED_LOCK.json. SUPPORT.json overrides status only; it does not
change wording, fixtures or expected values. The original 24 NIL references also
remain locked. No unknown fixture is accepted by the finite upstream oracle.

| Task | Attempt / disposition |
| --- | --- |
| ETL | Implemented an owned byte-keyed integer map of lowercase letters to scores; parsed the frozen compact JSON score/letter transport and emitted sorted-key compact JSON. All three languages pass all four checks each (golden included), and NIL also passes eight native O0/O2 checks. This is a Latin-letter score adapter, not a general JSON parser. |
| grade_school | Replaced duplicate-mask construction and repeated old-name searches with an insertion-ordered name/grade map while retaining the offset buffer and existing ordering comparator. Same input/output contract and baseline sources. Sorting still scans candidates; maps do not eliminate that cost. |
| alphametics | Examined the nine distinct retained puzzles and assignment/null outputs. m can represent an assignment, but a verified column/carry solver and compact JSON adapter are not implemented. Search needs bounded pruning rather than a fixture lookup or unmeasured brute-force claim. Still unsupported. |
| Forth | Examined first-property instruction streams, runtime definitions, redefinitions and error outputs. t can store case-normalized word bodies, but captured definition meanings, tokenization, stack interpretation and error serialization need a verified adapter. No fixture-specialized dictionary is substituted. Still unsupported. |
| camicia | Examined simulateGame deck/state and cycle outputs. m can store encoded visited states; canonical deck-state encoding and simulation are not implemented, and nested typed deck values remain absent. Still unsupported. |
| dot_dsl | The first-property result nests node, edge and attribute maps; map-valued entries remain outside this minimal homogeneous design. A serialized graph parser could emulate them but is not supplied or claimed verified. Still unsupported. |
| go_counting | The owner plus coordinate-pair collection is a product, not merely byte-key membership. The flood-fill/serialized result adapter is not implemented; typed records/product values remain absent. Still unsupported. |

Only ETL changes support status: 32 supported external / 18 unsupported external,
56 verified NIL programs / 19 unsupported overall. The five remaining adjacent
cases are retained; map availability must not be confused with completed algorithms.
Unsupported is a corpus verification status, not a theoretical impossibility proof.
Byte-valued maps support nesting a sequence, not arbitrary nested containers.
