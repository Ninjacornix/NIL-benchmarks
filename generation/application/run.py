"""Application adapter for the existing generation experiment, with frozen v5/Python tasks."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import experiment as core
import oracle


def extract_source(text):
    match=re.fullmatch(r'\s*```(?:nil|python|text)?\s*\n(.*?)\n```\s*',text,re.S)
    return (match.group(1) if match else text).strip()+'\n'


def prompt(language, task):
    reference=(HERE/('nil-reference.txt' if language=='expr-v5' else 'python-reference.txt')).read_text()
    return ('Return only the full source program. Use the following fixed language reference and generic example.\n'+reference+
            '\nTask: '+task['prompt']+'\nFor both languages: read the file given by the first parameter, write the file given by the second, return exactly its byte length, emit no stdout, and do not modify the input. Complete every valid input within 100000 execution steps and 256 call frames. Input paths are relative filenames. No task answers or hidden inputs are provided.')


def provenance():
    files=[HERE/'tasks.json',HERE/'experiment.json',HERE/'nil-reference.txt',HERE/'python-reference.txt',HERE/'oracle.py',HERE/'python_driver.py',Path(__file__),Path(core.__file__),core.SUITE/'helpers/application_check.rs',*core.ROOT.glob('Cargo*'),*core.ROOT.glob('rust-toolchain*')]
    files += list((core.ROOT/'crates').rglob('*.rs'))+list((core.ROOT/'crates').rglob('*.c'))+list((core.ROOT/'cli').rglob('*.rs'))
    return {core.source_key(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def stub(task,language,attempt):
    # Deliberately exercise repair and zero-solve accounting; not model output.
    if task['id']=='sum_pairs' or attempt==0:
        return 'invalid source'
    return (HERE/'solutions'/f"{task['id']}.{'nil' if language=='expr-v5' else 'py'}").read_text()


def run(output, endpoint, mock=False):
    output=output.expanduser().resolve()
    if any(output==p or p in output.parents for p in [core.ROOT,core.SUITE]):
        raise ValueError('Output must be outside both repositories')
    if output.exists():raise ValueError('Choose a fresh output directory')
    definition=json.loads((HERE/'experiment.json').read_text())
    tasks=json.loads((HERE/'tasks.json').read_text())['tasks']
    assert [t['id'] for t in tasks]==definition['task_ids']
    oracle.prepare()
    output.mkdir(parents=True)
    metadata={}
    if not mock:
        tags={x['name']:x for x in core.post(endpoint,'/api/tags')['models']}
        for name,digest in definition['models'].items():
            if name not in tags or tags[name]['digest']!=digest:
                raise ValueError('Frozen model missing or digest mismatch: '+name)
        metadata=dict(server=core.post(endpoint,'/api/version'),models={name:tags[name] for name in definition['models']},details={name:core.post(endpoint,'/api/show',{'model':name}) for name in definition['models']})
    config=definition | dict(mock=mock,model_metadata=metadata,compiler_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=core.ROOT,text=True).strip(),benchmark_suite=core.suite_provenance(),python=sys.version,source_hashes=provenance(),source_tokens=None,source_token_note='Not collected; exact provider input/output usage is the central metric. Source characters and UTF-8 bytes recorded separately.')
    if mock:config['models']={'STUB-NOT-A-MODEL':'synthetic-test-only'}
    (output/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    trials=[]
    with (output/'attempts.jsonl').open('x') as log:
        for model in config['models']:
            for index,task in enumerate(tasks):
                for seed in config['seeds']:
                    langs=config['languages'];offset=(index+seed)%2
                    for language in langs[offset:]+langs[:offset]:
                        trial_id=f'{model.replace(":","-")}-{task["id"]}-{seed}-{language}'
                        folder=output/trial_id;folder.mkdir()
                        messages=[{'role':'user','content':prompt(language,task)}]
                        spent=inputs=repairs=0;output_known=input_known=True;solved=False;attempt_count=0
                        for attempt in range(config['attempt_limit']):
                            remaining=config['output_budget']-spent
                            if remaining<=0:break
                            request=dict(model=model,messages=messages,stream=False,keep_alive='5m',options=dict(seed=seed,temperature=config['temperature'],num_ctx=config['num_ctx'],num_predict=min(config['per_attempt_limit'],remaining)))
                            (folder/f'request-{attempt}.json').write_text(json.dumps(request,indent=2)+'\n')
                            attempt_count+=1; start=time.perf_counter_ns()
                            try:
                                response=({'message':{'content':stub(task,language,attempt)},'eval_count':10+attempt,'prompt_eval_count':20+attempt,'done_reason':'stop','synthetic':True} if mock else core.post(endpoint,'/api/chat',request))
                            except Exception as error:
                                row=dict(trial_id=trial_id,model=model,profile=language,task=task['id'],seed=seed,attempt=attempt,semantic_ok=False,failure_reason='infrastructure',generated_tokens=None,input_tokens=None,error=str(error))
                                log.write(json.dumps(row)+'\n');log.flush();output_known=input_known=False;break
                            (folder/f'response-{attempt}.json').write_text(json.dumps(response,indent=2)+'\n')
                            text=response['message']['content'];source=extract_source(text)
                            (folder/('source-'+str(attempt)+('.nil' if language=='expr-v5' else '.py'))).write_text(source)
                            verdict=oracle.evaluate(source,language,task,folder)
                            used=response.get('eval_count');input_count=response.get('prompt_eval_count')
                            if type(used)!=int or used<0:output_known=False
                            else:spent+=used;repairs+=used if attempt else 0
                            if type(input_count)!=int or input_count<0:input_known=False
                            else:inputs+=input_count
                            row=dict(trial_id=trial_id,model=model,profile=language,task=task['id'],seed=seed,attempt=attempt,input_tokens=input_count,generated_tokens=used,repair_tokens=used if attempt else 0,source_characters=len(source),source_bytes=len(source.encode()),source_sha256=core.digest(source),prompt_sha256=core.digest(json.dumps(messages,sort_keys=True)),test_sha256=core.digest(json.dumps(task,sort_keys=True)),reasoning_tokens=None,thinking_text_present=bool(response['message'].get('thinking')),done_reason=response.get('done_reason'),wall_ns=time.perf_counter_ns()-start,**verdict)
                            log.write(json.dumps(row)+'\n');log.flush()
                            print(trial_id,attempt,used,verdict['failure_reason'] or 'correct',flush=True)
                            solved=verdict['semantic_ok']
                            if solved or not output_known:break
                            messages.extend([{'role':'assistant','content':text},{'role':'user','content':verdict['feedback']+' Return only the full source program.'}])
                        trial=dict(model=model,profile=language,task=task['id'],seed=seed,solved=solved,attempts=attempt_count,output_tokens=spent if output_known else None,input_tokens=inputs if input_known else None,repair_tokens=repairs if output_known else None)
                        trials.append(trial)
                        with (output/'trials.jsonl').open('a') as file:file.write(json.dumps(trial)+'\n')
                        (output/'summary.json').write_text(json.dumps(core.summary(trials),indent=2)+'\n')
    report(output)


def audit(root):
    config=json.loads((root/'config.json').read_text())
    trials=[json.loads(x) for x in (root/'trials.jsonl').read_text().splitlines()]
    attempts=[json.loads(x) for x in (root/'attempts.jsonl').read_text().splitlines()]
    expected={(m,p,t,s) for m in config['models'] for p in config['languages'] for t in config['task_ids'] for s in config['seeds']}
    keys=lambda r:(r['model'],r['profile'],r['task'],r['seed'])
    assert len(trials)==len(expected) and {keys(t) for t in trials}==expected,'incomplete or duplicate cells'
    for key,value in config['source_hashes'].items():
        assert hashlib.sha256(core.resolve_source(key).read_bytes()).hexdigest()==value,'changed measured source: '+key
    for t in trials:
        rows=[a for a in attempts if keys(a)==keys(t)]
        assert len(rows)==t['attempts']<=config['attempt_limit']
        assert [r['attempt'] for r in rows]==list(range(len(rows)))
        assert t['solved']==rows[-1]['semantic_ok'] and not any(r['semantic_ok'] for r in rows[:-1])
        for field,total in [('generated_tokens','output_tokens'),('input_tokens','input_tokens')]:
            known=all(type(r[field])==int and r[field]>=0 for r in rows)
            assert t[total]==(sum(r[field] for r in rows) if known else None)
        assert t['repair_tokens']==(sum(r['generated_tokens'] for r in rows[1:]) if t['output_tokens'] is not None else None)
        assert t['output_tokens'] is None or t['output_tokens']<=config['output_budget'],'provider exceeded output budget'
        for r in rows:
            if 'source_sha256' not in r:continue
            folder=root/r['trial_id'];n=r['attempt']
            response=json.loads((folder/f'response-{n}.json').read_text());request=json.loads((folder/f'request-{n}.json').read_text())
            source=(folder/('source-'+str(n)+('.nil' if r['profile']=='expr-v5' else '.py'))).read_text()
            assert core.digest(source)==r['source_sha256']
            assert core.digest(json.dumps(request['messages'],sort_keys=True))==r['prompt_sha256']
            assert response.get('eval_count')==r['generated_tokens'] and response.get('prompt_eval_count')==r['input_tokens']
            if r['semantic_ok']:
                assert r['tests_total']>0 and r['tests_passed']==r['tests_total']
                if r['profile']=='expr-v5':assert r['native_tests_passed']==2*r['tests_total']
    return config,trials,attempts


def report(root):
    config,trials,attempts=audit(root)
    groups=core.summary(trials)
    per_task={t:core.summary([r for r in trials if r['task']==t]) for t in config['task_ids']}
    intervals=[]
    for model in config['models']:
        out=core.paired_interval(trials,model,'python','expr-v5')
        total_rows=[r|{'output_tokens':r['output_tokens']+r['input_tokens'] if r['output_tokens'] is not None and r['input_tokens'] is not None else None,'input_tokens':0,'repair_tokens':0} for r in trials]
        total=core.paired_interval(total_rows,model,'python','expr-v5')
        intervals.append(dict(model=model,output=out,input_plus_output=total))
    result=dict(mock=config['mock'],aggregate=groups,per_task=per_task,paired_intervals=intervals,failure_modes=dict(Counter(r.get('failure_reason') for r in attempts if not r['semantic_ok'])),trials=len(trials),attempts=len(attempts))
    (root/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Audit passed:',len(trials),'trials;',len(attempts),'attempts;', 'STUB ONLY' if config['mock'] else 'REAL MODEL USAGE',flush=True)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--endpoint',default='http://127.0.0.1:11434')
    parser.add_argument('--mock',action='store_true')
    parser.add_argument('--report-only',action='store_true')
    args=parser.parse_args()
    if args.report_only:report(args.output)
    else:run(args.output,args.endpoint,args.mock)
