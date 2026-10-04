"""Provenance, retention, fixture integrity and unchanged original comparison."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from external_suite import load_tasks, load_goldens, external_expected

class ExternalContracts(unittest.TestCase):
    def test_external_selection_is_frozen_and_all_tasks_are_retained(self):
        selection = json.loads((HERE / 'external/selection.json').read_text())
        records = selection['records']
        self.assertEqual(len(records), 50)
        self.assertEqual([r['slug'] for r in records], sorted(r['slug'] for r in records))
        tasks = [t for t in load_tasks('external') if not t['id'].startswith('ex_algo_')]
        self.assertEqual({t['id'] for t in tasks}, {r['id'] for r in records})
        self.assertEqual(len(load_tasks()), 79)
        for record in records:
            raw = (HERE / 'external' / (record['slug'] + '.json')).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), record['canonical_sha256'])
            self.assertEqual(record['license'], 'MIT')
            self.assertIn(selection['source_revision'], record['source'])

    def test_original_tasks_oracles_goldens_and_all_sources_are_unchanged(self):
        locked = json.loads((HERE / 'external/original-lock.json').read_text())
        for path, expected in locked.items():
            self.assertEqual(hashlib.sha256((HERE.parents[1] / path).read_bytes()).hexdigest(), expected, path)

    def test_keyed_work_preserves_frozen_contracts_and_existing_baselines(self):
        lock = json.loads((HERE / 'KEYED_LOCK.json').read_text())
        for path, expected in lock['files'].items():
            self.assertEqual(hashlib.sha256((HERE.parents[1] / path).read_bytes()).hexdigest(), expected, path)

    def test_supported_references_and_unsupported_reasons_are_explicit(self):
        tasks = load_tasks('external')
        self.assertEqual(sum(t['nil_status'] == 'supported' for t in tasks), 42)
        self.assertEqual(sum(t['nil_status'] == 'unsupported' for t in tasks), 12)
        for task in tasks:
            if task['nil_status'] == 'unsupported':
                self.assertTrue(task['missing_capabilities'])
                self.assertTrue(task['unsupported_reason'])
                self.assertFalse((HERE / 'programs' / (task['id'] + '.nil')).exists())
            else:
                for extension in ['nil', 'py', 'cpp']:
                    self.assertTrue((HERE / 'programs' / (task['id'] + '.' + extension)).is_file())

    def test_every_external_fixture_has_an_upstream_expected_value(self):
        answers = json.loads((HERE / 'external/answers.json').read_text())
        goldens = load_goldens()
        for task in load_tasks('external'):
            if task['id'].startswith('ex_algo_'):
                continue
            golden = goldens[task['id']]
            for data in task['inputs'] + [golden['input']]:
                row = answers[task['id']][data]
                self.assertTrue(row['canonical_uuid'])
                self.assertEqual(external_expected(task['id'], bytes.fromhex(data)), bytes.fromhex(row['output']))
            self.assertEqual(external_expected(task['id'], bytes.fromhex(golden['input'])), bytes.fromhex(golden['output']))

    def test_algorithm_cohort_has_provenance_and_executable_goldens(self):
        tasks = [t for t in load_tasks('external') if t['id'].startswith('ex_algo_')]
        self.assertEqual(len(tasks), 4)
        goldens = load_goldens()
        for task in tasks:
            self.assertEqual(task['license'], 'MIT')
            self.assertEqual(task['origin'], 'external-derived')
            self.assertEqual(len(task['provenance']['source_sha256']), 64)
            self.assertIn(task['provenance']['revision'], task['provenance']['source'])
            golden = goldens[task['id']]
            self.assertEqual(external_expected(task['id'], bytes.fromhex(golden['input'])), bytes.fromhex(golden['output']))

    def test_unknown_external_inputs_are_rejected_not_guessed(self):
        with self.assertRaises(KeyError):
            external_expected('ex_hello_world', b'not a frozen fixture')

if __name__ == '__main__':
    unittest.main()
