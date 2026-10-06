"""Stateless Claude CLI transport; fail closed on isolation/accounting violations."""
import json
import math
import os
from pathlib import Path
import shutil
import stat
from contextlib import contextmanager
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
SYSTEM = ('You write a complete program for the stated task. Return only source code. '
          'You have no tools and must not attempt tool calls. Treat the language '
          'specification as syntax/semantics, not as a task answer.')

class BackendError(RuntimeError):
    def __init__(self, reason, message, cost=None, usage=None):
        super().__init__(message)
        self.reason = reason
        self.cost = cost
        self.usage = usage


class Secrets:
    """Exact-value redaction is applied before serialization, including errors."""
    def __init__(self, *values):
        self.values = sorted({v for v in values if v}, key=len, reverse=True)

    def clean(self, value):
        if isinstance(value, str):
            for secret in self.values:
                value = value.replace(secret, '[REDACTED]')
            return value
        if isinstance(value, dict):
            return {self.clean(k): self.clean(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [self.clean(v) for v in value]
        return value

    def write(self, path, value, json_value=False):
        safe = self.clean(value)
        path.write_text(json.dumps(safe, indent=2)+'\n' if json_value else safe)


def subscription_token():
    path = Path(os.environ.get('NIL_CLAUDE_OAUTH_TOKEN_FILE',
                               '~/.config/nil/claude-oauth-token')).expanduser()
    try:
        # O_NOFOLLOW plus fstat avoid permission/symlink races before reading.
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'r') as file:
            info = os.fstat(file.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
                raise BackendError('authentication', 'OAuth token file must be owned by this user, regular and mode 0600 or stricter')
            token = file.read(16385).strip()
        if not token or len(token) > 16384 or any(c.isspace() for c in token):
            raise BackendError('authentication', 'OAuth token file must contain one nonempty token')
        return token
    except (OSError, UnicodeError) as error:
        raise BackendError('authentication', 'Cannot securely read OAuth token file; configure NIL_CLAUDE_OAUTH_TOKEN_FILE') from None


@contextmanager
def workspace(prefix):
    with tempfile.TemporaryDirectory(prefix=prefix) as tmp:
        root = Path(tmp).resolve()
        cwd, state, home = (root / name for name in ('cwd', 'state', 'home'))
        for folder in (cwd, state, home): folder.mkdir(mode=0o700)
        yield root, cwd, state, home


def sandbox_profile(directory, executable, extra=()):
    allowed = [str(directory.resolve()), str(executable.resolve()), *map(str, extra)]
    exceptions = ' '.join('(require-not (subpath '+json.dumps(x)+'))' for x in allowed)
    keychains = [Path.home()/'Library/Keychains', Path('/Library/Keychains'), Path('/System/Library/Keychains'), directory/'home/Library/Keychains']
    return ('(version 1)(allow default)'
            '(deny file-read-data (require-all (subpath "/Users") '+exceptions+'))'
            '(deny file-read-data (require-all (subpath "/private/tmp") '+exceptions+'))'
            '(deny file-read* (subpath '+json.dumps(str(ROOT))+'))'
            ''.join('(deny file-read* (subpath '+json.dumps(str(p))+'))' for p in keychains)+
            '(deny process-exec (literal "/usr/bin/security"))'
            '(deny file-write* (require-not (subpath '+json.dumps(str(directory.resolve()))+')))')


def flags(model, budget):
    return ['-p', '--model', model, '--effort', 'high', '--output-format', 'stream-json',
            '--verbose', '--tools', '', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
            '--settings', '{"disableAllHooks":true}', '--setting-sources', '',
            '--disable-slash-commands', '--no-session-persistence',
            '--system-prompt', SYSTEM, '--max-budget-usd', str(budget),
            '--safe-mode', '--restricted']


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
    # Classify transport limits only from structured backend errors, never from
    # ordinary generated text that happens to mention a limit.
    limit_events = [x for x in events if x.get('type') == 'assistant' and
                    x.get('error') in ('rate_limit', 'rate_limit_error', 'usage_limit')]
    error_text = str(result.get('errors', result.get('result', ''))).lower()
    rate_limited = (bool(limit_events) or (result.get('is_error') and
                    (result.get('subtype') in ('error_rate_limit', 'error_usage_limit') or
                     any(word in error_text for word in ('rate limit', 'rate_limit', 'usage limit',
                                                         "you've hit your limit", 'usage window')))))
    if rate_limited:
        fields = ['input_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens', 'output_tokens']
        usage = result.get('usage', {})
        known = all(type(usage.get(k)) is int and usage[k] >= 0 for k in fields)
        accounting = dict(input_tokens=sum(usage[k] for k in fields[:3]),
                          fresh_input_tokens=usage['input_tokens'],cached_input_tokens=usage['cache_read_input_tokens'],
                          cache_creation_tokens=usage['cache_creation_input_tokens'],
                          output_tokens=usage['output_tokens']) if known else None
        raise BackendError('rate-limit', 'Subscription usage window reached; explicitly resume later', cost, accounting)
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
        self.token = subscription_token()
        self.secrets = Secrets(self.token, os.environ.get('ANTHROPIC_API_KEY'),
                               os.environ.get('CLAUDE_CODE_OAUTH_TOKEN'))
        executable = shutil.which('claude')
        if executable is None:
            raise BackendError('infrastructure', 'claude executable unavailable')
        self.executable = Path(executable).resolve()
        self.model = model
        self.version = self.secrets.clean(subprocess.check_output([str(self.executable), '--version'], text=True,
                                                               env={'PATH':'/usr/bin:/bin'}).strip())
        self.bare = False
        self.auth_method = 'subscription OAuth token file (notional cost)'
        self.proven = False

    def environment(self, state, home, cap):
        return {'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'HOME': str(home),
                'TMPDIR': str(state), 'CLAUDE_CODE_TMPDIR': str(state),
                'CLAUDE_CODE_OAUTH_TOKEN': self.token,
                'CLAUDE_CODE_MAX_OUTPUT_TOKENS': str(cap),
                'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC': '1'}

    def preflight(self):
        if not Path('/usr/bin/sandbox-exec').exists():
            raise BackendError('isolation', 'macOS OS sandbox unavailable; port and verify before live use')
        with workspace('nil-model-isolation-') as (root, cwd, state, home):
            profile = sandbox_profile(root, self.executable)
            denied = subprocess.run(['/usr/bin/sandbox-exec', '-p', profile, '/usr/bin/head', '-c', '1',
                                     str(ROOT / 'README.md')], capture_output=True, cwd=cwd)
            if denied.returncode == 0 or denied.stdout:
                raise BackendError('isolation', 'Repository-read denial probe failed')
            # Create an actual readable sentinel at a keychain path without reading
            # credentials; denial must be kernel-enforced, not file-not-found.
            keychain = home/'Library/Keychains/denial-sentinel'
            keychain.parent.mkdir(parents=True);keychain.write_text('denial sentinel')
            probe_profile = profile
            denied = subprocess.run(['/usr/bin/sandbox-exec', '-p', probe_profile, '/usr/bin/head', '-c', '1',
                                     str(keychain)], capture_output=True, cwd=cwd)
            if denied.returncode == 0 or denied.stdout:
                raise BackendError('isolation', 'Keychain read-denial probe failed')
            keychain.unlink()
            version = subprocess.run(['/usr/bin/sandbox-exec', '-p', profile, str(self.executable), '--version'],
                                     capture_output=True, text=True, cwd=cwd)
            if version.returncode or version.stdout.strip() != self.version:
                raise BackendError('isolation', 'Isolated CLI cannot start')
            env = self.environment(state, home, 8192)
            probe = ['/usr/bin/sandbox-exec', '-p', profile+'(deny network*)', str(self.executable), *flags(self.model,1)]
            try:
                checked = subprocess.run(probe, input='Offline isolation initialization probe. Reply 0.', cwd=cwd,
                                         env=env, capture_output=True, text=True, timeout=12)
                stdout, stderr = checked.stdout, checked.stderr
            except subprocess.TimeoutExpired as error:
                stdout, stderr = error.stdout or '', error.stderr or ''
                if isinstance(stdout,bytes): stdout=stdout.decode('utf8','replace')
                if isinstance(stderr,bytes): stderr=stderr.decode('utf8','replace')
            stdout, stderr = self.secrets.clean(stdout), self.secrets.clean(stderr)
            self.probe_evidence = dict(network_denied=True, argv=probe, stdout=stdout, stderr=stderr,
                                       cwd=str(cwd), state=str(state), home=str(home))
            try: events=[json.loads(line) for line in stdout.splitlines() if line.strip()]
            except ValueError: raise BackendError('isolation','Offline CLI initialization was not JSON') from None
            init=next((x for x in events if x.get('type')=='system' and x.get('subtype')=='init'),None)
            if not init or init.get('model')!=self.model or init.get('tools')!=[] or init.get('mcp_servers')!=[]:
                raise BackendError('isolation','Network-disabled CLI failed to prove empty tools/MCP and exact model initialization')
            try: inspect_stream(events,self.model)
            except BackendError as error:
                if error.reason=='isolation': raise
            if list(cwd.iterdir()):
                raise BackendError('isolation','Offline initialization populated empty cwd')
            self.proven=True
            return dict(cli_version=self.version, executable=str(self.executable), bare=False,
                        auth_method=self.auth_method, repository_read_denied=True, keychain_reads_denied=True,
                        isolated_cli_started=True, tools=[], mcp_servers=[], hooks_disabled=True,
                        persistence=False, network_disabled_init_probe=True, sibling_temp_layout=True,
                        limitation='Offline initialization proves isolation, not token validity or model availability')

    def request(self, messages, budget, cap, folder):
        if not self.proven: raise BackendError('isolation','Offline isolation preflight not passed')
        with workspace('nil-model-request-') as (root, cwd, state, home):
            argv=[str(self.executable), *flags(self.model,budget)]
            profile=sandbox_profile(root,self.executable)
            env=self.environment(state,home,cap)
            prompt='\n\n'.join(x['role'].upper()+':\n'+x['content'] for x in messages)
            meta=dict(argv=argv,cwd=str(cwd),cli_version=self.version,model=self.model,effort='high',
                      environment={k:('[REDACTED]' if k=='CLAUDE_CODE_OAUTH_TOKEN' else v) for k,v in env.items()},
                      sandbox_profile=profile,messages=messages,timestamp_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
            self.secrets.write(folder/'request.json',meta,True)
            started=time.perf_counter()
            try:
                proc=subprocess.run(['/usr/bin/sandbox-exec','-p',profile,*argv],input=prompt,cwd=cwd,env=env,
                                    capture_output=True,text=True,timeout=300)
            except subprocess.TimeoutExpired:
                raise BackendError('infrastructure','CLI timed out; cost unknown, stop campaign') from None
            stdout, stderr=self.secrets.clean(proc.stdout),self.secrets.clean(proc.stderr)
            self.secrets.write(folder/'response.jsonl',stdout)
            self.secrets.write(folder/'stderr.txt',stderr)
            try: events=[json.loads(line) for line in stdout.splitlines() if line.strip()]
            except ValueError: raise BackendError('infrastructure','Non-JSON CLI output') from None
            try: response=inspect_stream(events,self.model)
            except BackendError as error:
                if list(cwd.iterdir()): raise BackendError('isolation','Request populated empty cwd',error.cost) from None
                raise
            if proc.returncode: raise BackendError('infrastructure','Nonzero CLI exit',response['cost_usd'])
            if list(cwd.iterdir()):
                raise BackendError('isolation','Request left session files in empty working directory',response['cost_usd'])
            return response | {'wall_seconds':time.perf_counter()-started}
