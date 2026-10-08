"""Offline checks of the admission harness; native fault experiment is explicit."""
import subprocess
import unittest
import audit_read_order as audit

class ReadOrderAudit(unittest.TestCase):
    def test_matrix_has_quota_fault_laziness_child_and_call_controls(self):
        tasks = audit.definitions()
        self.assertEqual(len(tasks), 14)
        self.assertEqual(len({t['id'] for t in tasks}), 14)
        self.assertEqual(sum(t['expected'][0] != t['expected'][1] for t in tasks), 0)
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

    def test_resource_diagnostic_cannot_hide_sanitizer_or_reversed_span(self):
        for text in (b'E013 @3..4 failure\nAddressSanitizer: heap-buffer-overflow\n', b'E013 @4..3 failure\n'):
            with self.assertRaises(AssertionError):
                audit.observation(subprocess.CompletedProcess([], 1, b'', text))

    def test_resource_outcomes_are_inconclusive_not_equal(self):
        resource = dict(code='E013', span=[3,4], stdout_hex='')
        same = dict(resource)
        other = dict(code='E015', span=[7,8], stdout_hex='')
        self.assertEqual(audit.compare(resource, same), 'inconclusive')
        self.assertEqual(audit.compare(resource, other), 'inconclusive')
        self.assertEqual(audit.compare(other, resource), 'inconclusive')
        self.assertEqual(audit.compare(other, other), 'equal')
        self.assertEqual(audit.compare(other, dict(other, span=[8,9])), 'different')

if __name__ == '__main__':
    unittest.main()
