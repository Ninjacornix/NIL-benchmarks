"""Translate the pinned exercise's pseudocode operators to real callables."""
import json
from pathlib import Path


def accumulate(values, function):
    return [function(value) for value in values]


def solve(input_path, output_path):
    task = json.loads(Path(input_path).read_bytes())
    operators = {
        "(x) => x * x": lambda x: x * x,
        "(x) => upcase(x)": str.upper,
        "(x) => reverse(x)": lambda x: x[::-1],
        '(x) => accumulate(["1", "2", "3"], (y) => x + y)':
            lambda x: accumulate(["1", "2", "3"], lambda y: x + y),
    }
    values = accumulate(task["list"], operators[task["accumulator"]])
    result = "".join(str(value) + "\n" for value in values).encode()
    Path(output_path).write_bytes(result)
    return len(result)
