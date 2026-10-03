from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    first, second = data.split(b"\n", 1)
    if len(first) != len(second):
        return b"error\n"
    return (str(sum(a != b for a, b in zip(first, second))) + "\n").encode()
