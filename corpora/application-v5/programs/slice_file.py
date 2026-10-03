from pathlib import Path


def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    header, payload = data.split(b"\n", 1)
    start, length = map(int, header.split(b","))
    output = payload[start:start + length]
    Path(output_path).write_bytes(output)
    return len(output)
