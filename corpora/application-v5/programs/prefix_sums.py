from pathlib import Path


def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    values = list(map(int, data.splitlines()))
    total = 0
    rows = []
    for value in values:
        total += value
        rows.append(f"{total}\n")
    output = "".join(rows).encode("ascii")
    Path(output_path).write_bytes(output)
    return len(output)
