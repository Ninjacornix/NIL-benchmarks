import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE))
import backend
spec=importlib.util.spec_from_file_location('standing',HERE/'run.py')
standing=importlib.util.module_from_spec(spec);spec.loader.exec_module(standing)
MODEL='claude-sonnet-5-5'
def response(text='source'):
    return [dict(type='system',subtype='init',model=MODEL,tools=[],mcp_servers=[]),
            dict(type='result',is_error=False,result=text,total_cost_usd=.01,
                 usage=dict(input_tokens=10,cache_read_input_tokens=20,cache_creation_input_tokens=30,output_tokens=40))]

class TransportTests(unittest.TestCase):
    def test_usage_includes_all_cache_input_without_source_token_imputation(self):
        r=backend.inspect_stream(response(),MODEL)
        self.assertEqual(r['input_tokens'],60);self.assertEqual(r['output_tokens'],40)
    def test_missing_usage_fails_closed_with_known_cost(self):
        x=response();del x[-1]['usage']['output_tokens']
        with self.assertRaises(backend.BackendError) as e:backend.inspect_stream(x,MODEL)
        self.assertEqual(e.exception.reason,'usage-missing');self.assertEqual(e.exception.cost,.01)
    def test_tool_call_anywhere_is_isolation_violation(self):
        x=response();x.insert(1,dict(type='assistant',message=dict(content=[dict(type='tool_use',name='Read')])))
        with self.assertRaises(backend.BackendError) as e:backend.inspect_stream(x,MODEL)
        self.assertEqual(e.exception.reason,'isolation')
    def test_mcp_and_hook_events_fail_even_when_result_succeeds(self):
        for key in ['tools','mcp_servers']:
            x=response();x[0][key]=['leak']
            with self.assertRaises(backend.BackendError):backend.inspect_stream(x,MODEL)
        x=response();x.insert(1,dict(type='system',subtype='hook_started'))
        with self.assertRaises(backend.BackendError):backend.inspect_stream(x,MODEL)
    def test_wrong_model_and_infrastructure_result_stop_not_substitute(self):
        x=response();x[0]['model']='another-model'
        with self.assertRaises(backend.BackendError):backend.inspect_stream(x,MODEL)
        x=response();x[-1]['is_error']=True;x[-1]['errors']=['unavailable']
        with self.assertRaises(backend.BackendError) as e:backend.inspect_stream(x,MODEL)
        self.assertEqual(e.exception.reason,'infrastructure')
    def test_network_denied_initialization_failure_blocks_live_request(self):
        import subprocess
        client=object.__new__(backend.Claude)
        client.executable=Path('/usr/bin/true');client.model=MODEL;client.version='CLI';client.bare=False;client.proven=False
        completed=[subprocess.CompletedProcess([],1,b'',b'denied'),
                   subprocess.CompletedProcess([],0,'CLI\n',''),
                   subprocess.CompletedProcess([],1,'','EPERM global temporary settings')]
        with patch.object(backend.subprocess,'run',side_effect=completed):
            with self.assertRaises(backend.BackendError) as error:client.preflight()
        self.assertEqual(error.exception.reason,'isolation');self.assertFalse(client.proven)
        self.assertTrue(client.probe_evidence['network_denied'])

    def test_flags_pin_effort_disable_authority_and_bound_cost(self):
        f=backend.flags(MODEL,1)
        for key in ['--safe-mode','--restricted','--no-session-persistence','--strict-mcp-config']:self.assertIn(key,f)
        self.assertEqual(f[f.index('--tools')+1],'')
        self.assertEqual(f[f.index('--effort')+1],'high')
        self.assertEqual(f[f.index('--model')+1],MODEL)

class HarnessTests(unittest.TestCase):
    def test_split_and_all_three_prompts_contain_no_held_out_answers(self):
        plan,split,tasks=standing.validate_split()
        for tid in split['held_out']+split['dev']:
            for arm in plan['arms']:self.assertIn(tasks[tid]['prompt'],standing.make_prompt(arm,tasks[tid],split,tasks))
    def test_held_out_statement_in_context_stops_the_run(self):
        _,split,tasks=standing.validate_split()
        with self.assertRaises(ValueError):standing.guard_context(tasks[split['held_out'][0]]['prompt'],split,tasks)
    def test_held_out_solution_in_context_stops_the_run(self):
        _,split,tasks=standing.validate_split();tid=split['held_out'][0]
        answer=(standing.SUITE/'corpora/application-v5/programs'/f'{tid}.nil').read_text()
        with self.assertRaises(ValueError):standing.guard_context(answer,split,tasks)
    def test_zero_solves_and_unknown_usage_do_not_become_zero_tcr(self):
        row=dict(arm='nil-spec',trial='x',attempt=0,taxonomy='parse',input_tokens=None,output_tokens=None)
        a=standing.aggregate([row])[1]
        self.assertIsNone(a['total_tcr']);self.assertIsNone(a['output_tokens'])
    def test_repair_tokens_include_failed_attempt_and_fixed_spec_scenario(self):
        rows=[dict(arm='nil-spec',trial='x',attempt=i,taxonomy='parse' if i==0 else 'correct',semantic_ok=i==1,input_tokens=100,output_tokens=20,cost_usd=.01) for i in range(2)]
        a=standing.aggregate(rows,30)[1]
        self.assertEqual(a['output_tcr'],40);self.assertEqual(a['repair_output_tokens'],20)
        self.assertEqual(a['input_tokens_spec_amortized'],170)
    def test_mock_repair_reuses_actual_diagnostics_and_three_attempt_ceiling(self):
        def verdict(source,arm,task,folder):
            return dict(taxonomy='parse',semantic_ok=False,feedback='E001 actual mocked parser diagnostic',parse_ok=False)
        with tempfile.TemporaryDirectory() as tmp,patch.object(standing.application.oracle,'prepare'),patch.object(standing,'oracle',verdict):
            r=standing.run(Path(tmp)/'run',mock=True)
            rows=[json.loads(x) for x in (Path(tmp)/'run/attempts.jsonl').read_text().splitlines()]
            self.assertEqual(len(rows),9);self.assertEqual(r['status'],'complete')
            req=json.loads(next((Path(tmp)/'run').glob('*-nil-spec-1/request.json')).read_text())
            self.assertIn('E001',req['messages'][-1]['content'])
    def test_infrastructure_failure_stops_campaign_without_retry(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(standing.application.oracle,'prepare'),patch.object(standing.Mock,'request',side_effect=backend.BackendError('infrastructure','unavailable',0)):
            r=standing.run(Path(tmp)/'run',mock=True)
            self.assertEqual(r['status'],'blocked-infrastructure');self.assertEqual(r['attempts'],1)
    def test_spend_reservation_blocks_next_request(self):
        plan,_,_=standing.validate_split();plan=plan|{'spend_cap_usd':.5}
        with tempfile.TemporaryDirectory() as tmp,patch.object(standing.application.oracle,'prepare'),patch.object(standing,'validate_split',return_value=(plan,*standing.validate_split()[1:])):
            r=standing.run(Path(tmp)/'run',mock=True)
            self.assertEqual(r['status'],'spend-cap');self.assertEqual(r['attempts'],0)

if __name__=='__main__':unittest.main()
