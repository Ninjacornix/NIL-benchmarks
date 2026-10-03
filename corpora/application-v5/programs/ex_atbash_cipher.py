from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    clean = bytes(219 - byte if 97 <= byte <= 122 else byte for byte in data.lower() if 97 <= byte <= 122 or 48 <= byte <= 57)
    return b" ".join(clean[i:i+5] for i in range(0, len(clean), 5))
