from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    header, rest = data.split(b"\n", 1)
    source, target = map(int, header.split(b","))
    digits = list(map(int, rest.split(b","))) if rest else []
    if source < 2 or target < 2 or any(d < 0 or d >= source for d in digits):
        return b"error\n"
    value = 0
    for digit in digits:
        value = value * source + digit
    result = []
    while value:
        result.append(value % target)
        value //= target
    return b"".join((str(d) + "\n").encode() for d in reversed(result or [0]))
