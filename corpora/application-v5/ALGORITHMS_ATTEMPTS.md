# Algorithmic-operation review of unsupported tasks

Sorting/each shorten eleven supported external references; none of the retained
unsupported contracts becomes implemented merely by these operations. No fixture
lookup replaces an algorithm. All contracts, fixtures and expected outputs remain
frozen. This is an evidence/adapter review, not a claim of theoretical impossibility.

| Retained task | Still required |
|---|---|
| env_lookup | Environment host access remains absent. |
| ex_accumulate | User function selection/higher-order adapter remains absent. |
| ex_alphametics | Bounded column/carry search and structured assignment/null serialization; sort is not a constraint solver. |
| ex_anagram | Byte sorting is available, but retained Greek/case-folding fixtures require Unicode handling. A byte-only anagram prototype would not pass the unchanged contract. |
| ex_armstrong_numbers | Retained integer domain exceeds signed i64; sorting does not change numeric range. |
| ex_bank_account | Concurrent stateful lifecycle semantics. |
| ex_binary_search_tree | Recursive node-valued result/serialization adapter. |
| ex_bob | Unicode letter/case classification; byte membership and ordering cannot substitute. |
| ex_camicia | Verified nested deck encoding, cycle detection and simulation adapter; sort would destroy deck order. |
| ex_complex_numbers | Floating-point arithmetic and structured complex result. |
| ex_darts | Floating-point coordinates/distance. |
| ex_diffie_hellman | Entropy/domain adapter; sorting is unrelated. |
| ex_dot_dsl | Nested graph/node/edge attribute representation and parser/serialization adapter. |
| ex_forth | Verified stack interpreter, definitions and JSON instruction adapter; ordered dictionaries alone do not supply it. |
| ex_gigasecond | Calendar/date-time representation and verified adapter. |
| ex_go_counting | Flood-fill plus owner/coordinate-pair product and serialization; each is a full collection scan, not region traversal. |
| ex_grains | Unsigned 64-bit/total domain exceeds signed i64. |
| ex_grep | The frozen multiple-file fixture contract requires a multi-file adapter. |
| ex_hangman | Reactive state transition/lifecycle adapter. |

No unsupported task was newly delivered: 18 external plus one original = **19**.
There are 32 external and 24 original verified NIL solutions. Future adapters may
encode some structures manually; support requires passing the frozen oracle, not
just being theoretically expressible. Classification and standalone comparison
were rejected this round on the preregistered ranking; neither is silently added.
