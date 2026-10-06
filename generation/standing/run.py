"""Standing adapter for the frozen application generation/oracle harness."""
import argparse
import fcntl
from collections import Counter
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
SUITE=HERE.parents[1]
ROOT=SUITE.parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(SUITE/'generation/application'))
spec=importlib.util.spec_from_file_location('frozen_application',SUITE/'generation/application/run.py')
application=importlib.util.module_from_spec(spec);spec.loader.exec_module(application)
sys.path.insert(0,str(SUITE/'corpora/application-v5'))
from external_suite import load_tasks, external_expected
from oracles import expected as original_expected
from backend import BackendError, Claude, Secrets, subscription_token
import tiktoken

PLAN=HERE/'experiment.json';SPLIT=HERE/'split.json'
def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def read_json(path):return json.loads(path.read_text())
def norm(s):return re.sub(r'\s+','',s)
def examples():
    plan=read_json(SUITE/'generation/application/fewshot/experiment.json')
    result=[]
    for item in plan['examples']:
        source=(SUITE/item['source']).read_text()
        if digest(source)!=item['sha256']:raise ValueError('Fixed example changed')
        task=next(t for t in load_tasks() if t['id']==item['task'])
        result.append((task,source))
    return result


def validate_split():
    split=read_json(SPLIT);tasks=load_tasks();plan=read_json(PLAN)
    if digest(json.dumps(tasks,sort_keys=True))!=split['population_sha256']:raise ValueError('Task population changed')
    if digest((ROOT/'docs/language/EXPR_V5.md').read_text())!=split['spec_sha256']:raise ValueError('Specification changed')
    if hashlib.sha256((SUITE/'generation/application/fewshot/experiment.json').read_bytes()).hexdigest()!=split['fewshot_sha256']:raise ValueError('Example rule changed')
    held=set(split['held_out']);dev=set(split['dev']);ids={t['id'] for t in tasks}
    if len(held)!=24 or len(dev)>12 or held&dev or not (held|dev)<=ids:raise ValueError('Invalid split')
    if held&{t['id'] for t,_ in examples()}:raise ValueError('Held-out example leakage')
    counts=Counter(split['domains'][x] for x in held)
    if counts!={'original':8,'external':12,'algorithms':4}:raise ValueError('Stratification changed')
    return plan,split,{t['id']:t for t in tasks}


def guard_context(context,split,tasks):
    """Context excludes the current task too; its contract is appended only after this check."""
    for tid in split['held_out']:
        task=tasks[tid]
        if tid in context or task['prompt'] in context:
            raise ValueError('Held-out task in context: '+tid)
        # This audit reads frozen answers only to reject leakage, never inserts them into prompts.
        answer=(SUITE/'corpora/application-v5/programs'/f'{tid}.nil').read_text()
        if norm(answer) in norm(context):raise ValueError('Held-out solution in context: '+tid)


def make_prompt(arm,task,split,tasks):
    context=''
    if arm!='python':context='Language specification:\n'+(ROOT/'docs/language/EXPR_V5.md').read_text()
    if arm=='nil-fewshot':
        context+='\nFixed independent worked examples:\n'
        for t,source in examples():context+='\nExample: '+t['prompt']+'\nNIL source:\n'+source
    guard_context(context,split,tasks)
    contract=('Write a complete Python source file defining solve(input_path, output_path).' if arm=='python'
              else 'Write complete expr-v5 NIL source with entry function (s,s)=expression and i64 result.')
    contract+=(' Read the first path; write the second; return exactly the output byte length; emit no stdout; '
               'do not modify the input. Paths are relative filenames. Handle all stated valid inputs within '
               '100000 reference steps and 256 call frames. Return only the complete source.\nTask: '+task['prompt'])
    return context+'\n'+contract


def oracle(source,arm,task,folder):
    """Reuse the unchanged oracle and capture its real diagnostics/stages without changing answers."""
    observed=[];saved=application.oracle.subprocess.run
    def observe(*args,**kwargs):
        result=saved(*args,**kwargs);command=args[0] if args else kwargs.get('args',[])
        observed.append((list(map(str,command)),result));return result
    def expected(t,data,environment=None):
        return external_expected(t,data) if t.startswith('ex_') else original_expected(t,data,environment)
    with patch.object(application.oracle,'expected',expected),patch.object(application.oracle.subprocess,'run',observe):
        verdict=application.oracle.evaluate(source,'python' if arm=='python' else 'expr-v5',task,folder)
    code=None;trap=False;o0=o2=None;execution_diagnostic=None
    for command,result in observed:
        stderr=result.stderr.decode('utf8','replace') if isinstance(result.stderr,bytes) else result.stderr or ''
        stdout=result.stdout.decode('utf8','replace') if isinstance(result.stdout,bytes) else result.stdout or ''
        match=re.search(r'\bE\d{3}\b',stderr+'\n'+stdout)
        if match:code=match[0]
        if 'build' in command:
            if '-O0' in command:o0=result.returncode==0
            if '-O2' in command:o2=result.returncode==0
        if any('candidate-O' in x for x in command) and result.returncode:
            trap=True;execution_diagnostic=stderr[:800]
    reason=verdict['failure_reason']
    taxonomy=('correct' if verdict['semantic_ok'] else 'parse' if reason=='parse' else 'type' if reason=='type'
              else 'compile' if reason=='backend' else 'budget' if code in ('E010','E011') or reason=='timeout'
              else 'trap' if trap else 'infrastructure' if reason=='checker' else 'wrong-answer')
    if execution_diagnostic and taxonomy in ('trap','budget'):
        verdict['feedback']='Native execution diagnostic: '+execution_diagnostic+' Return a corrected complete program.'
    return verdict|dict(taxonomy=taxonomy,diagnostic_code=code,compile_o0=o0,compile_o2=o2)


def features(source,verdict):
    # Descriptive associations, not claims these constructs caused an error.
    found=[]
    for name,pattern in [('loop',r'@\('),('callbacks',r'\^|&|\[i:'),('records',r'\brecord\b|\.[a-zA-Z]'),
                         ('intrinsic-names',r'!\w+'),('modules',r'!\d+\.'),('each',r'!each\(')]:
        if re.search(pattern,source):found.append(name)
    if verdict['taxonomy']=='parse' and not found:found=['foreign-or-missing-syntax']
    return found


class Mock:
    version='MOCK-NOT-A-MODEL';auth_method='none';model='SYNTHETIC'
    def preflight(self):return {'mock':True,'no_live_requests':True}
    def request(self,messages,budget,cap,folder):
        task=self.task;arm=self.arm
        source=('not source' if self.attempt==0 else
                (SUITE/'corpora/application-v5/programs'/f"{task['id']}.{'py' if arm=='python' else 'nil'}").read_text())
        secrets=campaign_secrets()
        secrets.write(folder/'request.json',dict(mock=True,messages=messages,timestamp_utc=utc()),True)
        response=dict(text=source,input_tokens=100,cached_input_tokens=0,cache_creation_tokens=0,
                      fresh_input_tokens=100,output_tokens=20,cost_usd=0.001,tool_calls=0,
                      model='SYNTHETIC',wall_seconds=0.0,mock=True)
        response=secrets.clean(response)
        secrets.write(folder/'response.json',response,True);return response


def aggregate(rows,calibration=None,pauses=()):
    result=[]
    for arm in ['python','nil-spec','nil-fewshot']:
        rs=[r for r in rows if r['arm']==arm];ps=[r for r in pauses if r.get('arm')==arm]
        trials={r['trial'] for r in rs+ps}
        solves={r['trial'] for r in rs if r.get('semantic_ok')};count=len(trials)
        known=bool(rs+ps) and all(type(r.get('input_tokens'))==int and type(r.get('output_tokens'))==int for r in rs+ps)
        inputs=sum(r['input_tokens'] for r in rs+ps) if known else None
        outputs=sum(r['output_tokens'] for r in rs+ps) if known else None
        repairs=sum(r['output_tokens'] for r in rs+ps if r['attempt']>0) if known else None
        amortized=inputs if arm=='python' else (inputs-calibration*max(0,len(rs)+sum(p.get('input_tokens',0)>0 for p in ps)-count) if known and calibration is not None else None)
        if amortized is not None and amortized<0:amortized=None
        def rate(field):
            # All attempts are denominator; unknown evidence is not a pass.
            return sum(r.get(field) is True for r in rs)/len(rs) if rs else None
        result.append(dict(arm=arm,trials=count,attempts=len(rs),solves=len(solves),solve_rate=len(solves)/count if count else None,
                           first_attempt_solves=sum(r.get('semantic_ok',False) for r in rs if r['attempt']==0),
                           first_attempt_solve_rate=sum(r.get('semantic_ok',False) for r in rs if r['attempt']==0)/count if count else None,
                           parse_rate=rate('parse_ok'),compile_o0_rate=rate('compile_o0') if arm!='python' else None,compile_o2_rate=rate('compile_o2') if arm!='python' else None,
                           type_rate=rate('typecheck_ok') if arm!='python' else None,input_tokens_full=inputs,input_tokens_spec_amortized=amortized,
                           output_tokens=outputs,repair_output_tokens=repairs,
                           repair_input_tokens=sum(r['input_tokens'] for r in rs+ps if r['attempt']>0) if known else None,
                           unknown_parse_attempts=sum(r.get('parse_ok') is None for r in rs),
                           cached_input_tokens=sum(r.get('cached_input_tokens',0) for r in rs+ps) if known else None,
                           cache_creation_tokens=sum(r.get('cache_creation_tokens',0) for r in rs+ps) if known else None,
                           output_tcr=outputs/len(solves) if known and solves else None,
                           total_tcr=(inputs+outputs)/len(solves) if known and solves else None,
                           amortized_total_tcr=(amortized+outputs)/len(solves) if known and solves and amortized is not None else None,
                           cost_usd=sum(r['cost_usd'] for r in rs+ps if r.get('cost_usd') is not None),
                           wall_seconds=sum(r.get('wall_seconds',0) for r in rs+ps),transport_pauses=len(ps),cost_basis='notional subscription usage',
                           failures=dict(Counter(r['taxonomy'] for r in rs)),
                           feature_associations=dict(Counter(f for r in rs if not r.get('semantic_ok') for f in r.get('features',[])))))
    return result


def bootstrap(rows,tasks,calibration=None,pauses=()):
    import random
    rng=random.Random(37037)
    metrics=['parse_rate','compile_o0_rate','compile_o2_rate','solve_rate','first_attempt_solve_rate',
             'input_tokens_full','input_tokens_spec_amortized','output_tokens','repair_output_tokens',
             'repair_input_tokens','output_tcr','total_tcr','amortized_total_tcr','cost_usd','wall_seconds']
    arms=['python','nil-spec','nil-fewshot']
    samples={(a,m):[] for a in arms for m in metrics};diffs={(a,m):[] for a in arms[1:] for m in metrics}
    grouped={t:[r for r in rows if r['task']==t] for t in tasks}
    for _ in range(2000):
        draw=[];pause_draw=[]
        for j,t in enumerate(rng.choices(tasks,k=len(tasks))):
            draw.extend(r|{'trial':str(j)+'/'+r['trial']} for r in grouped[t])
            pause_draw.extend(r|{'trial':str(j)+'/'+r['trial']} for r in pauses if r.get('task')==t)
        ag={x['arm']:x for x in aggregate(draw,calibration,pause_draw)}
        for arm in arms:
            for m in metrics:
                v=ag[arm].get(m)
                if v is not None:samples[arm,m].append(v)
                if arm!='python' and v is not None and ag['python'].get(m) is not None:
                    diffs[arm,m].append(v-ag['python'][m])
    def interval(v):
        if not v:return {'interval':None,'defined_resamples':0}
        v=sorted(v);return {'interval':[v[int(.025*(len(v)-1))],v[int(.975*(len(v)-1))]],'defined_resamples':len(v)}
    return {'method':'2000 paired task-cluster resamples; all repairs/replicates retained; undefined TCR samples omitted and counted',
            'arm_intervals':{a:{m:interval(samples[a,m]) for m in metrics} for a in arms},
            'nil_minus_python':{a:{m:interval(diffs[a,m]) for m in metrics} for a in arms[1:]}}


def render(output,config,rows,status,spent,calibration,final=True,pauses=(),events=()):
    scored=[r for r in rows if r['split']=='held-out']
    result=dict(mock=config['mock'],status=status,config=config,scored=aggregate(scored,calibration,[p for p in pauses if p['split']=='held-out']),
                dev=aggregate([r for r in rows if r['split']=='dev'],pauses=[p for p in pauses if p['split']=='dev']),per_task={t:aggregate([r for r in scored if r['task']==t],calibration,[p for p in pauses if p.get('task')==t]) for t in config['held_out']},
                paired_intervals=bootstrap(scored,config['held_out'],calibration,pauses) if final and scored else {},
                spec_marginal_input_tokens=calibration,spent_usd=spent,cost_basis='notional subscription usage',attempts=len(rows),transport_pauses=list(pauses),campaign_events=list(events),
                unknown_cost_attempts=sum(r.get('cost_usd') is None for r in rows),unknown_cost_pauses=sum(p.get('cost_usd') is None for p in pauses),
                note='Synthetic mock is not model evidence; partial/blocked cells are not fabricated zero solves. TCR undefined at zero solves.')
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    text='# Standing generation evaluation\n\n'+('**SYNTHETIC MOCK — no model result.**' if config['mock'] else '**'+status+'**')+'\n\n'
    text+='| Arm | Trials | Solves | Full input | Output | Output TCR | Total TCR |\n|---|---:|---:|---:|---:|---:|---:|\n'
    for a in result['scored']:text+='| '+' | '.join(str(a[k]) for k in ['arm','trials','solves','input_tokens_full','output_tokens','output_tcr','total_tcr'])+' |\n'
    text+=f'\nReported notional spend: ${spent:.6f}. Status: {status}. See report.json for complete per-task vector, dev data, taxonomy, unknowns and paired intervals.\n'
    (output/'report.md').write_text(text);return result


def utc(): return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())


def atomic(path, value, secrets):
    data=json.dumps(secrets.clean(value),sort_keys=True,indent=2)+'\n'
    temporary=path.with_suffix(path.suffix+'.tmp')
    with temporary.open('w') as file:
        file.write(data);file.flush();os.fsync(file.fileno())
    os.replace(temporary,path)


def persist(output,state,secrets):
    # checkpoint is authoritative; projections can be rebuilt after a crash.
    safe=secrets.clean(state)
    atomic(output/'checkpoint.json',dict(state=safe,sha256=digest(json.dumps(safe,sort_keys=True))),secrets)
    secrets.write(output/'attempts.jsonl',''.join(json.dumps(r,sort_keys=True)+'\n' for r in safe['rows']))


def campaign_secrets():
    values=[os.environ.get('ANTHROPIC_API_KEY'),os.environ.get('CLAUDE_CODE_OAUTH_TOKEN')]
    # Mock campaigns never open an OAuth file. Only the live transport reads it.
    return Secrets(*values)


def matrix(plan,split,phase):
    cells=[]
    ids=split['held_out'] if phase=='held-out' else [plan['dev_task']]
    for index,tid in enumerate(ids):
        for replicate in plan['replicates'] if phase=='held-out' else plan['dev_replicates']:
            arms=plan['arms'];off=(index+replicate)%len(arms)
            cells.extend(dict(task=tid,replicate=replicate,arm=arm,trial=f'{tid}/{replicate}/{arm}')
                         for arm in arms[off:]+arms[:off])
    return cells


def run(output=None,mock=False,phase='dev',prior=None,resume=None,mock_rate_limit_after=None):
    target=resume if resume is not None else output
    if target is None: raise ValueError('--output or --resume is required')
    target=target.expanduser().resolve()
    if target.is_relative_to(ROOT): raise ValueError('Output must be outside checkout')
    target.parent.mkdir(parents=True,exist_ok=True)
    # A sibling lock survives crashes and prevents concurrent resumes/replays.
    fd=os.open(target.parent/(target.name+'.campaign.lock'),os.O_CREAT|os.O_RDWR,0o600)
    with os.fdopen(fd,'r+') as lock:
        try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: raise ValueError('Campaign is already running') from None
        return _run(output,mock,phase,prior,resume,mock_rate_limit_after)


def _run(output=None,mock=False,phase='dev',prior=None,resume=None,mock_rate_limit_after=None):
    started=time.perf_counter();plan,split,tasks=validate_split();secrets=campaign_secrets()
    if mock_rate_limit_after is not None and not mock: raise ValueError('Synthetic pauses require --mock')
    hashes=dict(plan_sha256=hashlib.sha256(PLAN.read_bytes()).hexdigest(),
                split_sha256=hashlib.sha256(SPLIT.read_bytes()).hexdigest(),spec_sha256=split['spec_sha256'],
                compiler_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                benchmark_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=SUITE,text=True).strip(),
                initial_prompt_hashes={tid:{arm:digest(json.dumps([{'role':'user','content':make_prompt(arm,tasks[tid],split,tasks)}],sort_keys=True))
                                          for arm in plan['arms']} for tid in split['held_out']+split['dev']})
    if resume is not None:
        if output is not None: raise ValueError('Use --resume alone, not --output')
        output=resume.expanduser().resolve()
        if output.is_relative_to(ROOT): raise ValueError('Output must be outside checkout')
        checkpoint=read_json(output/'checkpoint.json');state=checkpoint['state']
        if digest(json.dumps(state,sort_keys=True))!=checkpoint['sha256']: raise ValueError('Checkpoint journal integrity failure')
        if any(state['config'].get(k)!=v for k,v in hashes.items()): raise ValueError('Frozen campaign revision, split, spec or prompt changed')
        if state['pending'] or state['status']!='paused-rate-limit': raise ValueError('Only a known-accounting rate pause can resume; unresolved in-flight requests fail closed')
        mock=state['config']['mock'];phase=state['config']['phase']
        if state['mock_pause_after'] is not None and not mock: raise ValueError('Invalid live synthetic pause')
        state['events'].append(dict(type='resume',timestamp_utc=utc(),invocations=state['invocations']))
        state['status']='complete'
    else:
        if output is None: raise ValueError('--output is required for a new campaign')
        output=output.expanduser().resolve()
        if output.is_relative_to(ROOT) or output.exists(): raise ValueError('Use a fresh output outside checkout')
        spent=0.0;calibration=None
        if phase=='held-out' and not mock:
            if prior is None: raise ValueError('Held-out requires prior DEV report and committed cost forecast')
            prev=read_json(prior/'report.json');forecast=read_json(HERE/'cost-forecast.json')
            if (prev['mock'] or prev['status']!='complete' or prev['config']['phase']!='dev' or
                prev['config']['model']!=plan['model'] or prev['config']['plan_sha256']!=hashes['plan_sha256'] or
                prev['config']['split_sha256']!=hashes['split_sha256'] or
                forecast['dev_report_sha256']!=hashlib.sha256((prior/'report.json').read_bytes()).hexdigest()):
                raise ValueError('Invalid DEV/forecast provenance')
            if subprocess.check_output(['git','show','HEAD:generation/standing/cost-forecast.json'],cwd=SUITE)!=(HERE/'cost-forecast.json').read_bytes():
                raise ValueError('Cost forecast must be committed')
            spent=prev['spent_usd'];calibration=prev.get('spec_marginal_input_tokens')
        config=plan|hashes|dict(mock=mock,phase=phase,held_out=split['held_out'],started_at_utc=utc(),python_version=sys.version,cli_version=None)
        output.mkdir(parents=True)
        state=dict(config=config,status='complete',spent_usd=spent,calibration=calibration,rows=[],pauses=[],events=[],
                   cursor=0,attempt=0,used=0,messages=None,accounting=[],accounting_cursor=0,pending=None,
                   invocations=prev['config'].get('invocations',0) if phase=='held-out' and not mock else 0,
                   mock_pause_after=mock_rate_limit_after,mock_pause_done=False)
        persist(output,state,secrets)
    backend=None;config=state['config'];cells=matrix(plan,split,phase)
    try:
        backend=Mock() if mock else Claude(plan['model'])
        if not mock: secrets=backend.secrets
        if config['cli_version'] is not None and config['cli_version']!=backend.version:
            raise BackendError('infrastructure','CLI version changed since campaign started')
        config['cli_version']=backend.version
        if resume is None and phase=='held-out' and not mock and prev['config']['cli_version']!=backend.version:
            raise BackendError('infrastructure','CLI version changed since DEV')
        proof=backend.preflight();secrets.write(output/'isolation.json',proof,True)
        if hasattr(backend,'probe_evidence'): secrets.write(output/'isolation-probe.json',backend.probe_evidence,True)
        application.oracle.prepare()
        while state['status']=='complete':
            accounting=state['cursor']>=len(cells)
            if accounting and (mock or phase!='dev' or state['accounting_cursor']>=2): break
            if not accounting:
                cell=cells[state['cursor']];tid=cell['task'];arm=cell['arm'];task=tasks[tid]
                if state['messages'] is None: state['messages']=[{'role':'user','content':make_prompt(arm,task,split,tasks)}]
                if state['used']>=plan['trial_output_cap']:
                    state['events'].append(dict(type='trial-token-exhaustion',trial=cell['trial'],timestamp_utc=utc()))
                    state.update(cursor=state['cursor']+1,attempt=0,used=0,messages=None);persist(output,state,secrets);continue
                messages=state['messages'];cap=min(plan['per_attempt_output_cap'],plan['trial_output_cap']-state['used'])
                guard_context('\n'.join(m['content'] for m in messages),split|{'held_out':[x for x in split['held_out'] if x!=tid]},tasks)
                row=cell|dict(split=phase,attempt=state['attempt'],prompt_sha256=digest(json.dumps(messages,sort_keys=True)))
                if mock: backend.task=task;backend.arm=arm;backend.attempt=state['attempt']
                label=f"{tid}-{cell['replicate']}-{arm}-{state['attempt']}"
            else:
                index=state['accounting_cursor']
                prefix='' if index==0 else 'Language specification:\n'+(ROOT/'docs/language/EXPR_V5.md').read_text()+'\n'
                messages=[{'role':'user','content':prefix+'Input-token accounting only. Reply with exactly 0.'}]
                cap=plan['per_attempt_output_cap'];label=f'accounting-{index}'
                row=dict(split='accounting',attempt=0)
            if state['spent_usd']+plan['request_reservation_usd']>plan['spend_cap_usd']:
                state['status']='spend-cap';break
            if state['invocations']>=plan['max_requests']:
                state['status']='request-cap';break
            invocation=state['invocations'];state['invocations']+=1
            folder=output/(label if not (output/label).exists() else f'{label}-invocation-{invocation}')
            folder.mkdir()
            state['pending']=dict(invocation=invocation,folder=folder.name,prompt_sha256=digest(json.dumps(messages,sort_keys=True)),timestamp_utc=utc())
            persist(output,state,secrets)
            try:
                if mock and not state['mock_pause_done'] and state['mock_pause_after']==len(state['rows']):
                    state['mock_pause_done']=True
                    secrets.write(folder/'request.json',dict(mock=True,messages=messages),True)
                    raise BackendError('rate-limit','Synthetic subscription pause',0,dict(input_tokens=0,output_tokens=0))
                response=secrets.clean(backend.request(messages,plan['request_reservation_usd'],cap,folder))
            except BackendError as error:
                if error.cost is not None: state['spent_usd']+=error.cost
                if error.reason=='rate-limit':
                    pause=row|dict(type='rate-limit',timestamp_utc=utc(),invocation=invocation,cost_usd=error.cost,
                                   input_tokens=None,output_tokens=None,error=secrets.clean(str(error)))
                    if error.usage is not None: pause.update(error.usage)
                    state['pauses'].append(pause)
                    if error.cost is None or error.usage is None:
                        state['status']='blocked-rate-limit-accounting'
                    else:
                        if not accounting: state['used']+=error.usage['output_tokens']
                        state['pending']=None;state['status']='paused-rate-limit'
                        if error.usage['output_tokens']>cap or state['spent_usd']>plan['spend_cap_usd']: state['status']='budget-overrun'
                    persist(output,state,secrets);break
                if error.reason=='refusal' and not accounting and error.cost is not None and error.usage is not None:
                    # A safety refusal ends the trial unsolved: charged in full, no repair turn
                    # (resending the same conversation invites the same refusal), campaign continues.
                    state['rows'].append(row|error.usage|dict(taxonomy='refusal',semantic_ok=False,
                                                              error=secrets.clean(str(error)),cost_usd=error.cost))
                    print(cell['trial'],state['attempt'],'refusal',flush=True)
                    state['used']+=error.usage['output_tokens']
                    state.update(cursor=state['cursor']+1,attempt=0,used=0,messages=None)
                    if state['spent_usd']>plan['spend_cap_usd']: state['status']='budget-overrun'
                    state['pending']=None;persist(output,state,secrets);continue
                if not accounting:
                    state['rows'].append(row|dict(taxonomy=error.reason,semantic_ok=False,error=secrets.clean(str(error)),
                                                  cost_usd=error.cost,input_tokens=None,output_tokens=None))
                state['status']='blocked-'+error.reason
                # This stopped request is not resumable, even if cost is known.
                persist(output,state,secrets);break
            state['spent_usd']+=response['cost_usd']
            if accounting:
                state['accounting'].append({k:v for k,v in response.items() if k!='text'})
                state['accounting_cursor']+=1
                if len(state['accounting'])==2:
                    a,b=(r['input_tokens'] for r in state['accounting'])
                    if b>=a: state['calibration']=b-a
                secrets.write(output/'accounting.json',state['accounting'],True)
            else:
                state['used']+=response['output_tokens']
                source=application.extract_source(response['text']);secrets.write(folder/'source.txt',source)
                if state['spent_usd']>plan['spend_cap_usd']:
                    verdict=dict(taxonomy='budget',semantic_ok=False,feedback='Backend exceeded frozen budget; campaign stopped.');state['status']='budget-overrun'
                elif response['output_tokens']>cap:
                    # The CLI can auto-continue past max_tokens within one invocation (several API
                    # turns), so one attempt may exceed the per-attempt cap. That is a failed attempt,
                    # charged in full and never scored, not a campaign stop (ADR 037 stop policy).
                    verdict=dict(taxonomy='budget',semantic_ok=False,
                                 feedback='Your previous response exceeded the per-attempt output budget, so it was not evaluated.')
                else:
                    verdict=secrets.clean(oracle(source,arm,task,folder))
                    if verdict['taxonomy']=='infrastructure': state['status']='blocked-oracle-infrastructure'
                row.update({k:v for k,v in response.items() if k!='text'},**verdict,features=features(source,verdict),
                           source_tokens={n:len(tiktoken.get_encoding(n).encode(source)) for n in ['cl100k_base','o200k_base']},
                           source_bytes=len(source.encode()),source_characters=len(source))
                state['rows'].append(row);print(cell['trial'],state['attempt'],row['taxonomy'],flush=True)
                if row.get('semantic_ok') or state['used']>=plan['trial_output_cap'] or state['attempt']+1>=plan['attempt_limit']:
                    state.update(cursor=state['cursor']+1,attempt=0,used=0,messages=None)
                else:
                    state['messages'].extend([{'role':'assistant','content':response['text']},
                                              {'role':'user','content':row['feedback']+' Return only the full source program.'}])
                    state['attempt']+=1
            if (accounting and response['output_tokens']>cap) or state['spent_usd']>plan['spend_cap_usd']: state['status']='budget-overrun'
            state['pending']=None;persist(output,state,secrets)
    except (BackendError,ValueError,RuntimeError) as error:
        if backend is not None and hasattr(backend,'probe_evidence'): secrets.write(output/'isolation-probe.json',backend.probe_evidence,True)
        state['status']='blocked-'+getattr(error,'reason','infrastructure')
        secrets.write(output/'blocked.txt',str(error)+'\n')
    config['invocations']=state['invocations'];config['elapsed_total_seconds']=config.get('elapsed_total_seconds',0)+time.perf_counter()-started
    persist(output,state,secrets)
    result=render(output,config,state['rows'],state['status'],state['spent_usd'],state['calibration'],
                  pauses=state['pauses'],events=state['events'])
    publish_report(output,mock,phase,secrets)
    print('Status:',state['status'],'attempts:',len(state['rows']),'notional spend:',state['spent_usd'],flush=True)
    return result


def publish_report(output,mock,phase,secrets):
    report_dir=SUITE/'reports'/time.strftime('%Y-%m-%d',time.gmtime());report_dir.mkdir(parents=True,exist_ok=True)
    label=('MOCK_' if mock else '')+'STANDING_GENERATION_PRO_'+phase.upper().replace('-','_')
    secrets.write(report_dir/(label+'.json'),(output/'report.json').read_text())
    secrets.write(report_dir/(label+'.md'),(output/'report.md').read_text())


def preflight(output):
    output=output.expanduser().resolve()
    if output.exists() or output.is_relative_to(ROOT): raise ValueError('Use a fresh output outside checkout')
    output.mkdir(parents=True);secrets=campaign_secrets();backend=None
    try:
        plan,_,_=validate_split();backend=Claude(plan['model']);secrets=backend.secrets
        proof=backend.preflight();secrets.write(output/'isolation.json',proof,True)
        secrets.write(output/'isolation-probe.json',backend.probe_evidence,True)
        print('Offline preflight passed; network denied; no model request made.');return True
    except BackendError as error:
        if backend is not None and hasattr(backend,'probe_evidence'): secrets.write(output/'isolation-probe.json',backend.probe_evidence,True)
        secrets.write(output/'blocked.txt',str(error)+'\n');print('Offline preflight blocked:',error.reason);return False


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path)
    p.add_argument('--preflight',action='store_true',help='Network-denied isolation/auth-file startup only; no generation')
    p.add_argument('--resume',type=Path);p.add_argument('--mock',action='store_true')
    p.add_argument('--mock-rate-limit-after',type=int,help='Synthetic pause after N completed attempts; mock only')
    p.add_argument('--phase',choices=['dev','held-out'],default='dev');p.add_argument('--prior',type=Path)
    a=p.parse_args()
    if a.preflight:
        if a.resume or a.mock or a.output is None: p.error('--preflight requires --output only')
        sys.exit(0 if preflight(a.output) else 2)
    r=run(a.output,a.mock,a.phase,a.prior,a.resume,a.mock_rate_limit_after)
    if r['status']=='paused-rate-limit': sys.exit(75)
    if r['status']!='complete': sys.exit(2)
