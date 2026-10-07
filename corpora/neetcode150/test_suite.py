"""Independent hand-calculated cases and qualification harness regressions."""
import hashlib
import json
import tempfile
from pathlib import Path
import unittest
import fixtures
import reference
import verify
import export
import cpp

class SuiteTests(unittest.TestCase):
    def test_public_list_and_hash_selection_are_exact(self):
        tasks=verify.tasks();self.assertEqual(len(tasks),150);self.assertEqual(len({t['id'] for t in tasks}),150)
        cats={t['category'] for t in tasks};self.assertEqual(len(cats),18)
        for cat in cats:
            group=[t for t in tasks if t['category']==cat]
            for t in group:self.assertEqual(t['selection_hash'],hashlib.sha256(('NIL-Core-1.0\0'+cat+'\0'+t['id']).encode()).hexdigest())
            self.assertEqual({t['id'] for t in group if t['selected']},{t['id'] for t in sorted(group,key=lambda t:t['selection_hash'])[:2]})
    def test_all_tasks_have_original_references(self):
        ids={t['id'] for t in verify.tasks()};self.assertEqual(set(reference.SOLVERS),ids);self.assertEqual(set(cpp.B),ids)
    def test_selected_oracles_match_independent_hand_answers(self):
        cases={
        'contains-duplicate':('3 5 -1 5\n',b'1\n'),
        'valid-sudoku':(' '.join(['0']*81),b'1\n'),
        '3sum':('4 -5 0 2 3\n',b'-5 2 3\n'),
        'valid-palindrome':('B!b',b'1\n'),
        'longest-substring-without-repeating-characters':('abcbde',b'4\n'),
        'longest-repeating-character-replacement':('1\nAACAB',b'4\n'),
        'car-fleet':('30\n2\n10 3\n20 2\n',b'2\n'),
        'generate-parentheses':('2',b'(())\n()()\n'),
        'median-of-two-sorted-arrays':('2 1 5\n2 2 8\n',b'7\n'),
        'search-in-rotated-sorted-array':('4 6 8 0 2\n0\n',b'2\n'),
        'reverse-linked-list':('2 1\n3 -1\n8 0\n',b'3 8\n'),
        'lru-cache':('1 3\n0 8 99\n1 8\n1 7\n',b'99\n-1\n'),
        'balanced-binary-tree':('0 -1',b'1\n'),
        'validate-binary-search-tree':('2 0\n1 -1 1\n1 -1 -1',b'0\n'),
        'implement-trie-prefix-tree':('4\n+ bat\n= ba\n? ba\n= bat\n',b'0\n1\n1\n'),
        'word-search-ii':('1 2\naz\n3\na\naz\nza\n',b'a\naz\nza\n'),
        'last-stone-weight':('3 4 9 6\n',b'1\n'),
        'kth-largest-element-in-an-array':('3 7 2 7\n2\n',b'7\n'),
        'n-queens':('1',b'0\n'),
        'letter-combinations-of-a-phone-number':('3',b'd\ne\nf\n'),
        'course-schedule':('1 1\n0 0',b'0\n'),
        'course-schedule-ii':('3 1\n2 0',b'1 2 0\n'),
        'network-delay-time':('2 1 1\n1 0 8',b'8\n'),
        'cheapest-flights-within-k-stops':('2 1 0 1 0\n0 1 8',b'8\n'),
        'min-cost-climbing-stairs':('2 7 3',b'3\n'),
        'coin-change':('2 4 7\n8',b'2\n'),
        'target-sum':('2 1 1\n0',b'2\n'),
        'best-time-to-buy-and-sell-stock-with-cooldown':('4 1 5 0 4',b'4\n'),
        'gas-station':('2 0 5\n2 2 3',b'1\n'),
        'maximum-subarray':('4 -4 2 3 -2',b'5\n'),
        'meeting-rooms':('2\n1 3\n3 8',b'1\n'),
        'insert-interval':('1\n3 5\n1 4',b'1 5\n'),
        'plus-one':('2 9 9',b'1 0 0\n'),
        'spiral-matrix':('2 2\n1 2 3 4',b'1 2 4 3\n'),
        'single-number':('3 -8 1 -8',b'1\n'),
        'reverse-integer':('3 -120 2147483647 0',b'-21 0 0\n')}
        self.assertEqual(set(cases),{t['id'] for t in verify.tasks() if t['selected']})
        for slug,(data,answer) in cases.items():
            with self.subTest(task=slug):self.assertEqual(reference.SOLVERS[slug](data.encode()),answer)
    def test_wrong_answer_cannot_pass(self):
        with tempfile.TemporaryDirectory() as d:
            v=verify.observed(['python3','-c','open("output.bin","wb").write(b"x");print(1)'],Path(d),b'fixture',b'y')
            self.assertFalse(v['pass'])
    def test_correct_output_with_changed_input_cannot_pass(self):
        with tempfile.TemporaryDirectory() as d:
            v=verify.observed(['python3','-c','open("output.bin","wb").write(b"x");open("input.bin","wb").write(b"bad");print(1)'],Path(d),b'fixture',b'x')
            self.assertFalse(v['pass'])
    def test_correct_bytes_with_trap_cannot_pass(self):
        with tempfile.TemporaryDirectory() as d:
            v=verify.observed(['python3','-c','open("output.bin","wb").write(b"x");print(1);raise SystemExit(1)'],Path(d),b'fixture',b'x')
            self.assertFalse(v['pass'])
    def test_exported_sources_do_not_import_the_oracle(self):
        for t in verify.tasks():
            source=export.python_source(t['id']);self.assertNotIn('import reference',source);self.assertNotIn('tasks.json',source)
    def test_generator_replays_identical_small_fixtures(self):
        for t in verify.tasks():
            small={**t,'contract':{**t['contract'],'largest_size':min(5,t['contract']['largest_size'])}}
            self.assertEqual(list(fixtures.cases(small)),list(fixtures.cases(small)))
    def test_frozen_fixture_set_contains_every_task(self):
        golden=json.loads((verify.HERE/'goldens.json').read_text());self.assertEqual(set(golden),{t['id'] for t in verify.tasks()})

if __name__=='__main__':unittest.main()
