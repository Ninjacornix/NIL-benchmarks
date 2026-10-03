from pathlib import Path


def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    values = list(map(int, data.splitlines()))
    output = f"{min(values)},{max(values)}\n".encode("ascii")
    Path(output_path).write_bytes(output)
    return len(output)
