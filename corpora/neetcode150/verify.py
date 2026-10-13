"""Trusted authored corpus verification. No model execution or compiler changes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import tempfile
import statistics
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent
SUITE=HERE.parents[1]
sys.path.insert(0,str(SUITE))
from support import ROOT, build_helpers
from resource_outcomes import clean_resource
import fixtures
import reference
TIMEOUT=120
# Round 27 step 4: the per-check budget is CPU seconds, not wall seconds, so a
# cohort can run beside other gates without false timeouts. A concurrent gate
# run previously reported 1,067/1,070 and 1,069/1,070 purely from load. Wall
# time keeps a generous backstop for a process that blocks rather than spins.
WALL_BACKSTOP=TIMEOUT*8

def _cpu_budget():
    import resource
    resource.setrlimit(resource.RLIMIT_CPU,(TIMEOUT,TIMEOUT))

def sha(data): return hashlib.sha256(data).hexdigest()
def tasks(): return json.loads((HERE/'tasks.json').read_text())['tasks']
def qualification(result):
    if result.get('nil_status')!='verified': return 'unverified'
    if not result.get('timings'): return 'performance-pending'
    return 'meets-bound' if result['timings']['ratio']<=3 else 'performance-miss'
def run(command,cwd):
    env={'PATH':os.environ['PATH'],'HOME':str(cwd),'TMPDIR':str(cwd),'PYTHONDONTWRITEBYTECODE':'1'}
    if 'NIL_CLANG' in os.environ:env['NIL_CLANG']=os.environ['NIL_CLANG']
    try:
        p=subprocess.run(command,cwd=cwd,env=env,capture_output=True,timeout=WALL_BACKSTOP,preexec_fn=_cpu_budget)
        # SIGKILL/SIGXCPU from the CPU rlimit reads as a timeout, same verdict
        # as before, but now triggered by work done rather than by load.
        if p.returncode in (-9,-24): return -999,b'',b'timeout'
        return p.returncode,p.stdout,p.stderr
    except subprocess.TimeoutExpired: return -999,b'',b'timeout'
def observed(command,work,data,answer,ref=False):
    (work/'input.bin').write_bytes(data)
    for name in ('output.bin','stdout.bin'): (work/name).unlink(missing_ok=True)
    code,out,err=run(command,work)
    output=(work/'output.bin').read_bytes() if (work/'output.bin').exists() else None
    expected=(f'VALUE\t{len(answer)}\n'.encode() if ref else f'{len(answer)}\n'.encode())
    good=(code==0 and out==expected and not err and output==answer and (work/'input.bin').read_bytes()==data)
    if ref: good=good and (work/'stdout.bin').exists() and (work/'stdout.bin').read_bytes()==b''
    files={p.name for p in work.iterdir()}
    good=good and files<=({'input.bin','output.bin','stdout.bin'} if ref else {'input.bin','output.bin'})
    resource=clean_resource(subprocess.CompletedProcess(command,code,out,err), reference=ref)
    return {'pass':good,'inconclusive':resource,'exit':code,'stdout':out.decode(errors='backslashreplace')[:2000], 'stderr':err.decode(errors='backslashreplace')[:2000],'output_sha256':sha(output) if output is not None else None}
def freeze():
    frozen={}
    for t in tasks():
        if t['id'] not in reference.SOLVERS: continue
        frozen[t['id']]={}
        for name,data in fixtures.cases(t):
            answer=reference.SOLVERS[t['id']](data)
            frozen[t['id']][name]={'input_sha256':sha(data),'output_sha256':sha(answer),'input_bytes':len(data),'output_bytes':len(answer)}
    payload=json.dumps(frozen,indent=2)+'\n'
    path=HERE/'goldens.json'
    if path.exists() and path.read_text()!=payload:raise RuntimeError('Frozen goldens differ; refusing to overwrite')
    if not path.exists():path.write_text(payload)
    print('FROZEN',len(frozen),'tasks',sum(map(len,frozen.values())),'fixtures')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);ap.add_argument('--freeze',action='store_true');ap.add_argument('--baselines-only',action='store_true');ap.add_argument('--all',action='store_true');ap.add_argument('--verified-only',action='store_true');ap.add_argument('--task',action='append');ap.add_argument('--candidate-dir',type=Path);ap.add_argument('--jobs',type=int,default=2);ap.add_argument('--timing-repeats',type=int,default=0)
    args=ap.parse_args()
    if args.freeze: freeze();return
    if not args.output: ap.error('--output required')
    args.output=args.output.resolve()
    if args.output.is_relative_to(ROOT):ap.error('raw results must be outside checkout')
    if args.timing_repeats and args.timing_repeats<15:ap.error('at least 15 timing repeats')
    if args.jobs<1:ap.error('--jobs must be positive')
    if args.timing_repeats and args.jobs!=1:ap.error('timing requires --jobs 1 to avoid competing measurements')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.with_suffix('.jsonl').write_text('')
    golden=json.loads((HERE/'goldens.json').read_text())
    selected=[t for t in tasks() if (t['id'] in args.task if args.task else args.all or t['selected'])]
    if args.verified_only:selected=[t for t in selected if (HERE/'programs'/(t['id']+'.nil')).exists()]
    if args.task and set(args.task)!={t['id'] for t in selected}:ap.error('unknown task')
    if not args.baselines_only:build_helpers('core_check')
    helper=Path(os.environ.get('NIL_BIN') or (ROOT/'target/release'))/'examples/core_check'
    clang=os.environ.get('NIL_CLANG','clang')
    def verify(t):
        slug=t['id']; source=HERE/'programs'/f'{slug}.nil'
        if args.candidate_dir:source=(args.candidate_dir/f'{slug}.nil').resolve()
        result={'task':slug,'forecast':t['forecast'],'checks':[], 'timings':{}}
        with tempfile.TemporaryDirectory(prefix='nil-core-') as directory:
            folder=Path(directory); cpp=folder/'cpp'
            result['cpp_command']=[clang,'--driver-mode=g++','-std=c++17','-O2','-ffp-contract=off',str(HERE/'programs'/f'{slug}.cpp'),'-o',str(cpp)]
            build=subprocess.run(result['cpp_command'],capture_output=True)
            if build.returncode:result.update(status='infrastructure-failure',detail=build.stderr.decode());return result
            commands={'python':[sys.executable,'-I',str(HERE/'programs'/f'{slug}.py'),'input.bin','output.bin'],'cpp':[str(cpp),'input.bin','output.bin']}
            if not args.baselines_only:
                if not source.exists(): result['nil_status']='not-authored'
                else:
                    result['nil_source_sha256']=sha(source.read_bytes()); result['builds']={}
                    for opt in ('O0','O2'):
                        binary=folder/('nil-'+opt);code,out,err=run([str(helper),str(source),'build-'+opt,str(binary)],folder)
                        result['builds'][opt]={'exit':code,'stdout':out.decode(errors='backslashreplace'),'stderr':err.decode(errors='backslashreplace')}
                        if code==0 and out==b'BUILD\tOK\n' and not err:commands[opt]=[str(binary),'input.bin','output.bin']
                    commands['reference']=[str(helper),str(source),'input.bin','output.bin','stdout.bin']
            for name,data in fixtures.cases(t):
                answer=reference.SOLVERS[slug](data)
                locked=golden[slug][name]
                if locked['input_sha256']!=sha(data) or locked['output_sha256']!=sha(answer):raise RuntimeError(f'frozen oracle/fixture changed: {slug}/{name}')
                for language,command in commands.items():
                    work=folder/f'{name}-{language}';work.mkdir()
                    verdict=observed(command,work,data,answer,language=='reference')
                    result['checks'].append({'fixture':name,'language':language,**verdict})
                    if not verdict['pass'] and not verdict['inconclusive']:
                        # Failed candidates do not spend repeated 120s on later maximum cases.
                        commands[language]=None
                commands={k:v for k,v in commands.items() if v is not None}
            baseline_good=all(x['pass'] for x in result['checks'] if x['language'] in ('cpp','python'))
            nilchecks=[x for x in result['checks'] if x['language'] in ('reference','O0','O2')]
            needed=3*len(golden[slug])
            result['nil_status']='verified' if len(nilchecks)==needed and all(x['pass'] for x in nilchecks) else ('not-run' if args.baselines_only else result.get('nil_status','blocked-candidate'))
            resource_only=len(nilchecks)==needed and any(x['inconclusive'] for x in nilchecks) and all(x['pass'] or x['inconclusive'] for x in nilchecks)
            if resource_only:result['nil_status']='resource-inconclusive'
            result['status']='pass' if baseline_good and (args.baselines_only or result['nil_status']=='verified') else ('resource-inconclusive' if baseline_good and resource_only else 'failed')
            if args.timing_repeats and result['nil_status']=='verified':
                binary=folder/'nil-perf';code,out,err=run([str(helper),str(source),'perf-O2',str(binary)],folder)
                if code or out!=b'BUILD\tOK\n' or err:raise RuntimeError('perf build failed')
                data=list(fixtures.cases(t))[-1][1];answer=reference.SOLVERS[slug](data);samples={'nil':[],'cpp':[]}
                work=folder/'timing';work.mkdir()
                cmds={'nil':[str(binary),'input.bin','output.bin'],'cpp':[str(cpp),'input.bin','output.bin']}
                for repeat in range(args.timing_repeats+1):
                    for language in (('nil','cpp') if repeat%2==0 else ('cpp','nil')):
                        (work/'input.bin').write_bytes(data);(work/'output.bin').unlink(missing_ok=True)
                        start=time.perf_counter_ns();code,out,err=run(cmds[language],work);elapsed=(time.perf_counter_ns()-start)/1e6
                        if code or err or out!=f'{len(answer)}\n'.encode() or (work/'output.bin').read_bytes()!=answer or (work/'input.bin').read_bytes()!=data:raise RuntimeError('timing output mismatch')
                        if repeat:samples[language].append(elapsed)
                for language,values in samples.items():result['timings'][language]={'min_ms':min(values),'median_ms':statistics.median(values),'max_ms':max(values),'samples_ms':values,'stdev_ms':statistics.stdev(values)}
                result['timings']['ratio']=result['timings']['nil']['median_ms']/result['timings']['cpp']['median_ms']
        result['qualification']=qualification(result)
        with args.output.with_suffix('.jsonl').open('a') as progress:progress.write(json.dumps(result)+'\n')
        print(slug,result['status'],result['nil_status'],sum(x['pass'] for x in result['checks']),flush=True)
        return result
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:results=list(pool.map(verify,selected))
    report={'schema':1,'clang_version':subprocess.check_output([clang,'--version'],text=True).splitlines()[0],'python_version':sys.version,'compiler_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'benchmarks_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=SUITE,text=True).strip(),'limits':{'steps':1000000000,'depth':1000000,'stack_bytes':134217728,'cpu_seconds':TIMEOUT,'wall_backstop_seconds':WALL_BACKSTOP},'tasks_sha256':sha((HERE/'tasks.json').read_bytes()),'goldens_sha256':sha((HERE/'goldens.json').read_bytes()),'results':results,'totals':{'tasks':len(results),'verified_nil':sum(r.get('nil_status')=='verified' for r in results),'checks':sum(len(r['checks']) for r in results),'passed_checks':sum(x['pass'] for r in results for x in r['checks']),'inconclusive_checks':sum(x['inconclusive'] for r in results for x in r['checks'])}}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print('TOTALS',json.dumps(report['totals']))
    if any(r['status'] not in ('pass','resource-inconclusive') for r in results):raise SystemExit(1)
if __name__=='__main__':main()
