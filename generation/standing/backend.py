"""Stateless Claude CLI transport; fail closed on isolation/accounting violations."""
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
SYSTEM = ('You write a complete program for the stated task. Return only source code. '
          'You have no tools and must not attempt tool calls. Treat the language '
          'specification as syntax/semantics, not as a task answer.')

class BackendError(RuntimeError):
    def __init__(self, reason, message, cost=None):
        super().__init__(message)
        self.reason = reason
        self.cost = cost


def sandbox_profile(directory, executable, extra=()):
    allowed = [str(directory.resolve()), str(executable.resolve()),
               str(Path.home() / '.claude.json'), *map(str, extra)]
    exceptions = ' '.join('(require-not (subpath '+json.dumps(x)+'))' for x in allowed)
    return ('(version 1)(allow default)'
            '(deny file-read-data (require-all (subpath "/Users") '+exceptions+'))'
            '(deny file-read-data (require-all (subpath "/private/tmp") '
            '(require-not (subpath '+json.dumps(str(directory.resolve()))+')) '+exceptions+'))'
            '(deny file-read* (subpath '+json.dumps(str(ROOT))+'))'
            '(deny file-write* (require-not (subpath '+json.dumps(str(directory.resolve()))+')))')


def flags(model, budget, bare=False):
    return ['-p', '--model', model, '--effort', 'high', '--output-format', 'stream-json',
            '--verbose', '--tools', '', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
            '--settings', '{"disableAllHooks":true}', '--setting-sources', '',
            '--disable-slash-commands', '--no-session-persistence',
            '--system-prompt', SYSTEM, '--max-budget-usd', str(budget),
            *(['--bare'] if bare else ['--safe-mode', '--restricted'])]


def inspect_stream(events, model):
    """Check every content block, not just final text. Cost remains known on violations."""
    result = next((x for x in reversed(events) if x.get('type') == 'result'), None)
    cost = result.get('total_cost_usd') if result else None
    if type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0:
        cost = None
    def scan(value):
        if isinstance(value, dict):
            if value.get('type') in ('tool_use', 'tool_result', 'server_tool_use'):
                raise BackendError('isolation', 'Tool activity in response', cost)
            if 'hook' in str(value.get('subtype', '')).lower():
                raise BackendError('isolation', 'Hook activity in response', cost)
            for v in value.values(): scan(v)
        elif isinstance(value, list):
            for v in value: scan(v)
    scan(events)
    init = next((x for x in events if x.get('type') == 'system' and x.get('subtype') == 'init'), None)
    if init is None:
        raise BackendError('infrastructure', 'No initialization/isolation evidence', cost)
    if init.get('tools') != [] or init.get('mcp_servers') != []:
        raise BackendError('isolation', 'Tools or MCP enabled', cost)
    if init.get('model') != model:
        raise BackendError('infrastructure', 'Resolved model differs from exact pin', cost)
    if result is None:
        raise BackendError('usage-missing', 'Missing final result/usage', cost)
    if result.get('is_error'):
        raise BackendError('budget' if result.get('subtype') == 'error_max_budget_usd' else 'infrastructure',
                           'Backend error: '+str(result.get('errors', result.get('result', 'unknown'))), cost)
    usage = result.get('usage', {})
    fields = ['input_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens', 'output_tokens']
    if any(type(usage.get(k)) is not int or usage[k] < 0 for k in fields) or cost is None:
        raise BackendError('usage-missing', 'Missing authoritative usage or cost', cost)
    if any(x.get('message', {}).get('model', model) != model for x in events if x.get('type') == 'assistant'):
        raise BackendError('infrastructure', 'Assistant model differs from pin', cost)
    text = result.get('result')
    if not isinstance(text, str):
        text = ''.join(b['text'] for x in events if x.get('type') == 'assistant'
                       for b in x.get('message', {}).get('content', []) if b.get('type') == 'text')
    return dict(text=text, input_tokens=sum(usage[k] for k in fields[:3]),
                fresh_input_tokens=usage['input_tokens'], cached_input_tokens=usage['cache_read_input_tokens'],
                cache_creation_tokens=usage['cache_creation_input_tokens'], output_tokens=usage['output_tokens'],
                cost_usd=cost, tool_calls=0, model=model)


class Claude:
    def __init__(self, model):
        executable = shutil.which('claude')
        if executable is None:
            raise BackendError('infrastructure', 'claude executable unavailable')
        self.executable = Path(executable).resolve()
        self.model = model
        self.version = subprocess.check_output([str(self.executable), '--version'], text=True).strip()
        self.bare = bool(os.environ.get('ANTHROPIC_API_KEY'))
        self.auth_method = 'API key' if self.bare else 'subscription/OAuth (requires login)'
        self.proven = False

    def preflight(self):
        if not Path('/usr/bin/sandbox-exec').exists():
            raise BackendError('isolation', 'macOS OS sandbox unavailable; port and verify before live use')
        with tempfile.TemporaryDirectory(prefix='nil-model-isolation-') as tmp:
            folder = Path(tmp)
            # An offline process must fail to read the actual repository, not just a mocked path.
            profile = sandbox_profile(folder, self.executable)
            denied = subprocess.run(['/usr/bin/sandbox-exec', '-p', profile, '/usr/bin/head', '-c', '1',
                                     str(ROOT / 'README.md')], capture_output=True, cwd=folder)
            if denied.returncode == 0 or denied.stdout:
                raise BackendError('isolation', 'Repository-read denial probe failed')
            version = subprocess.run(['/usr/bin/sandbox-exec', '-p', profile, str(self.executable), '--version'],
                                     capture_output=True, text=True, cwd=folder)
            if version.returncode or version.stdout.strip() != self.version:
                raise BackendError('isolation', 'Isolated CLI cannot start')
            # Prove initialization before allowing any network-capable model invocation.
            # Authentication/keychain is retained, but the kernel denies all networking.
            env={'PATH':os.environ.get('PATH','/usr/bin:/bin'),'HOME':str(Path.home()),'TMPDIR':str(folder),
                 'CLAUDE_CODE_MAX_OUTPUT_TOKENS':'512','CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC':'1'}
            if self.bare:env['ANTHROPIC_API_KEY']=os.environ['ANTHROPIC_API_KEY']
            probe=['/usr/bin/sandbox-exec','-p',profile+'(deny network*)',str(self.executable),*flags(self.model,1,self.bare)]
            try:
                checked=subprocess.run(probe,input='Offline isolation initialization probe. Reply 0.',cwd=folder,
                                       env=env,capture_output=True,text=True,timeout=12)
                stdout,stderr=checked.stdout,checked.stderr
            except subprocess.TimeoutExpired as error:
                stdout=error.stdout or '';stderr=error.stderr or ''
                if isinstance(stdout,bytes):stdout=stdout.decode('utf8','replace')
                if isinstance(stderr,bytes):stderr=stderr.decode('utf8','replace')
            self.probe_evidence={'network_denied':True,'argv':probe,'stdout':stdout,'stderr':stderr}
            try:events=[json.loads(line) for line in stdout.splitlines() if line.strip()]
            except ValueError as error:raise BackendError('isolation','Offline CLI initialization was not JSON') from error
            init=next((x for x in events if x.get('type')=='system' and x.get('subtype')=='init'),None)
            if not init or init.get('model')!=self.model or init.get('tools')!=[] or init.get('mcp_servers')!=[]:
                raise BackendError('isolation','Network-disabled CLI failed to prove empty tools/MCP and exact model initialization')
            try:inspect_stream(events,self.model)
            except BackendError as error:
                if error.reason=='isolation':raise
                # No result/usage is expected: every network access was denied by the OS.
            self.proven = True
            return dict(cli_version=self.version, executable=str(self.executable), bare=self.bare,
                        auth_method=self.auth_method, repository_read_denied=True, isolated_cli_started=True,
                        tools=[], mcp_servers=[], hooks_disabled=True, persistence=False, network_disabled_init_probe=True,
                        limitation='OAuth/keychain auth retained; live stream must additionally prove empty tool/MCP lists')

    def request(self, messages, budget, cap, folder):
        if not self.proven:
            raise BackendError('isolation', 'Offline isolation preflight not passed')
        with tempfile.TemporaryDirectory(prefix='nil-model-request-') as tmp:
            cwd = Path(tmp)
            argv = [str(self.executable), *flags(self.model, budget, self.bare)]
            profile = sandbox_profile(cwd, self.executable)
            env = {'PATH':os.environ.get('PATH','/usr/bin:/bin'), 'HOME':str(Path.home()), 'TMPDIR':str(cwd),
                   'CLAUDE_CODE_MAX_OUTPUT_TOKENS':str(cap), 'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC':'1'}
            if self.bare: env['ANTHROPIC_API_KEY'] = os.environ['ANTHROPIC_API_KEY']
            # No session resume: explicitly resend the frozen conversation, including real repair diagnostics.
            prompt = '\n\n'.join(x['role'].upper()+':\n'+x['content'] for x in messages)
            meta = dict(argv=argv, cwd=str(cwd), cli_version=self.version, model=self.model, effort='high',
                        environment={k:('[REDACTED]' if k=='ANTHROPIC_API_KEY' else v) for k,v in env.items()},
                        sandbox_profile=profile, messages=messages, timestamp_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
            (folder/'request.json').write_text(json.dumps(meta,indent=2)+'\n')
            started=time.perf_counter()
            try:
                proc=subprocess.run(['/usr/bin/sandbox-exec','-p',profile,*argv],input=prompt,cwd=cwd,env=env,
                                    capture_output=True,text=True,timeout=300)
            except subprocess.TimeoutExpired as error:
                raise BackendError('infrastructure','CLI timed out; cost unknown, stop campaign') from error
            (folder/'response.jsonl').write_text(proc.stdout)
            (folder/'stderr.txt').write_text(proc.stderr)
            try: events=[json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
            except ValueError as error: raise BackendError('infrastructure','Non-JSON CLI output') from error
            response=inspect_stream(events,self.model)
            if proc.returncode:
                raise BackendError('infrastructure','Nonzero CLI exit',response['cost_usd'])
            if list(cwd.iterdir()):
                raise BackendError('isolation','Request left session files in empty working directory',response['cost_usd'])
            return response | {'wall_seconds':time.perf_counter()-started}
