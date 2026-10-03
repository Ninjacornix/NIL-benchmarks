"""Frozen external contracts and independent canonical expected values."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

def load_tasks(group='all'):
    original = json.loads((HERE / 'tasks.json').read_text())['tasks']
    external = json.loads((HERE / 'external/tasks.json').read_text())['tasks']
    return original if group == 'original' else external if group == 'external' else original + external

def load_goldens():
    return json.loads((HERE / 'goldens.json').read_text()) | json.loads((HERE / 'external/goldens.json').read_text())

ANSWERS = json.loads((HERE / 'external/answers.json').read_text())

def external_expected(task, data):
    # Finite fixture oracle from upstream, not a reference-solution implementation.
    # Reject unknown inputs; do not claim a general-purpose algorithmic oracle.
    return bytes.fromhex(ANSWERS[task][data.hex()]['output'])
