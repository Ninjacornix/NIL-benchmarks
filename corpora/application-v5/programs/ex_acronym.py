from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    words = data.replace(b"-", b" ").split()
    return bytes(word.lstrip(b"_'")[0] for word in words if word.lstrip(b"_'")).upper()
