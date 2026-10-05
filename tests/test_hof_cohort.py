"""Selection metadata must agree between verification and density consumers."""
import importlib.util
from pathlib import Path
import unittest

class HistoricalCohort(unittest.TestCase):
    def test_original_audit_keeps_frozen_support_but_all_runs_cover_environment(self):
        path = Path(__file__).resolve().parents[1]/'corpora/application-v5/external_suite.py'
        spec = importlib.util.spec_from_file_location('hof_corpus_cohort', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original = module.load_tasks('original')
        all_tasks = module.load_tasks()
        self.assertEqual(len(original),25)
        self.assertEqual(sum(t['nil_status']=='supported' for t in original),24)
        env = next(t for t in original if t['id']=='env_lookup')
        self.assertEqual(env['nil_status'],'unsupported')
        self.assertEqual(next(t for t in all_tasks if t['id']=='env_lookup')['nil_status'],'supported')
        self.assertEqual(next(t for t in all_tasks if t['id']=='ex_accumulate')['nil_status'],'supported')
        self.assertEqual(sum(t['nil_status']=='supported' for t in all_tasks),68)
        self.assertEqual(env['inputs'],next(t for t in all_tasks if t['id']=='env_lookup')['inputs'])

if __name__=='__main__': unittest.main()
