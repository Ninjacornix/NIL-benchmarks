"""Subscription transport/resume tests never invoke Claude or read real credentials."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from test_standing import backend, standing, response, MODEL, TemporaryReports

FAKE='planted-OAuth-secret-NIL-15b-never-a-real-token'


def client():
    value=object.__new__(backend.Claude)
    value.executable=Path('/usr/bin/true');value.model=MODEL;value.version='MOCK-CLI'
    value.token=FAKE;value.secrets=backend.Secrets(FAKE,'planted-api-secret')
    value.bare=False;value.auth_method='MOCK subscription';value.proven=True
    return value


def verdict(source,arm,task,folder):
    return dict(taxonomy='parse' if source.strip()=='not source' else 'correct',
                semantic_ok=source.strip()!='not source',feedback='E001 actual parser feedback',parse_ok=source.strip()!='not source')


class SubscriptionTransportTests(unittest.TestCase):
    def test_private_token_file_only_and_no_api_key_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/'token';file.write_text(FAKE);file.chmod(0o600)
            with patch.dict(os.environ,{'NIL_CLAUDE_OAUTH_TOKEN_FILE':str(file),'ANTHROPIC_API_KEY':'unforwarded'}):
                self.assertEqual(backend.subscription_token(),FAKE)
                with patch.object(backend.shutil,'which',return_value='/usr/bin/true'),patch.object(backend.subprocess,'check_output',return_value='MOCK-CLI'):
                    c=backend.Claude(MODEL)
                env=c.environment(Path(tmp)/'state',Path(tmp)/'home',8192)
                self.assertEqual(env['CLAUDE_CODE_OAUTH_TOKEN'],FAKE)
                self.assertNotIn('ANTHROPIC_API_KEY',env)
                self.assertNotIn('--bare',backend.flags(MODEL,1))
                self.assertEqual(env['CLAUDE_CODE_MAX_OUTPUT_TOKENS'],'8192')
    def test_group_or_other_readable_token_fails_before_cli_startup(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/'token';file.write_text(FAKE)
            for mode in (0o640,0o604,0o644,0o660):
                file.chmod(mode)
                with patch.dict(os.environ,{'NIL_CLAUDE_OAUTH_TOKEN_FILE':str(file)}),patch.object(backend.shutil,'which') as which:
                    with self.assertRaises(backend.BackendError) as error: backend.Claude(MODEL)
                    self.assertEqual(error.exception.reason,'authentication');which.assert_not_called()
    def test_missing_symlink_directory_and_empty_token_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/'token';file.touch();file.chmod(0o600)
            link=Path(tmp)/'link';link.symlink_to(file)
            for path in (Path(tmp)/'missing',link,Path(tmp),file):
                with patch.dict(os.environ,{'NIL_CLAUDE_OAUTH_TOKEN_FILE':str(path)}):
                    with self.assertRaises(backend.BackendError): backend.subscription_token()
    def test_sibling_layout_allows_cli_state_but_keeps_working_directory_empty(self):
        c=client();c.proven=False;calls=[]
        def fake_run(argv,**kwargs):
            calls.append((argv,kwargs))
            cwd=Path(kwargs['cwd']);self.assertEqual(cwd.name,'cwd');self.assertFalse(list(cwd.iterdir()))
            if argv[-2:]==['-c','1']: self.fail('missing read-probe target')
            if '/usr/bin/head' in argv: return subprocess.CompletedProcess(argv,1,b'',b'denied')
            if '--version' in argv: return subprocess.CompletedProcess(argv,0,'MOCK-CLI\n','')
            env=kwargs['env'];state=Path(env['CLAUDE_CODE_TMPDIR'])
            self.assertNotEqual(state,cwd);self.assertEqual(state.parent,cwd.parent)
            self.assertEqual(Path(env['HOME']).parent,cwd.parent)
            self.assertIn('(deny network*)',argv[2]);self.assertNotIn('CLAUDE_CODE_OAUTH_TOKEN',env)
            (state/'claude-501').mkdir()
            return subprocess.CompletedProcess(argv,1,json.dumps(response()[0])+'\n',FAKE)
        with patch.object(backend.subprocess,'run',fake_run): proof=c.preflight()
        self.assertTrue(proof['sibling_temp_layout']);self.assertTrue(proof['keychain_reads_denied'])
        self.assertEqual(len(calls),4);self.assertNotIn(FAKE,json.dumps(c.probe_evidence))
    def test_profile_denies_real_keychains_security_executable_and_repository(self):
        profile=backend.sandbox_profile(Path('/tmp/fake'),Path('/usr/bin/true'))
        self.assertIn(str(Path.home()/'Library/Keychains'),profile)
        self.assertIn('(deny process-exec (literal "/usr/bin/security"))',profile)
        self.assertNotIn(str(Path.home()/'.claude.json'),profile)
        self.assertIn(str(backend.ROOT),profile)
    def test_profile_is_a_sequence_of_balanced_top_level_rules(self):
        # Implicit string-literal concatenation once nested the keychain rules inside the
        # repository rule; sandbox-exec rejected the whole profile. Check structure here,
        # since sandbox-exec itself is unavailable in some CI/agent sandboxes.
        profile=backend.sandbox_profile(Path('/tmp/fake'),Path('/usr/bin/true'))
        forms,depth,start=[],0,0
        for index,char in enumerate(profile):
            if char=='(':
                if depth==0: start=index
                depth+=1
            elif char==')':
                depth-=1
                self.assertGreaterEqual(depth,0)
                if depth==0: forms.append(profile[start:index+1])
        self.assertEqual(depth,0)
        self.assertEqual(''.join(forms),profile)
        self.assertEqual(forms[0],'(version 1)')
        for form in forms[1:]:
            self.assertRegex(form,r'^\((allow|deny) ')
            # A rule must not contain another top-level rule.
            self.assertNotRegex(form[1:],r'\((allow|deny) ')
        self.assertEqual(sum(f.startswith('(deny file-read* (subpath') for f in forms),5)
    def test_preflight_environment_never_contains_the_token(self):
        c=client()
        with tempfile.TemporaryDirectory() as tmp:
            env=c.environment(Path(tmp)/'state',Path(tmp)/'home',8192,authenticated=False)
            self.assertNotIn('CLAUDE_CODE_OAUTH_TOKEN',env)
            self.assertNotIn(FAKE,json.dumps(env))
            live=c.environment(Path(tmp)/'state',Path(tmp)/'home',8192)
            self.assertEqual(live['CLAUDE_CODE_OAUTH_TOKEN'],FAKE)
    def test_request_redacts_token_in_stdout_stderr_metadata_and_error(self):
        c=client();events=response(FAKE);events[-1]['is_error']=True;events[-1]['errors']=[FAKE]
        with tempfile.TemporaryDirectory() as tmp,patch.object(backend.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'\n'.join(map(json.dumps,events)),FAKE)):
            folder=Path(tmp)
            with self.assertRaises(backend.BackendError) as error:
                c.request([{'role':'user','content':'echo '+FAKE}],1,8192,folder)
            self.assertNotIn(FAKE,str(error.exception))
            for file in folder.rglob('*'):
                if file.is_file(): self.assertNotIn(FAKE.encode(),file.read_bytes(),str(file))
            meta=json.loads((folder/'request.json').read_text())
            self.assertEqual(meta['environment']['CLAUDE_CODE_OAUTH_TOKEN'],'[REDACTED]')
    def test_rate_window_is_transport_pause_with_authoritative_accounting(self):
        for message in ('Rate limit exceeded',"You've hit your limit · resets 8pm",'usage window exhausted'):
            events=response();events[-1].update(is_error=True,errors=[message])
            with self.assertRaises(backend.BackendError) as error: backend.inspect_stream(events,MODEL)
            self.assertEqual(error.exception.reason,'rate-limit');self.assertEqual(error.exception.cost,.01)
            self.assertEqual(error.exception.usage['input_tokens'],60)
    def test_model_answer_mentioning_rate_limit_is_not_a_pause(self):
        self.assertEqual(backend.inspect_stream(response('rate limit exceeded'),MODEL)['text'],'rate limit exceeded')
    def test_tool_use_wins_over_rate_limit_classification(self):
        events=response();events[-1].update(is_error=True,subtype='error_rate_limit')
        events.insert(1,{'type':'tool_use'})
        with self.assertRaises(backend.BackendError) as error: backend.inspect_stream(events,MODEL)
        self.assertEqual(error.exception.reason,'isolation')
    def test_rate_limit_with_new_cwd_file_is_isolation_failure(self):
        c=client();events=response();events[-1].update(is_error=True,subtype='error_rate_limit')
        def fake_run(argv,**kwargs):
            (Path(kwargs['cwd'])/'leak').touch()
            return subprocess.CompletedProcess(argv,1,'\n'.join(map(json.dumps,events)),'')
        with tempfile.TemporaryDirectory() as tmp,patch.object(backend.subprocess,'run',fake_run):
            with self.assertRaises(backend.BackendError) as error: c.request([],1,8192,Path(tmp))
        self.assertEqual(error.exception.reason,'isolation')


class ResumeTests(TemporaryReports):
    def run_mock(self,path,**kwargs):
        with patch.object(standing.application.oracle,'prepare'),patch.object(standing,'oracle',verdict):
            return standing.run(path,mock=True,**kwargs)
    def test_resumed_campaign_has_identical_attempts_prompts_usage_and_cost(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);full=self.run_mock(root/'full')
            paused=self.run_mock(root/'paused',mock_rate_limit_after=2)
            self.assertEqual(paused['status'],'paused-rate-limit');self.assertEqual(paused['attempts'],2)
            resumed=self.run_mock(None,resume=root/'paused')
            self.assertEqual(resumed['status'],'complete');self.assertEqual(resumed['attempts'],full['attempts'])
            self.assertEqual(resumed['spent_usd'],full['spent_usd'])
            rows=lambda p:(p/'attempts.jsonl').read_text()
            self.assertEqual(rows(root/'full'),rows(root/'paused'))
            for f in (root/'full').glob('*/request.json'):
                x=json.loads(f.read_text());g=root/'paused'/f.relative_to(root/'full')
                if not g.exists(): g=next((root/'paused').glob(f.parent.name+'-invocation-*/request.json'))
                y=json.loads(g.read_text());self.assertEqual(x['messages'],y['messages'])
            self.assertEqual(len(resumed['transport_pauses']),1)
            self.assertEqual(resumed['campaign_events'][0]['type'],'resume')
            with self.assertRaises(ValueError): self.run_mock(None,resume=root/'paused')
    def test_pause_is_not_failed_attempt_and_charged_output_reduces_trial_budget(self):
        saved=standing.Mock.request;caps=[];once=[False]
        def pause_then_return(c,messages,budget,cap,folder):
            caps.append(cap)
            if not once[0]:
                once[0]=True
                raise backend.BackendError('rate-limit','limit',.02,{'input_tokens':17,'output_tokens':8192})
            return saved(c,messages,budget,cap,folder)
        with tempfile.TemporaryDirectory() as tmp,patch.object(standing.Mock,'request',pause_then_return):
            root=Path(tmp)/'run';first=self.run_mock(root);self.assertEqual(first['attempts'],0)
            final=self.run_mock(None,resume=root)
            self.assertEqual(final['attempts'],6);self.assertAlmostEqual(final['spent_usd'],.026)
            self.assertEqual(caps[:3],[8192,8192,8172])
            self.assertEqual(final['dev'][0]['output_tokens'],8232)
            self.assertEqual(final['dev'][0]['input_tokens_full'],217)
            self.assertEqual(final['dev'][0]['failures'],{'parse':1,'correct':1})
    def test_unknown_rate_usage_or_cost_blocks_resume(self):
        for cost,usage in [(None,{'input_tokens':0,'output_tokens':0}),(.01,None)]:
            with tempfile.TemporaryDirectory() as tmp,patch.object(standing.Mock,'request',side_effect=backend.BackendError('rate-limit','limit',cost,usage)):
                root=Path(tmp)/'run';r=self.run_mock(root)
                self.assertEqual(r['status'],'blocked-rate-limit-accounting');self.assertEqual(r['attempts'],0)
                with self.assertRaises(ValueError): self.run_mock(None,resume=root)
    def test_unresolved_inflight_request_and_checkpoint_tampering_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'run';self.run_mock(root,mock_rate_limit_after=1)
            file=root/'checkpoint.json';saved=json.loads(file.read_text())
            for resign in (False,True):
                x=json.loads(json.dumps(saved));x['state']['pending']={'unknown':'usage'}
                if resign:x['sha256']=standing.digest(json.dumps(x['state'],sort_keys=True))
                file.write_text(json.dumps(x))
                with self.assertRaises(ValueError): self.run_mock(None,resume=root)
    def test_changed_frozen_plan_or_cli_version_cannot_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'run';self.run_mock(root,mock_rate_limit_after=1)
            with patch.object(standing.Mock,'version','CHANGED'):
                r=self.run_mock(None,resume=root);self.assertEqual(r['status'],'blocked-infrastructure')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'run';self.run_mock(root,mock_rate_limit_after=1)
            changed=root/'changed-plan.json';plan=json.loads(standing.PLAN.read_text());plan['per_attempt_output_cap']=4096;changed.write_text(json.dumps(plan))
            with patch.object(standing,'PLAN',changed):
                with self.assertRaises(ValueError): self.run_mock(None,resume=root)
    def test_global_request_bound_includes_rate_limited_invocations(self):
        plan,split,tasks=standing.validate_split();plan=plan|{'max_requests':1}
        with tempfile.TemporaryDirectory() as tmp,patch.object(standing,'validate_split',return_value=(plan,split,tasks)):
            root=Path(tmp)/'run';self.run_mock(root,mock_rate_limit_after=0)
            r=self.run_mock(None,resume=root)
            self.assertEqual(r['status'],'request-cap');self.assertEqual(r['attempts'],0)
    def test_concurrent_campaign_resume_is_rejected_before_requests(self):
        import fcntl
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'run';lock=root.parent/(root.name+'.campaign.lock')
            with lock.open('w') as file:
                fcntl.flock(file,fcntl.LOCK_EX|fcntl.LOCK_NB)
                with self.assertRaisesRegex(ValueError,'already running'): self.run_mock(root)

    def test_committed_reasoning_cap_amendment_applies_equally_to_all_arms(self):
        plan=json.loads(standing.PLAN.read_text())
        self.assertEqual(plan['per_attempt_output_cap'],8192);self.assertEqual(plan['trial_output_cap'],16384)
        self.assertEqual(plan['attempt_limit'],3);self.assertEqual(plan['spend_cap_usd'],20)
    def test_mock_campaign_never_reads_subscription_token_file(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(standing,'subscription_token',side_effect=AssertionError('real token read')):
            self.run_mock(Path(tmp)/'run')
    def test_all_mock_campaign_artifacts_redact_planted_oauth_and_api_tokens(self):
        c=client();c.preflight=lambda: {'mock':True,'echo':FAKE}
        events=response('not source # '+FAKE);proc=subprocess.CompletedProcess([],0,'\n'.join(map(json.dumps,events)),FAKE+' planted-api-secret')
        real_run=subprocess.run
        def no_live(argv,**kwargs):
            return proc if argv[0]=='/usr/bin/sandbox-exec' else real_run(argv,**kwargs)
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'CLAUDE_CODE_OAUTH_TOKEN':FAKE,'ANTHROPIC_API_KEY':'planted-api-secret'}),patch.object(standing,'Mock',return_value=c),patch.object(backend.subprocess,'run',no_live):
            root=Path(tmp)/'run';self.run_mock(root)
            for file in list(root.rglob('*'))+list(self.report_root.rglob('MOCK_STANDING_GENERATION*_DEV.*')):
                if file.is_file():
                    for secret in (FAKE,'planted-api-secret'):
                        self.assertNotIn(secret.encode(),file.read_bytes(),str(file))


class OfflinePreflightAndAccountingTests(TemporaryReports):
    def test_offline_preflight_with_private_fake_token_and_mock_cli_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);token=root/'fake-token';token.write_text(FAKE);token.chmod(0o600)
            def fake_run(argv,**kwargs):
                if '/usr/bin/head' in argv: return subprocess.CompletedProcess(argv,1,b'',b'denied')
                if '--version' in argv: return subprocess.CompletedProcess(argv,0,'MOCK-CLI\n','')
                self.assertIn('(deny network*)',argv[2])
                # A valid token makes the CLI contact the server before `init`; the
                # network-denied probe must run unauthenticated to observe isolation.
                self.assertNotIn('CLAUDE_CODE_OAUTH_TOKEN',kwargs['env'])
                self.assertNotIn(FAKE,json.dumps(kwargs['env']))
                return subprocess.CompletedProcess(argv,1,json.dumps(response()[0])+'\n',FAKE)
            with patch.dict(os.environ,{'NIL_CLAUDE_OAUTH_TOKEN_FILE':str(token)}),patch.object(backend.shutil,'which',return_value='/usr/bin/true'),patch.object(backend.subprocess,'check_output',return_value='MOCK-CLI'),patch.object(backend.subprocess,'run',fake_run):
                self.assertTrue(standing.preflight(root/'preflight'))
            self.assertEqual(json.loads((root/'preflight/isolation.json').read_text())['tools'],[])
            for file in (root/'preflight').rglob('*'):
                if file.is_file(): self.assertNotIn(FAKE.encode(),file.read_bytes())
    def test_accounting_probe_pause_resumes_without_repeating_completed_generation(self):
        calls=[];pause_once=[False]
        class Fake:
            version='MOCK-CLI'
            def __init__(self,model): self.secrets=backend.Secrets(FAKE)
            def preflight(self): return {'mock':True,'network_denied':True}
            def request(self,messages,budget,cap,folder):
                prompt=messages[0]['content'];calls.append(prompt)
                if 'Input-token accounting only.' in prompt and not pause_once[0]:
                    pause_once[0]=True
                    raise backend.BackendError('rate-limit','limit',0,{'input_tokens':0,'output_tokens':0})
                return dict(text='complete source',cost_usd=.01,input_tokens=100 if 'Language specification:' not in prompt else 200,
                            output_tokens=20,cached_input_tokens=0,cache_creation_tokens=0,fresh_input_tokens=100,model=MODEL,tool_calls=0)
        with tempfile.TemporaryDirectory() as tmp,patch.object(standing,'Claude',Fake),patch.object(standing,'publish_report'),patch.object(standing.application.oracle,'prepare'),patch.object(standing,'oracle',verdict):
            root=Path(tmp)/'run';r=standing.run(root)
            self.assertEqual(r['status'],'paused-rate-limit');self.assertEqual(r['attempts'],3)
            r=standing.run(resume=root)
            self.assertEqual(r['status'],'complete');self.assertEqual(r['attempts'],3)
            self.assertEqual(r['spec_marginal_input_tokens'],100);self.assertAlmostEqual(r['spent_usd'],.05)
            self.assertEqual(len(calls),6);self.assertEqual(r['config']['invocations'],6)
    def test_interrupted_request_journal_blocks_replay_instead_of_guessing_usage(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(standing.application.oracle,'prepare'),patch.object(standing.Mock,'request',side_effect=KeyboardInterrupt):
            root=Path(tmp)/'run'
            with self.assertRaises(KeyboardInterrupt): standing.run(root,mock=True)
            state=json.loads((root/'checkpoint.json').read_text())['state']
            self.assertIsNotNone(state['pending']);self.assertEqual(state['invocations'],1)
            with self.assertRaises(ValueError): standing.run(resume=root)
    def test_per_attempt_output_overrun_fails_attempt_without_stopping_campaign(self):
        # Live finding: the CLI auto-continued past max_tokens within one invocation
        # (two API turns, 10,735 output tokens against an 8,192 cap).
        original=standing.Mock.request;calls=[]
        def overrun_first(self,messages,budget,cap,folder):
            result=original(self,messages,budget,cap,folder);calls.append(messages)
            if len(calls)==1: result=result|dict(output_tokens=cap+1)
            return result
        with tempfile.TemporaryDirectory() as tmp,patch.object(standing.application.oracle,'prepare'),patch.object(standing.Mock,'request',overrun_first):
            r=standing.run(Path(tmp)/'run',mock=True)
            rows=[json.loads(x) for x in (Path(tmp)/'run/attempts.jsonl').read_text().splitlines()]
        self.assertEqual(r['status'],'complete')
        first=rows[0];self.assertEqual(first['taxonomy'],'budget');self.assertFalse(first['semantic_ok'])
        self.assertEqual(first['output_tokens'],8193)
        self.assertGreater(len(rows),1);self.assertEqual(rows[1]['trial'],first['trial']);self.assertEqual(rows[1]['attempt'],1)
        self.assertIn('exceeded the per-attempt output budget',calls[1][-1]['content'])
    def test_structured_refusal_is_classified_with_accounting(self):
        x=response();x.insert(1,dict(type='assistant',message=dict(stop_reason='refusal',
            stop_details=dict(type='refusal',category='reasoning_extraction'),content=[dict(type='text',text='API Error')])))
        x[-1].update(is_error=True,stop_reason='refusal')
        with self.assertRaises(backend.BackendError) as e: backend.inspect_stream(x,MODEL)
        self.assertEqual(e.exception.reason,'refusal');self.assertIn('reasoning_extraction',str(e.exception))
        self.assertEqual(e.exception.usage['output_tokens'],40);self.assertEqual(e.exception.cost,.01)
        # Generated text that merely mentions a refusal is not a refusal.
        y=response('I refuse to use a refusal stop_reason here')
        self.assertEqual(backend.inspect_stream(y,MODEL)['text'],'I refuse to use a refusal stop_reason here')
    def test_refusal_ends_trial_unsolved_without_stopping_campaign(self):
        original=standing.Mock.request;calls=[]
        def refuse_first(self,messages,budget,cap,folder):
            calls.append(messages)
            if len(calls)==1:
                raise backend.BackendError('refusal','Model safety refusal (category: reasoning_extraction)',.02,
                    dict(input_tokens=100,fresh_input_tokens=100,cached_input_tokens=0,cache_creation_tokens=0,output_tokens=500))
            return original(self,messages,budget,cap,folder)
        with tempfile.TemporaryDirectory() as tmp,patch.object(standing.application.oracle,'prepare'),patch.object(standing.Mock,'request',refuse_first):
            r=standing.run(Path(tmp)/'run',mock=True)
            rows=[json.loads(x) for x in (Path(tmp)/'run/attempts.jsonl').read_text().splitlines()]
        self.assertEqual(r['status'],'complete')
        self.assertEqual(rows[0]['taxonomy'],'refusal');self.assertFalse(rows[0]['semantic_ok']);self.assertEqual(rows[0]['output_tokens'],500)
        self.assertNotEqual(rows[1]['trial'],rows[0]['trial'])  # no repair turn after a refusal
    def test_refusal_with_unknown_accounting_still_fails_closed(self):
        def refuse(self,messages,budget,cap,folder): raise backend.BackendError('refusal','refused',None,None)
        with tempfile.TemporaryDirectory() as tmp,patch.object(standing.application.oracle,'prepare'),patch.object(standing.Mock,'request',refuse):
            r=standing.run(Path(tmp)/'run',mock=True)
        self.assertEqual(r['status'],'blocked-refusal')
    def test_rate_limit_output_overrun_is_retained_and_not_resumable(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(standing.application.oracle,'prepare'),patch.object(standing.Mock,'request',side_effect=backend.BackendError('rate-limit','limit',.01,{'input_tokens':0,'output_tokens':8193})):
            root=Path(tmp)/'run';r=standing.run(root,mock=True)
            self.assertEqual(r['status'],'budget-overrun');self.assertEqual(r['attempts'],0)
            self.assertEqual(r['dev'][0]['output_tokens'],8193)
            with self.assertRaises(ValueError): standing.run(resume=root)

if __name__=='__main__': unittest.main()
