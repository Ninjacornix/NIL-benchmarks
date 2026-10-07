"""The coverage ledger must stay exactly in step with what the overlays emit."""
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import copy_ledger
import copy_overlay
import native_copy_overlay

REFERENCE_CALL = r'copy_trace::copied\(.*?"([a-z_0-9]+)"'
NATIVE_CALL = r'nil_measure_copy\(.*?"([a-z_0-9]+)"'


def emitted(name, pattern):
    """Every kind literal the named overlay can pass to its trace hook."""
    return set(re.findall(pattern, (HERE / name).read_text()))


def reference_kinds():
    return emitted('copy_overlay.py', REFERENCE_CALL)


def native_kinds():
    return emitted('native_copy_overlay.py', NATIVE_CALL)


class CoverageLedger(unittest.TestCase):
    def test_reference_overlay_kinds_are_all_in_the_ledger(self):
        kinds = reference_kinds()
        self.assertGreaterEqual(len(kinds), 19)
        self.assertEqual(kinds - set(copy_ledger.KINDS), set())

    def test_native_overlay_kinds_are_all_in_the_ledger(self):
        kinds = native_kinds()
        self.assertGreaterEqual(len(kinds), 16)
        self.assertEqual(kinds - set(copy_ledger.KINDS), set())

    def test_every_declared_kind_is_actually_emitted(self):
        """A ledger entry with no hook would overstate coverage."""
        self.assertEqual(set(copy_ledger.KINDS) - (reference_kinds() | native_kinds()), set())

    def test_native_shared_kinds_appear_on_both_paths(self):
        self.assertEqual(copy_ledger.NATIVE_SHARED_KINDS, reference_kinds() & native_kinds())

    def test_groups_are_frozen_and_complete(self):
        for kind, (group, path, measure) in copy_ledger.KINDS.items():
            self.assertIn(group, copy_ledger.groups(), kind)
            self.assertIn(path, ('reference', 'native'), kind)
            self.assertTrue(measure, kind)

    def test_payload_copy_group_is_not_empty_on_either_path(self):
        for path in ('reference', 'native'):
            found = [k for k, (g, p, _) in copy_ledger.KINDS.items()
                     if g == copy_ledger.PAYLOAD_COPY and p == path]
            self.assertTrue(found, path)

    def test_unknown_kind_is_a_census_failure_not_avoidable(self):
        with self.assertRaises(KeyError):
            copy_ledger.group('not_a_real_kind')

    def test_excluded_sites_each_carry_a_group_and_a_reason(self):
        self.assertGreaterEqual(len(copy_ledger.EXCLUDED), 15)
        for path, site, group, reason in copy_ledger.EXCLUDED:
            self.assertIn(path, ('reference', 'native'), site)
            self.assertIn(group, copy_ledger.groups(), site)
            self.assertGreater(len(reason), 30, site)

    def test_headline_group_is_payload_copy_only(self):
        receipt = copy_ledger.receipt()
        self.assertEqual(receipt['headline_group'], copy_ledger.PAYLOAD_COPY)
        self.assertIn('not a proof that the', receipt['note'])
        self.assertEqual(set(receipt['kinds']), set(copy_ledger.KINDS))

    def test_every_dynamic_constructor_registers_a_new_storage_version(self):
        import tempfile
        root = HERE.parents[1]
        with tempfile.TemporaryDirectory() as directory:
            shadow = Path(directory)
            for name in ['lib', 'sequence', 'evaluator', 'application', 'keyed', 'records']:
                relative = Path('crates/nil-compiler/src') / (name + '.rs')
                target = shadow / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((root / relative).read_bytes())
            copy_overlay.patch(shadow)
            sequence = (shadow / 'crates/nil-compiler/src/sequence.rs').read_text()
            keyed = (shadow / 'crates/nil-compiler/src/keyed.rs').read_text()
            records = (shadow / 'crates/nil-compiler/src/records.rs').read_text()
            self.assertEqual(sequence.count('copy_trace::fresh(value.identity())'), 2)
            self.assertEqual(keyed.count('copy_trace::fresh(value.identity())'), 1)
            self.assertIn('let value = unpack_value(ty,records,bytes)', records)
            self.assertIn('Value::Array(fields) => crate::copy_trace::fresh', records)

    def test_overlays_patch_a_shadow_checkout_not_the_repository(self):
        for module in (copy_overlay, native_copy_overlay):
            source = Path(module.__file__).read_text()
            self.assertNotIn("/Users", source)
            self.assertIn('shadow', source)


if __name__ == '__main__':
    unittest.main()
