from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    n = data[0] - 65
    lines = []
    for row in range(2*n + 1):
        offset = n - abs(row-n)
        line = bytearray(b" " * (2*n + 1))
        line[n-offset] = line[n+offset] = 65+offset
        lines.append(bytes(line) + b"\n")
    return b"".join(lines)
