from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    if any(byte not in (48, 49) for byte in data):
        return b"null"
    return (str(int(data or b"0", 2)) + "\n").encode()
