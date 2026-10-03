from pathlib import Path


def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    rows = data.split(b"\n")
    if rows[-1] == b"":
        rows.pop()
    output = b"".join(str(i).encode("ascii") + b":" + row + b"\n" for i, row in enumerate(rows, 1))
    Path(output_path).write_bytes(output)
    return len(output)
