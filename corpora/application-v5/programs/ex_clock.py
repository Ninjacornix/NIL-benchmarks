from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    hour, minute = map(int, data.split(b","))
    minutes = (hour * 60 + minute) % 1440
    return f"{minutes // 60:02}:{minutes % 60:02}".encode()
