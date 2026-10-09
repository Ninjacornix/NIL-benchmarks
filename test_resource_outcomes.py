import subprocess
import unittest
from resource_outcomes import clean_e013, clean_resource, native_code

class ResourceOutcomesTests(unittest.TestCase):
    def result(self, exit, out=b'', err=b''):
        return subprocess.CompletedProcess([], exit, out, err)

    def test_clean_resource_is_inconclusive_with_or_without_span(self):
        for diagnostic in (b'E013 @3..4 allocation failed\n', b'E013 argument allocation failed\n'):
            self.assertTrue(clean_e013(self.result(1, err=diagnostic)))
            self.assertTrue(clean_e013(self.result(0, b'ERR\tExecute\t'+diagnostic), reference=True))
            self.assertEqual(native_code(self.result(1, err=diagnostic)), 'E013')

    def test_crashes_malformed_output_and_sanitizers_are_not_resources(self):
        for result in (
            self.result(-6, err=b'E013 @3..4 allocation failed\n'),
            self.result(1, err=b'E013 @4..3 allocation failed\n'),
            self.result(1, err=b'E013 @3..4 allocation failed\nAddressSanitizer: failure\n'),
            self.result(1, err=b'E013 runtime error: overflow\n'),
            self.result(0, err=b'E013 @3..4 allocation failed\n'),
        ):
            self.assertFalse(clean_e013(result))
            with self.assertRaises(AssertionError):
                native_code(result)

    def test_real_diagnostics_are_not_resources(self):
        self.assertFalse(clean_e013(self.result(1, err=b'E012 @3..4 bad index\n')))
        self.assertEqual(native_code(self.result(1, err=b'E012 @3..4 bad index\n')), 'E012')

class StackResources(unittest.TestCase):
    def test_clean_stack_exhaustion_is_inconclusive(self):
        result = subprocess.CompletedProcess([], 1, b'', b'E008 call depth/stack exhausted\n')
        self.assertTrue(clean_resource(result))
    def test_signal_with_stack_text_still_fails(self):
        result = subprocess.CompletedProcess([], -11, b'', b'E008 call depth/stack exhausted\n')
        self.assertFalse(clean_resource(result))

if __name__ == '__main__':
    unittest.main()
