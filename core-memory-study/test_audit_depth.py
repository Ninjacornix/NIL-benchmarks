"""Offline integrity checks; live admission is deliberately fail-closed."""
import subprocess
import unittest
import audit_depth as audit


class DepthAudit(unittest.TestCase):
    def test_signal_is_not_depth_diagnostic_even_with_diagnostic_text(self):
        r = subprocess.CompletedProcess([], -11, b"", b"E008 @1..2 call depth limit exceeded\n")
        self.assertEqual(audit.observe(r), dict(kind="signal", signal=11))

    def test_depth_diagnostic_preserves_span(self):
        r = subprocess.CompletedProcess([], 1, b"", b"E008 @40..46 call depth limit exceeded\n")
        self.assertEqual(audit.observe(r), dict(kind="diagnostic", code="E008", span=[40, 46]))

    def test_sanitizer_report_is_not_clean_depth_failure(self):
        r = subprocess.CompletedProcess([], 1, b"", b"E008 @1..2 failure\nAddressSanitizer: stack-overflow\n")
        self.assertEqual(audit.observe(r)["kind"], "infrastructure")

    def test_invalid_span_is_not_a_language_result(self):
        r = subprocess.CompletedProcess([], 1, b"", b"E008 @4..3 failure\n")
        self.assertEqual(audit.observe(r)["kind"], "invalid-diagnostic")

    def test_wrong_status_is_not_a_clean_diagnostic(self):
        r = subprocess.CompletedProcess([], 2, b"", b"E008 @3..4 failure\n")
        self.assertEqual(audit.observe(r)["kind"], "infrastructure")

    def test_sources_cover_mutual_recursion_and_large_record_frames(self):
        cases = audit.definitions()
        self.assertEqual(len(cases), 3)
        self.assertEqual(len({c["id"] for c in cases}), 3)
        self.assertIn("c(a-1)", cases[1]["source"])
        self.assertEqual(cases[2]["source"].count(":256"), 15)
        self.assertIn("b(a-1,b)", cases[2]["source"])


if __name__ == "__main__":
    unittest.main()
