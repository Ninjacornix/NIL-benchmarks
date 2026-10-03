import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('application_experiment',HERE/'run.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)


class ApplicationOracle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r.oracle.prepare()
        cls.tasks=json.loads((HERE/'tasks.json').read_text())['tasks']

    def test_literal_contract_edges_independent_of_solutions(self):
        self.assertEqual(r.oracle.expected('ascii_upper',b'a\x00\xffZ'),b'A\x00\xffZ')
        self.assertEqual(r.oracle.expected('nonempty_lines',b'\n \n\r\nlast'),b' \n\r\nlast\n')
        self.assertEqual(r.oracle.expected('sum_pairs',b'-4,9\n0,-2'),b'5\n-2\n')
        self.assertEqual(r.oracle.expected('running_report',b'3'),b'0:0\n1:1\n2:3\n')

    def test_all_frozen_fixtures_reference_native_o0_o2_and_python(self):
        with tempfile.TemporaryDirectory(prefix='nil-app-oracles-') as d:
            for task in self.tasks:
                for language,extension in [('expr-v5','nil'),('python','py')]:
                    with self.subTest(task=task['id'],language=language):
                        result=r.oracle.evaluate((HERE/'solutions'/f"{task['id']}.{extension}").read_text(),language,task,Path(d))
                        self.assertTrue(result['semantic_ok'],result)
                        self.assertEqual(result['tests_passed'],4)
                        if language=='expr-v5':self.assertEqual(result['native_tests_passed'],8)

    def test_parse_type_wrong_bytes_stdout_and_input_mutation_fail(self):
        task=self.tasks[0]
        with tempfile.TemporaryDirectory(prefix='nil-app-failures-') as d:
            folder=Path(d)
            self.assertFalse(r.oracle.evaluate('invalid','expr-v5',task,folder)['parse_ok'])
            self.assertFalse(r.oracle.evaluate('(s,s)=true+1','expr-v5',task,folder)['typecheck_ok'])
            self.assertFalse(r.oracle.evaluate('(s,s)=!write(b,!read(a))','expr-v5',task,folder)['semantic_ok'])
            source=(HERE/'solutions/ascii_upper.py').read_text()
            self.assertFalse(r.oracle.evaluate(source+'\nprint("extra")\n','python',task,folder)['semantic_ok'])
            mutated=source.replace('return len(result)',"open(input_path, 'wb').write(b'changed')\n    return len(result)")
            self.assertFalse(r.oracle.evaluate(mutated,'python',task,folder)['semantic_ok'])

    def test_sandbox_denies_other_fixtures_home_writes_and_network(self):
        with tempfile.TemporaryDirectory(prefix='nil-app-sandbox-') as d:
            folder=Path(d).resolve()
            sentinel=folder/'outside';sentinel.write_bytes(b'secret')
            case=folder/'case';case.mkdir()
            for code in [f'open({str(sentinel)!r}, "rb").read()',
                         'import socket; socket.create_connection(("127.0.0.1",11434))',
                         f'open({str(folder/"forbidden")!r}, "wb").write(b"bad")']:
                result=r.oracle.sandbox([str(Path(sys.executable).resolve()),'-I','-c',code],case)
                self.assertNotEqual(result.returncode,0)
            self.assertFalse((folder/'forbidden').exists())

    def test_stub_runs_real_oracles_repair_and_unsolved_cells_then_audits_usage(self):
        with tempfile.TemporaryDirectory(prefix='nil-app-stub-test-') as d:
            output=Path(d)/'run'
            r.run(output,'unused',mock=True)
            result=r.report(output)
            self.assertTrue(result['mock'])
            self.assertEqual(result['trials'],24)
            self.assertEqual(result['attempts'],54)
            for row in result['aggregate']:
                self.assertEqual(row['solved'],9)
                self.assertEqual(row['output_tokens'],288)
                self.assertEqual(row['input_tokens'],558)
                self.assertEqual(row['repair_tokens'],168)
                self.assertEqual(row['first_pass'],0)
            trials=output/'trials.jsonl';rows=[json.loads(x) for x in trials.read_text().splitlines()]
            rows[0]['output_tokens']+=1
            trials.write_text(''.join(json.dumps(x)+'\n' for x in rows))
            with self.assertRaises(AssertionError):r.audit(output)

    def test_single_fence_extraction_keeps_unrequested_prose(self):
        self.assertEqual(r.extract_source('```python\ndef solve(a,b): return 0\n```'),'def solve(a,b): return 0\n')
        self.assertIn('Explanation',r.extract_source('Explanation\n```nil\n(s,s)=0\n```'))


if __name__=='__main__':unittest.main()
