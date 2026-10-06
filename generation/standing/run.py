"""Standing adapter for the frozen application generation/oracle harness."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
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
from backend import BackendError, Claude
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
        (folder/'request.json').write_text(json.dumps({'mock':True,'messages':messages,'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())},indent=2))
        response=dict(text=source,input_tokens=100,cached_input_tokens=0,cache_creation_tokens=0,
                      fresh_input_tokens=100,output_tokens=20,cost_usd=0.001,tool_calls=0,
                      model='SYNTHETIC',wall_seconds=0.0,mock=True)
        (folder/'response.json').write_text(json.dumps(response));return response


def aggregate(rows,calibration=None):
    result=[]
    for arm in ['python','nil-spec','nil-fewshot']:
        rs=[r for r in rows if r['arm']==arm];trials={r['trial'] for r in rs}
        solves={r['trial'] for r in rs if r.get('semantic_ok')};count=len(trials)
        known=bool(rs) and all(type(r.get('input_tokens'))==int and type(r.get('output_tokens'))==int for r in rs)
        inputs=sum(r['input_tokens'] for r in rs) if known else None
        outputs=sum(r['output_tokens'] for r in rs) if known else None
        repairs=sum(r['output_tokens'] for r in rs if r['attempt']>0) if known else None
        amortized=inputs if arm=='python' else (inputs-calibration*(len(rs)-count) if known and calibration is not None else None)
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
                           repair_input_tokens=sum(r['input_tokens'] for r in rs if r['attempt']>0) if known else None,
                           unknown_parse_attempts=sum(r.get('parse_ok') is None for r in rs),
                           cached_input_tokens=sum(r.get('cached_input_tokens',0) for r in rs) if known else None,
                           cache_creation_tokens=sum(r.get('cache_creation_tokens',0) for r in rs) if known else None,
                           output_tcr=outputs/len(solves) if known and solves else None,
                           total_tcr=(inputs+outputs)/len(solves) if known and solves else None,
                           amortized_total_tcr=(amortized+outputs)/len(solves) if known and solves and amortized is not None else None,
                           cost_usd=sum(r['cost_usd'] for r in rs if r.get('cost_usd') is not None),
                           wall_seconds=sum(r.get('wall_seconds',0) for r in rs),
                           failures=dict(Counter(r['taxonomy'] for r in rs)),
                           feature_associations=dict(Counter(f for r in rs if not r.get('semantic_ok') for f in r.get('features',[])))))
    return result


def bootstrap(rows,tasks,calibration=None):
    import random
    rng=random.Random(37037)
    metrics=['parse_rate','compile_o0_rate','compile_o2_rate','solve_rate','first_attempt_solve_rate',
             'input_tokens_full','input_tokens_spec_amortized','output_tokens','repair_output_tokens',
             'repair_input_tokens','output_tcr','total_tcr','amortized_total_tcr','cost_usd','wall_seconds']
    arms=['python','nil-spec','nil-fewshot']
    samples={(a,m):[] for a in arms for m in metrics};diffs={(a,m):[] for a in arms[1:] for m in metrics}
    grouped={t:[r for r in rows if r['task']==t] for t in tasks}
    for _ in range(2000):
        draw=[]
        for j,t in enumerate(rng.choices(tasks,k=len(tasks))):
            draw.extend(r|{'trial':str(j)+'/'+r['trial']} for r in grouped[t])
        ag={x['arm']:x for x in aggregate(draw,calibration)}
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


def render(output,config,rows,status,spent,calibration,final=True):
    scored=[r for r in rows if r['split']=='held-out']
    result=dict(mock=config['mock'],status=status,config=config,scored=aggregate(scored,calibration),
                dev=aggregate([r for r in rows if r['split']=='dev']),per_task={t:aggregate([r for r in scored if r['task']==t],calibration) for t in config['held_out']},
                paired_intervals=bootstrap(scored,config['held_out'],calibration) if final and scored else {},
                spec_marginal_input_tokens=calibration,spent_usd=spent,attempts=len(rows),
                unknown_cost_attempts=sum(r.get('cost_usd') is None for r in rows),
                note='Synthetic mock is not model evidence; partial/blocked cells are not fabricated zero solves. TCR undefined at zero solves.')
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    text='# Standing generation evaluation\n\n'+('**SYNTHETIC MOCK — no model result.**' if config['mock'] else '**'+status+'**')+'\n\n'
    text+='| Arm | Trials | Solves | Full input | Output | Output TCR | Total TCR |\n|---|---:|---:|---:|---:|---:|---:|\n'
    for a in result['scored']:text+='| '+' | '.join(str(a[k]) for k in ['arm','trials','solves','input_tokens_full','output_tokens','output_tcr','total_tcr'])+' |\n'
    text+=f'\nReported notional spend: ${spent:.6f}. Status: {status}. See report.json for complete per-task vector, dev data, taxonomy, unknowns and paired intervals.\n'
    (output/'report.md').write_text(text);return result


def run(output,mock=False,phase='dev',prior=None):
    plan,split,tasks=validate_split();output=output.expanduser().resolve()
    if output.is_relative_to(ROOT) or output.exists():raise ValueError('Use a fresh output outside checkout')
    if phase=='held-out' and not mock:
        if prior is None:raise ValueError('Held-out requires prior DEV report and committed cost forecast')
        prev=read_json(prior/'report.json');forecast=read_json(HERE/'cost-forecast.json')
        if prev['mock'] or prev['status']!='complete' or forecast['dev_report_sha256']!=hashlib.sha256((prior/'report.json').read_bytes()).hexdigest():raise ValueError('Invalid dev/forecast provenance')
        committed=subprocess.check_output(['git','show','HEAD:generation/standing/cost-forecast.json'],cwd=SUITE)
        if committed!= (HERE/'cost-forecast.json').read_bytes():raise ValueError('Cost forecast must be committed')
        spent=prev['spent_usd']
    else:spent=0.0
    backend=None
    output.mkdir(parents=True);rows=[];status='complete';calibration=(prev.get('spec_marginal_input_tokens') if phase=='held-out' and not mock else None)
    config=plan|dict(mock=mock,phase=phase,held_out=split['held_out'],split_sha256=hashlib.sha256(SPLIT.read_bytes()).hexdigest(),
                     spec_sha256=split['spec_sha256'],python_version=sys.version,plan_sha256=hashlib.sha256(PLAN.read_bytes()).hexdigest(),compiler_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                     benchmark_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=SUITE,text=True).strip(),cli_version=None)
    try:
        backend=Mock() if mock else Claude(plan['model']);config['cli_version']=backend.version
        proof=backend.preflight();(output/'isolation.json').write_text(json.dumps(proof,indent=2)+'\n')
        if hasattr(backend,'probe_evidence'):(output/'isolation-probe.json').write_text(json.dumps(backend.probe_evidence,indent=2)+'\n')
        application.oracle.prepare()
        ids=split['held_out'] if phase=='held-out' else [plan['dev_task']]
        reps=plan['replicates'] if phase=='held-out' else plan['dev_replicates']
        with (output/'attempts.jsonl').open('x') as log:
            stop=False
            for index,tid in enumerate(ids):
                if stop:break
                for replicate in reps:
                    if stop:break
                    arms=plan['arms'];off=(index+replicate)%len(arms)
                    for arm in arms[off:]+arms[:off]:
                        if stop:break
                        task=tasks[tid];prompt=make_prompt(arm,task,split,tasks)
                        messages=[{'role':'user','content':prompt}];used=0
                        trial=f'{tid}/{replicate}/{arm}'
                        for attempt in range(plan['attempt_limit']):
                            if spent+plan['request_reservation_usd']>plan['spend_cap_usd']:
                                status='spend-cap';stop=True;break
                            folder=output/f'{tid}-{replicate}-{arm}-{attempt}';folder.mkdir()
                            row=dict(trial=trial,task=tid,replicate=replicate,arm=arm,split=phase,attempt=attempt,prompt_sha256=digest(json.dumps(messages,sort_keys=True)))
                            if mock:backend.task=task;backend.arm=arm;backend.attempt=attempt
                            try:
                                # The current contract/own generated repair is allowed; other held-out material is not.
                                guard_context('\n'.join(m['content'] for m in messages),split|{'held_out':[x for x in split['held_out'] if x!=tid]},tasks)
                                response=backend.request(messages,plan['request_reservation_usd'],min(plan['per_attempt_output_cap'],plan['trial_output_cap']-used),folder)
                                spent+=response['cost_usd'];used+=response['output_tokens']
                                source=application.extract_source(response['text']);(folder/'source.txt').write_text(source)
                                if spent>plan['spend_cap_usd'] or response['output_tokens']>plan['per_attempt_output_cap'] or used>plan['trial_output_cap']:
                                    verdict=dict(taxonomy='budget',semantic_ok=False,feedback='Backend exceeded the frozen budget; campaign stopped.');status='budget-overrun';stop=True
                                else:
                                    verdict=oracle(source,arm,task,folder)
                                    if verdict['taxonomy']=='infrastructure':status='blocked-oracle-infrastructure';stop=True
                                row.update({k:v for k,v in response.items() if k!='text'},**verdict,
                                           features=features(source,verdict),source_tokens={n:len(tiktoken.get_encoding(n).encode(source)) for n in ['cl100k_base','o200k_base']},
                                           source_bytes=len(source.encode()),source_characters=len(source))
                            except ValueError as error:
                                row.update(taxonomy='split-integrity',semantic_ok=False,error=str(error),cost_usd=0,input_tokens=None,output_tokens=None)
                                status='blocked-split-integrity';stop=True
                            except BackendError as error:
                                if error.cost is not None:spent+=error.cost
                                row.update(taxonomy=error.reason,semantic_ok=False,error=str(error),cost_usd=error.cost,
                                           input_tokens=None,output_tokens=None)
                                status='blocked-'+error.reason;stop=True
                            log.write(json.dumps(row)+'\n');log.flush();rows.append(row)
                            (output/'checkpoint.json').write_text(json.dumps(dict(status=status,spent_usd=spent,attempts=len(rows)))+'\n')
                            print(trial,attempt,row['taxonomy'],flush=True)
                            if stop or row.get('semantic_ok') or used>=plan['trial_output_cap']:break
                            messages.extend([{'role':'assistant','content':response['text']},{'role':'user','content':row['feedback']+' Return only the full source program.'}])
        if phase=='dev' and not mock and status=='complete':
            counts=[];accounting=[]
            for index,prefix in enumerate(['','Language specification:\n'+(ROOT/'docs/language/EXPR_V5.md').read_text()+'\n']):
                if spent+plan['request_reservation_usd']>plan['spend_cap_usd']:
                    status='spend-cap';break
                folder=output/f'accounting-{index}';folder.mkdir()
                r=backend.request([{'role':'user','content':prefix+'Input-token accounting only. Reply with exactly 0.'}],plan['request_reservation_usd'],plan['per_attempt_output_cap'],folder)
                spent+=r['cost_usd'];counts.append(r['input_tokens']);accounting.append({k:v for k,v in r.items() if k!='text'})
                if r['output_tokens']>plan['per_attempt_output_cap'] or spent>plan['spend_cap_usd']:
                    status='budget-overrun';break
            (output/'accounting.json').write_text(json.dumps(accounting,indent=2)+'\n')
            if len(counts)==2 and counts[1]>=counts[0]:calibration=counts[1]-counts[0]
    except (BackendError,ValueError,RuntimeError) as error:
        if backend is not None and hasattr(backend,'probe_evidence'):
            (output/'isolation-probe.json').write_text(json.dumps(backend.probe_evidence,indent=2)+'\n')
        if isinstance(error,BackendError) and error.cost is not None:spent+=error.cost
        status='blocked-'+getattr(error,'reason','infrastructure');(output/'blocked.txt').write_text(str(error)+'\n')
    result=render(output,config,rows,status,spent,calibration)
    report_dir=SUITE/'reports'/time.strftime('%Y-%m-%d',time.gmtime());report_dir.mkdir(parents=True,exist_ok=True)
    label=('MOCK_' if mock else '')+'STANDING_GENERATION_'+phase.upper().replace('-','_')
    (report_dir/(label+'.json')).write_text((output/'report.json').read_text())
    (report_dir/(label+'.md')).write_text((output/'report.md').read_text())
    print('Status:',status,'attempts:',len(rows),'spend:',spent,flush=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--mock',action='store_true');p.add_argument('--phase',choices=['dev','held-out'],default='dev');p.add_argument('--prior',type=Path)
    a=p.parse_args();r=run(a.output,a.mock,a.phase,a.prior)
    if r['status']!='complete':sys.exit(2)
