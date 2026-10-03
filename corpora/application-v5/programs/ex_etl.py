import json
from pathlib import Path

def solve(input_path, output_path):
    legacy = json.loads(Path(input_path).read_bytes())["legacy"]
    result = {letter.lower(): int(score)
              for score, letters in legacy.items() for letter in letters}
    output = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    Path(output_path).write_bytes(output)
    return len(output)
