import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('exposure', HERE / 'run.py')
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)


class Exposure(unittest.TestCase):
    def test_fixed_selection_excludes_evaluated_answers_and_new_capabilities(self):
        self.assertEqual([t['id'] for t, _ in r.examples()], ['invert_bytes', 'histogram_digits', 'count_newlines', 'hex_encode'])
        tasks = json.loads((r.APP / 'tasks.json').read_text())['tasks']
        for task in tasks:
            control = r.frozen.prompt('expr-v5', task)
            treated = r.prompt('expr-v5', task)
            prefix, suffix = control.split('\nTask: ', 1)
            self.assertTrue(treated.startswith(prefix))
            self.assertTrue(treated.endswith('\nTask: ' + suffix))
            self.assertNotIn(json.dumps(task['inputs']), treated)
            for example, source in r.examples():
                self.assertIn(source, treated)
                self.assertNotEqual(example['id'], task['id'])

    def test_validity_counts_distinguish_unknown_and_failed_stages(self):
        rows = [dict(parse_ok=False, semantic_ok=False, failure_reason='parse'),
                dict(parse_ok=True, typecheck_ok=False, semantic_ok=False, failure_reason='type'),
                dict(parse_ok=True, typecheck_ok=True, compile_ok=True, semantic_ok=False, failure_reason='semantic_or_execution'),
                dict(parse_ok=True, typecheck_ok=True, compile_ok=True, semantic_ok=True)]
        d = r.modes(rows)
        self.assertEqual([d[k] for k in ['attempts','parse_pass','typecheck_pass','compile_pass']], [4,3,2,2])
        self.assertEqual(d['outcomes'], {'parse':1,'type':1,'semantic_or_execution':1,'correct':1})
        self.assertEqual(d['typecheck_unknown'], 1)
        self.assertEqual(d['compile_unknown'], 2)

    def test_original_prompt_is_unchanged(self):
        import subprocess
        old = subprocess.check_output(['git','show','0d7ead4:generation/application/run.py'], cwd=r.SUITE, text=True)
        start = old.index('def prompt('); end = old.index('\n\ndef provenance', start)
        namespace = {'HERE':r.APP};exec(old[start:end], namespace)
        for task in json.loads((r.APP / 'tasks.json').read_text())['tasks']:
            for language in ['expr-v5','python']:
                self.assertEqual(r.frozen.prompt(language,task), namespace['prompt'](language,task))

if __name__ == '__main__': unittest.main()
