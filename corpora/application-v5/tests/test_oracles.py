"""Independent literal goldens, binary boundaries, and rejection of wrong references."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from oracles import expected
import verify

GOLDENS = {key: (bytes.fromhex(case['input']), bytes.fromhex(case['output']))
           for key, case in json.loads((verify.HERE / 'goldens.json').read_text()).items()}


class Contracts(unittest.TestCase):
    def test_all_tasks_have_independent_literal_golden(self):
        tasks = json.loads((verify.HERE / 'tasks.json').read_text())['tasks']
        self.assertEqual(set(GOLDENS), {task['id'] for task in tasks})
        for task, (data, output) in GOLDENS.items():
            with self.subTest(task=task):
                self.assertEqual(expected(task, data, {'NAME': 'é'}), output)

    def test_empty_and_final_delimiter_policies(self):
        for task in ['prefix_lines', 'number_lines', 'nonempty_lines', 'dedupe_adjacent_lines']:
            self.assertEqual(expected(task, b''), b'')
        self.assertEqual(expected('number_lines', b'\n'), b'1:\n')
        self.assertEqual(expected('prefix_lines', b'\n'), b'>\n')
        self.assertEqual(expected('slice_file', b'3,0\nabc'), b'')
        self.assertEqual(expected('env_lookup', b'ABSENT', {}), b'')

    def test_density_rejects_stale_or_failed_verification(self):
        from density import validate_verification
        with self.assertRaisesRegex(ValueError, 'stale'):
            validate_verification({'source_hashes': {}})
        with self.assertRaisesRegex(ValueError, 'Unverified'):
            validate_verification({'source_hashes': verify.fingerprint(), 'results': [{'semantic_ok': False}]})

    def test_export_rejects_stale_verification(self):
        from export import export
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'verification.json'
            path.write_text(json.dumps({'source_hashes': {}}))
            with self.assertRaisesRegex(ValueError, 'Stale'):
                export(path, Path(directory) / 'data.jsonl')

    def test_baseline_rejects_wrong_output_and_input_mutation(self):
        task = {'id': 'copy_file', 'inputs': ['6162']}
        for body in ['Path(output_path).write_bytes(b"ab")\n    Path(input_path).write_bytes(b"bad")\n    return 2', 'Path(output_path).write_bytes(b"wrong")\n    return 5']:
            with tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)
                path = folder / 'bad.py'
                path.write_text('from pathlib import Path\ndef solve(input_path, output_path):\n    ' + body + '\n')
                self.assertFalse(verify.baseline(task, path, folder, 'python')['semantic_ok'])


if __name__ == '__main__':
    unittest.main()
