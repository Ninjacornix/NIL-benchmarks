from pathlib import Path


def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = data.replace(b"\r\n", b"\n")
    Path(output_path).write_bytes(output)
    return len(output)
