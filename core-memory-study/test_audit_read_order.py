"""Offline checks of the admission harness; native fault experiment is explicit."""
import subprocess
import unittest
import audit_read_order as audit

class ReadOrderAudit(unittest.TestCase):
    def test_matrix_has_quota_fault_laziness_child_and_call_controls(self):
        tasks = audit.definitions()
        self.assertEqual(len(tasks), 12)
        self.assertEqual(len({t['id'] for t in tasks}), 12)
        self.assertEqual(sum(t['expected'][0] != t['expected'][1] for t in tasks), 5)
        self.assertTrue(any(t['fault'] == 0 for t in tasks))
        self.assertTrue(any(t['fault'] == 64 for t in tasks))
        self.assertTrue(any(t.get('calls') == 0 for t in tasks))

    def test_diagnostic_observation_preserves_code_and_span(self):
        r = subprocess.CompletedProcess([], 1, b'', b'E013 @29..30 dynamic allocation limit exceeded\n')
        self.assertEqual(audit.observation(r), dict(code='E013', span=[29, 30], stdout_hex=''))

    def test_crash_is_not_mislabeled_as_language_diagnostic(self):
        with self.assertRaises(AssertionError):
            audit.observation(subprocess.CompletedProcess([], -6, b'', b'crash'))
        with self.assertRaises(AssertionError):
            audit.observation(subprocess.CompletedProcess([], -6, b'', b'E013 @29..30 failure\n'))

    def test_stdout_before_failure_is_not_silently_discarded(self):
        with self.assertRaises(AssertionError):
            audit.observation(subprocess.CompletedProcess([], 1, b'unexpected', b'E013 @29..30 failure\n'))

    def test_success_retains_exact_output_bytes(self):
        self.assertEqual(audit.observation(subprocess.CompletedProcess([], 0, b'12\n', b'')),
                         dict(code='OK', span=None, stdout_hex='31320a'))

if __name__ == '__main__':
    unittest.main()
