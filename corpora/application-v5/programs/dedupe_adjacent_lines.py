from pathlib import Path


def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    rows = data.split(b"\n")
    if rows[-1] == b"":
        rows.pop()
    kept = [row for i, row in enumerate(rows) if i == 0 or row != rows[i - 1]]
    output = b"".join(row + b"\n" for row in kept)
    Path(output_path).write_bytes(output)
    return len(output)
