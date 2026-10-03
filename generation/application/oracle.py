"""Frozen application contracts, real evaluator/native paths and Python baseline."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from support import ROOT, build_helpers


def expected(task_id, data):
    if task_id == 'ascii_upper':
        return bytes(x-32 if 97 <= x <= 122 else x for x in data)
    if task_id == 'nonempty_lines':
        return b''.join(x+b'\n' for x in data.split(b'\n') if x)
    if task_id == 'sum_pairs':
        return b''.join((str(sum(map(int, row.split(b','))))+'\n').encode()
                        for row in data.splitlines())
    if task_id == 'running_report':
        return b''.join(f'{i}:{i*(i+1)//2}\n'.encode() for i in range(int(data)))
    raise ValueError('unknown task: '+task_id)


def prepare():
    build_helpers('application_check')
    subprocess.run(['cargo','build','--release','--locked','--offline','-p','nil'], cwd=ROOT, check=True)
    if sys.platform != 'darwin' or not Path('/usr/bin/sandbox-exec').exists():
        raise RuntimeError('Application inference requires the documented macOS process sandbox; port it before executing generated host code elsewhere.')


def sandbox(command, folder, timeout=5):
    # This is a benchmark execution boundary, not a NIL security feature.
    import json
    allowed = [str(folder.resolve()), str(HERE/'python_driver.py')]
    for arg in command:
        path = Path(str(arg))
        if path.is_absolute() and path.is_file():
            allowed.append(str(path.resolve()))
    exceptions = ' '.join('(require-not (literal '+json.dumps(p)+'))' for p in allowed[1:])
    # System dyld paths vary across macOS versions; permit reads generally but
    # explicitly deny user data and other /tmp fixtures/artifacts.
    user_deny = '(deny file-read-data (require-all (subpath "/Users") '+exceptions+'))'
    temp_deny = ''.join('(deny file-read-data (require-all (subpath '+json.dumps(root)+') (require-not (subpath '+json.dumps(allowed[0])+')) '+exceptions+'))' for root in ['/private/tmp',str(Path(tempfile.gettempdir()).resolve())])
    profile = '(version 1)(deny default)(allow process-exec)(allow sysctl-read)(allow mach-lookup)(allow process-info*)(allow file-read*)(allow file-write* (subpath '+json.dumps(str(folder.resolve()))+'))'+user_deny+temp_deny
    env = {'PATH':os.environ.get('PATH','/usr/bin:/bin'), 'HOME':str(folder), 'TMPDIR':str(folder),
           'PYTHONDONTWRITEBYTECODE':'1', 'PYTHONHASHSEED':'0'}
    return subprocess.run(['/usr/bin/sandbox-exec','-p',profile,*map(str,command)], cwd=folder,
                          env=env,capture_output=True,timeout=timeout)


def evaluate(source, language, task, folder):
    folder = folder.resolve()
    path = folder/('candidate.nil' if language == 'expr-v5' else 'candidate.py')
    path.write_text(source)
    outcome = dict(parse_ok=None,typecheck_ok=None,compile_ok=None,semantic_ok=False,
                   tests_total=len(task['inputs']),tests_passed=0,native_tests_passed=0,
                   failure_reason=None,feedback='Semantic tests failed; check the full task contract and edge cases. Return the complete corrected program.')
    if not task['inputs']:
        raise ValueError('empty oracle')
    binaries = []
    try:
        if language == 'python':
            try:
                compile(source,str(path),'exec')
            except SyntaxError as error:
                return outcome | dict(parse_ok=False,failure_reason='parse',feedback=f'SyntaxError at line {error.lineno}: {error.msg}. Return the complete corrected program.')
            outcome.update(parse_ok=True,compile_ok=True)
        elif language == 'expr-v5':
            # Compile/check once before building native variants, even for bad sources.
            with tempfile.TemporaryDirectory(dir=folder) as directory:
                work=Path(directory);(work/'input.bin').write_bytes(bytes.fromhex(task['inputs'][0]))
                ref=subprocess.run([str(ROOT/'target/release/examples/application_check'),str(path),str(work/'input.bin'),str(work/'reference.bin'),str(work/'stdout.bin')],capture_output=True,text=True,timeout=5)
            if ref.returncode:
                return outcome | dict(failure_reason='checker',feedback='Reference checker process failed.')
            if ref.stdout.startswith('ERR\t'):
                phase=ref.stdout.split('\t',2)[1]
                if phase != 'Execute':
                    return outcome | dict(parse_ok=phase!='Parse',typecheck_ok=False if phase!='Parse' else None,failure_reason='parse' if phase=='Parse' else 'type',feedback=ref.stdout.strip()[:800])
            outcome.update(parse_ok=True,typecheck_ok=True)
            for level in ['O0','O2']:
                binary=folder/('candidate-'+level)
                built=subprocess.run([str(ROOT/'target/release/nil'),'--profile','expr-v5','--bounded','build',str(path),'-o',str(binary),'-'+level],capture_output=True,text=True,timeout=60)
                if built.returncode:
                    return outcome | dict(compile_ok=False,failure_reason='backend',feedback='Native compilation failed: '+built.stderr[:800])
                binaries.append(binary)
            outcome['compile_ok']=True
        else:
            raise ValueError('unknown language')
        for data_hex in task['inputs']:
            data=bytes.fromhex(data_hex); answer=expected(task['id'],data)
            with tempfile.TemporaryDirectory(dir=folder) as directory:
                work=Path(directory); inp=work/'input.bin'; output=work/'output.bin'
                inp.write_bytes(data)
                if language == 'expr-v5':
                    ref=subprocess.run([str(ROOT/'target/release/examples/application_check'),str(path),str(inp),str(work/'reference.bin'),str(work/'stdout.bin')],capture_output=True,timeout=5)
                    ref_ok=ref.returncode==0 and ref.stdout==f'VALUE\t{len(answer)}\n'.encode() and (work/'reference.bin').exists() and (work/'reference.bin').read_bytes()==answer and (work/'stdout.bin').read_bytes()==b''
                    outcome['tests_passed']+=int(ref_ok)
                    for artifact in ['reference.bin','stdout.bin']:
                        artifact_path=work/artifact
                        if artifact_path.exists():artifact_path.unlink()
                    for binary in binaries:
                        if output.exists():output.unlink()
                        native=sandbox([binary,'input.bin','output.bin'],work)
                        good=native.returncode==0 and native.stdout==f'{len(answer)}\n'.encode() and output.exists() and output.read_bytes()==answer
                        outcome['native_tests_passed']+=int(good)
                else:
                    run=sandbox([str(Path(sys.executable).resolve()),'-I',HERE/'python_driver.py',path],work)
                    good=run.returncode==0 and run.stdout==f'{len(answer)}\n'.encode() and output.exists() and output.read_bytes()==answer
                    outcome['tests_passed']+=int(good)
                if inp.read_bytes()!=data:
                    outcome['tests_passed']=0
        outcome['semantic_ok']=outcome['tests_passed']==outcome['tests_total'] and (language=='python' or outcome['native_tests_passed']==2*outcome['tests_total'])
        outcome['failure_reason']=None if outcome['semantic_ok'] else 'semantic_or_execution'
        if outcome['semantic_ok']:outcome['feedback']='Correct.'
    except subprocess.TimeoutExpired:
        outcome.update(failure_reason='timeout',feedback='Execution or compilation timed out; use a terminating algorithm within 100000 reference steps and 256 call frames.')
    return outcome
