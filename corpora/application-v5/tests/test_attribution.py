import sys
import unittest
from fractions import Fraction
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from attribution import ledger, nil_labels, python_labels
from remediation import signature_references, empty_steps


class AttributionTests(unittest.TestCase):
    def test_mixed_token_tie_and_fractional_ledger_account_exactly(self):
        counts, shares, rows = ledger(',a', ['separator', 'identifier'], [b',a'])
        self.assertEqual(counts, {'separator': 1})
        self.assertEqual(shares, {'separator': '1/2', 'identifier': '1/2'})
        self.assertEqual(sum(Fraction(x) for x in shares.values()), 1)
        self.assertEqual(rows[0]['end'], 2)

    def test_whitespace_does_not_steal_a_mixed_token(self):
        counts, _, _ = ledger(' abc', ['whitespace'] + ['identifier'] * 3, [b' abc'])
        self.assertEqual(counts, {'identifier': 1})

    def test_gemma_dummy_space_is_not_a_source_token(self):
        counts, _, _ = ledger('a', ['identifier'], [b' a'], True)
        self.assertEqual(counts, {'identifier': 1})

    def test_source_reconstruction_mismatch_fails_closed(self):
        with self.assertRaises(AssertionError):
            ledger('a', ['identifier'], [b'b'])

    def test_nested_loops_have_their_own_positional_state(self):
        source = '(s):s=@(a,0;b<#a;a,b+1;@(a,0;b<#a;a,b+1;a))\n'
        labels, data = nil_labels(source)
        self.assertEqual(len(data['loops']), 2)
        self.assertEqual([source[s:e] for s, e in data['passthrough_spans']], ['a', 'a'])
        self.assertEqual(labels[source.index('b+1')], 'loop_index_bound')
        self.assertEqual(labels[0], 'signature')

    def test_literals_containing_delimiters_do_not_create_loops(self):
        _, data = nil_labels('(s):s=!concat(a,"@(;),[]")\n')
        self.assertEqual(data['loops'], [])

    def test_python_library_calls_and_user_calls_are_separated(self):
        source = 'def helper(x):\n    return len(x)\ndef solve(x):\n    return helper(x)\n'
        labels, _ = python_labels(source)
        self.assertEqual(labels[source.index('len')], 'intrinsic_name')
        self.assertEqual(labels[source.rindex('helper')], 'call_identifier')
        self.assertEqual(labels[0], 'signature')

    def test_signature_forecast_uses_complete_prior_signature(self):
        source = '(s,i):s=a\n(s,i):b=true\n(s,i):s=a\n'
        proposed, edits = signature_references(source)
        self.assertEqual(proposed, '(s,i):s=a\n(s,i):b=true\n^a=a\n')
        self.assertEqual(edits[0]['reference'], 0)
        self.assertEqual(len(edits), 1)

    def test_empty_step_forecast_preserves_state_positions(self):
        proposed, spans = empty_steps('(s):s=@(a,0;b<#a;a,b+1;a)\n')
        self.assertEqual(proposed, '(s):s=@(a,0;b<#a;,b+1;a)\n')
        self.assertEqual(len(spans), 1)


if __name__ == '__main__':
    unittest.main()
