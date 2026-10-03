from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    dates = data.splitlines()
    return b"true\n" if len({date[5:] for date in dates}) < len(dates) else b"false\n"
