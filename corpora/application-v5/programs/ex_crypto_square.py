from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    clean = bytes(x for x in data.lower() if 97 <= x <= 122 or 48 <= x <= 57)
    if not clean:
        return b""
    columns = 1
    while columns * columns < len(clean):
        columns += 1
    rows = (len(clean) + columns - 1) // columns
    padded = clean.ljust(rows * columns, b" ")
    return b" ".join(padded[column::columns] for column in range(columns))
