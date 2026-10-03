from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    number = int(data)
    return (str(sum(range(1, number + 1)) ** 2) + "\n").encode()
