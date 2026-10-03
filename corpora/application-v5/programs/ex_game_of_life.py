from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    rows = data.splitlines()
    if not rows:
        return b""
    height, width = len(rows), len(rows[0])
    output = []
    for y, row in enumerate(rows):
        result = bytearray(row)
        for x, value in enumerate(row):
            neighbors = sum(rows[yy][xx] == 49 for yy in range(max(0, y-1), min(height, y+2)) for xx in range(max(0, x-1), min(width, x+2)) if (xx, yy) != (x, y))
            result[x] = 49 if neighbors == 3 or value == 49 and neighbors == 2 else 48
        output.append(bytes(result) + b"\n")
    return b"".join(output)
