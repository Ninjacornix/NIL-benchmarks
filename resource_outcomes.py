"""ADR 046 resource classification; signals and instrumentation findings fail closed."""
import re

_DIAGNOSTIC = rb'E\d{3}(?: @(\d+)\.\.(\d+))? [^\r\n]+\n?'

def clean_e013(result, *, reference=False):
    """Recognize one clean resource diagnostic, never a crash/noisy subprocess.

    Reference helper protocols use exit 0 and ERR\tExecute\t on stdout;
    native executables use exit 1 and a diagnostic on stderr. Other outcomes
    remain the caller's ordinary pass/fail responsibility.
    """
    if reference:
        if result.returncode != 0 or result.stderr:
            return False
        prefix = b'ERR\tExecute\t'
        if not result.stdout.startswith(prefix):
            return False
        text = result.stdout[len(prefix):]
    else:
        if result.returncode != 1:
            return False
        text = result.stderr
    try:
        text.decode('utf-8')
    except UnicodeDecodeError:
        return False
    match = re.fullmatch(_DIAGNOSTIC, text)
    if not match or not text.startswith(b'E013 '):
        return False
    if match[1] is not None and int(match[1]) > int(match[2]):
        return False
    # Single-line instrumentation messages are not language failures either.
    return not any(marker in text for marker in
                   (b'AddressSanitizer', b'UndefinedBehaviorSanitizer', b'runtime error:', b'LeakSanitizer'))


def native_code(result):
    """Strict census decoder: E013 cannot mask an invalid native process."""
    assert result.returncode in (0, 1), ('native process failure', result.returncode, result.stderr)
    if result.returncode == 0:
        assert not result.stderr, ('noisy native success', result.stderr)
        return 'OK'
    result.stderr.decode('utf-8')
    match = re.fullmatch(_DIAGNOSTIC, result.stderr)
    assert match, ('malformed native diagnostic', result.stderr)
    assert match[1] is None or int(match[1]) <= int(match[2]), ('reversed diagnostic span', result.stderr)
    assert not any(marker in result.stderr for marker in
                   (b'AddressSanitizer', b'UndefinedBehaviorSanitizer', b'runtime error:', b'LeakSanitizer')), result.stderr
    return result.stderr[:4].decode('ascii')
