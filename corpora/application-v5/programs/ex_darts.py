from pathlib import Path

def solve(input_path, output_path):
    output = transform(Path(input_path).read_bytes())
    Path(output_path).write_bytes(output)
    return len(output)

import json

def transform(data):
    point = json.loads(data)
    squared = point['x'] ** 2 + point['y'] ** 2
    score = 10 if squared <= 1 else 5 if squared <= 25 else 1 if squared <= 100 else 0
    return f'{score}\n'.encode()
