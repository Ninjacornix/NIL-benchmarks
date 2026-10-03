from pathlib import Path

def solve(input_path, output_path):
    output = transform(Path(input_path).read_bytes())
    Path(output_path).write_bytes(output)
    return len(output)

import json

def transform(data):
    square = json.loads(data)['square']
    return (str(1 << (square - 1)) if 1 <= square <= 64 else 'error').encode() + b'\n'
