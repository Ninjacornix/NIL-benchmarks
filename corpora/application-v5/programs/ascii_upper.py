from pathlib import Path


def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = bytes(x - 32 if 97 <= x <= 122 else x for x in data)
    Path(output_path).write_bytes(output)
    return len(output)
