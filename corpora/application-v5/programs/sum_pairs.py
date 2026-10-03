from pathlib import Path


def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = b"".join((str(sum(map(int, row.split(b",")))) + "\n").encode("ascii") for row in data.splitlines())
    Path(output_path).write_bytes(output)
    return len(output)
