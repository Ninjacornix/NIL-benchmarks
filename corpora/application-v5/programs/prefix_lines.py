from pathlib import Path


def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    rows = data.split(b"\n")
    if rows[-1] == b"":
        rows.pop()
    output = b"\n".join(b">" + row for row in rows)
    if data.endswith(b"\n"):
        output += b"\n"
    Path(output_path).write_bytes(output)
    return len(output)
