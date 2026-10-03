from pathlib import Path


def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    pairs = [tuple(map(int, row.split(b","))) for row in data.splitlines()]
    left = [x for x, _ in pairs]
    right = [y for _, y in pairs]
    output = (str(dot(left, right)) + "\n").encode("ascii")
    Path(output_path).write_bytes(output)
    return len(output)


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))
