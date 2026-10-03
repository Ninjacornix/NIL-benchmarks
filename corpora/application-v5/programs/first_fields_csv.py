from pathlib import Path


def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    rows = (data[:-1] if data.endswith(b"\n") else data).split(b"\n") if data else []
    output = b"".join(row.split(b",", 1)[0] + b"\n" for row in rows)
    Path(output_path).write_bytes(output)
    return len(output)
