"""Interleave selected already-prepared ownership controls across revisions."""
import argparse
import json
import statistics
import subprocess
import shutil
import time
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--before', type=Path, required=True)
p.add_argument('--after', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--control', action='append', required=True)
p.add_argument('--repeats', type=int, default=25)
p.add_argument('--argv0', help='Optional identical argv[0] for a launch-path control')
p.add_argument('--same-executable-path', type=Path,
               help='Copy each arm to one external path before starting its timer')
a = p.parse_args()
root = Path(__file__).resolve().parents[2]
if a.output.resolve().is_relative_to(root) or a.repeats < 25:
    p.error('outside output and >=25 repeats required')
if a.same_executable_path and a.same_executable_path.resolve().is_relative_to(root):
    p.error('shared executable must be outside checkout')
commands, expected = {}, {}
for arm, directory in [('before', a.before), ('after', a.after)]:
    prepared = json.loads((directory / 'prepared.json').read_text())
    for name in a.control:
        key = arm + '/' + name
        commands[key] = prepared['commands'][name]
        expected[key] = (directory / (name + '.expected')).read_bytes()
samples = {key: [] for key in commands}
names = list(commands)
for rep in range(a.repeats + 1):
    for key in names[rep % len(names):] + names[:rep % len(names)]:
        command = commands[key]
        if a.same_executable_path:
            shutil.copyfile(command[0], a.same_executable_path)
            a.same_executable_path.chmod(0o755)
            command = [str(a.same_executable_path), *command[1:]]
        start = time.perf_counter_ns()
        result = subprocess.run(
            [a.argv0, *command[1:]] if a.argv0 else command,
            executable=command[0] if a.argv0 else None, capture_output=True)
        elapsed = (time.perf_counter_ns() - start) / 1e6
        if result.returncode or result.stderr or result.stdout != expected[key]:
            raise RuntimeError((key, result.returncode, result.stderr))
        if rep:
            samples[key].append(elapsed)
rows = {key: dict(min_ms=min(v), median_ms=statistics.median(v),
                  max_ms=max(v), samples_ms=v) for key, v in samples.items()}
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps(dict(repeats=a.repeats, argv0=a.argv0,
    shared_path=str(a.same_executable_path) if a.same_executable_path else None, rows=rows,
    method='Warm whole process, interleaved revisions, one warmup, exact output checked.'), indent=2) + '\n')
print({k: round(v['median_ms'], 3) for k, v in rows.items()})
