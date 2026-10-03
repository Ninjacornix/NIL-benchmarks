from pathlib import Path


def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = b"".join(row + b"\n" for row in data.split(b"\n") if row)
    Path(output_path).write_bytes(output)
    return len(output)
