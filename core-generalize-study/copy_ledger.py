"""Explicit storage-coverage ledger for the Part A1 copy census.

Every event kind an overlay can emit must appear in ``KINDS`` with a frozen group.
Every owning-storage site found by inspection must appear either in ``KINDS``
(instrumented) or in ``EXCLUDED`` with a reason. A trace kind missing from
``KINDS`` is an ``UNCLASSIFIED`` census failure, never silently AVOIDABLE.

Groups partition owning storage events:

``PAYLOAD_COPY``
    Duplicates an existing logical value's payload. This is the only group the
    REQUIRED/AVOIDABLE headline covers, because it is the only group a
    generalized ownership analysis could remove.
``CONSTRUCTION``
    Builds storage for a value with no pre-existing logical source, including a
    collection taking its own owned copy of a transient scratch buffer.
``INPUT_DECODE``
    Materializes a value from host input: argv, env, directory, file read.
``OUTPUT_MATERIALIZE``
    Materializes bytes for host output, formatting or record packing.
``GROWTH_RELOCATION``
    Capacity growth of an existing owning buffer. ``realloc`` may remap pages
    without copying payload, so these bytes are an upper bound, reported apart.

Relabelling a site between groups changes the published per-group totals, so a
payload copy cannot be hidden by calling it construction.
"""

PAYLOAD_COPY = 'PAYLOAD_COPY'
CONSTRUCTION = 'CONSTRUCTION'
INPUT_DECODE = 'INPUT_DECODE'
OUTPUT_MATERIALIZE = 'OUTPUT_MATERIALIZE'
GROWTH_RELOCATION = 'GROWTH_RELOCATION'

# kind -> (group, path, what the bytes measure)
KINDS = {
    # --- reference evaluator, payload duplication -------------------------
    'sequence_cow': (PAYLOAD_COPY, 'reference', 'Storage::clone element payload'),
    'concat_left': (PAYLOAD_COPY, 'reference', 'left concat source payload'),
    'concat_right': (PAYLOAD_COPY, 'reference', 'right concat source payload'),
    'append_right': (PAYLOAD_COPY, 'reference', 'appended source payload'),
    'bytes_slice': (PAYLOAD_COPY, 'reference', 'sliced byte payload'),
    'buffer_slice': (PAYLOAD_COPY, 'reference', 'sliced i64 payload'),
    'record_buffer_slice': (PAYLOAD_COPY, 'reference', 'sliced record cells'),
    'record_update': (PAYLOAD_COPY, 'reference', 'record field cells'),
    'array_update': (PAYLOAD_COPY, 'reference', 'fixed array elements'),
    'map_cow': (PAYLOAD_COPY, 'reference', 'map entries, keys, values and index'),
    'map_key_extract': (PAYLOAD_COPY, 'reference', 'key bytes materialized out of a map'),
    'map_value_extract': (PAYLOAD_COPY, 'reference', 'value bytes materialized out of a map'),
    'map_key_argument': (PAYLOAD_COPY, 'reference', 'key argument payload copied for insert/put'),
    'map_value_argument': (PAYLOAD_COPY, 'reference', 'byte value argument payload copied for insert/put'),
    # --- reference evaluator, map-owned construction ----------------------
    'map_key_own_index': (CONSTRUCTION, 'reference', 'map index takes its own key copy'),
    'map_key_own_entry': (CONSTRUCTION, 'reference', 'map entry list takes its own key copy'),
    'map_reindex_key': (CONSTRUCTION, 'reference', 'index rebuilt after sort takes own keys'),
    # --- reference evaluator, growth --------------------------------------
    'sequence_growth': (GROWTH_RELOCATION, 'reference', 'capacity before an append reserve'),
    'map_entries_growth': (GROWTH_RELOCATION, 'reference', 'entry vector capacity before a push'),
    # --- native application runtime, payload duplication ------------------
    'set': (PAYLOAD_COPY, 'native', 'replacement copy-on-write payload'),
    'slice': (PAYLOAD_COPY, 'native', 'sliced payload'),
    'sort_cow': (PAYLOAD_COPY, 'native', 'sort copy-on-write payload'),
    'map_rebuild': (PAYLOAD_COPY, 'native', 'aggregate of entry, key and value bytes re-emitted'),
    'record_get': (PAYLOAD_COPY, 'native', 'record row read out of a buffer'),
    'record_set_cow': (PAYLOAD_COPY, 'native', 'record buffer copy-on-write rows'),
    'record_set_replacement': (PAYLOAD_COPY, 'native', 'replacement row payload'),
    'record_concat_left': (PAYLOAD_COPY, 'native', 'left record concat rows'),
    'record_concat_right': (PAYLOAD_COPY, 'native', 'right record concat rows'),
    'record_append_right': (PAYLOAD_COPY, 'native', 'appended record rows'),
    'record_slice': (PAYLOAD_COPY, 'native', 'sliced record rows'),
}
# Native reuses these reference kind names for the same semantic operation.
NATIVE_SHARED_KINDS = {'concat_left', 'concat_right', 'append_right',
                       'map_key_extract', 'map_value_extract'}

# Owning-storage sites deliberately outside the census, with the reason. These
# are enumerated so a later total cannot quietly absorb them.
EXCLUDED = [
    ('reference', 'crates/nil-compiler/src/sequence.rs From<Vec>', CONSTRUCTION,
     'Fresh sequence for a constructed or decoded value; no pre-existing logical source.'),
    ('reference', 'crates/nil-compiler/src/evaluator.rs Operation::Bytes/Array/Repeat', CONSTRUCTION,
     'Literal materialization from HIR, not from a runtime value version.'),
    ('reference', 'crates/nil-compiler/src/application.rs buffer/bytes/map constructors', CONSTRUCTION,
     'Constructor fill; the only source is a scalar fill value.'),
    ('reference', 'crates/nil-compiler/src/keyed.rs empty/empty_record', CONSTRUCTION,
     'Zero-length entry and index allocation; no payload bytes.'),
    ('reference', 'crates/nil-compiler/src/evaluator.rs argv decode', INPUT_DECODE,
     'Host argument vector decoded once before execution begins.'),
    ('reference', 'crates/nil-compiler/src/application.rs Host env/directory/read', INPUT_DECODE,
     'Host input materialization; the source is outside the program semantics.'),
    ('reference', 'crates/nil-compiler/src/application.rs ParseBuffer values', INPUT_DECODE,
     'Decoded i64 vector built from text; separate logical value.'),
    ('reference', 'crates/nil-compiler/src/records.rs unpack', INPUT_DECODE,
     'Reconstructs a record from packed map bytes; the map copy itself is counted.'),
    ('reference', 'crates/nil-compiler/src/application.rs Intrinsic::Format', OUTPUT_MATERIALIZE,
     'Formats a scalar into fresh bytes; no sequence payload is duplicated.'),
    ('reference', 'crates/nil-compiler/src/numeric.rs format/format_float', OUTPUT_MATERIALIZE,
     'Scalar to text; reached only through Format.'),
    ('reference', 'crates/nil-compiler/src/records.rs pack', OUTPUT_MATERIALIZE,
     'Packs record cells for map storage; its observation is recorded so the map copy classifies.'),
    ('reference', 'crates/nil-compiler/src/keyed.rs render', OUTPUT_MATERIALIZE,
     'Tooling-only rendering, unreachable from program semantics.'),
    ('reference', 'crates/nil-compiler/src/evaluator.rs frame/branch/loop value clones', CONSTRUCTION,
     'Clones Value handles. Sequence, map and record handles are Arc pointers, so no payload moves; '
     'any payload duplication appears at the Storage::clone hook instead.'),
    ('native', 'crates/nil-llvm/src/application.c nil_literal (226-228)', CONSTRUCTION,
     'Shared literal allocator. Its payload-copying callers at 511 and 516 are hooked individually; '
     'the construction and env/format callers are excluded here.'),
    ('native', 'crates/nil-llvm/src/application.c nil_read/nil_parsebuf/nil_directory', INPUT_DECODE,
     'Host input materialization; the source lies outside the program semantics.'),
    ('native', 'crates/nil-llvm/src/application.c scalar-record pack (609)', OUTPUT_MATERIALIZE,
     'Packs a record into map bytes; the enclosing map update is counted.'),
    ('native', 'crates/nil-llvm/src/application.c constructor fills (201,203,687)', CONSTRUCTION,
     'Buffer and record-buffer fill loops; no pre-existing logical source.'),
    ('native', 'crates/nil-llvm/src/application.c realloc growth (316,738)', GROWTH_RELOCATION,
     'Unique-path capacity growth. realloc can remap without copying, so a byte count here would '
     'be an invented memcpy; reported as uninstrumented rather than estimated.'),
    ('native', 'crates/nil-llvm/src/runtime.rs F64 print (198)', OUTPUT_MATERIALIZE,
     'Eight-byte scalar move for printing.'),
    ('native', 'crates/nil-llvm/src/application.c map_rebuild per-entry memcpy (541,545)', PAYLOAD_COPY,
     'Covered by the map_rebuild aggregate at 537, which sums entry, key and value bytes. Not a '
     'separate total: adding per-memcpy hooks would double count the same bytes.'),
]

def group(kind):
    """Frozen group for a trace kind. Unknown kinds are a census failure."""
    if kind not in KINDS:
        raise KeyError(f'UNCLASSIFIED copy kind {kind!r}: extend copy_ledger.KINDS')
    return KINDS[kind][0]

def groups():
    return (PAYLOAD_COPY, CONSTRUCTION, INPUT_DECODE, OUTPUT_MATERIALIZE, GROWTH_RELOCATION)

def receipt():
    return {
        'schema': 1,
        'kinds': {k: {'group': g, 'path': p, 'bytes_measure': m} for k, (g, p, m) in KINDS.items()},
        'native_shared_kinds': sorted(NATIVE_SHARED_KINDS),
        'excluded': [{'path': p, 'site': s, 'group': g, 'reason': r} for p, s, g, r in EXCLUDED],
        'headline_group': PAYLOAD_COPY,
        'note': 'REQUIRED/AVOIDABLE is published for PAYLOAD_COPY. Other groups are reported per '
                'group and never folded into that headline. AVOIDABLE means no later reference '
                'observation of the source version under the stated metric, not a proof that the '
                'copy is removable.',
    }
