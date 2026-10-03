from pathlib import Path

def solve(input_path, output_path):
    output = transform(Path(input_path).read_bytes())
    Path(output_path).write_bytes(output)
    return len(output)

import json

def transform(data):
    return (json.dumps(json.loads(data)['z'][0]) + "\n").encode()
