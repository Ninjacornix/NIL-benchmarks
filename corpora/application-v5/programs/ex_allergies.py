from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    names = ["eggs", "peanuts", "shellfish", "strawberries", "tomatoes", "chocolate", "pollen", "cats"]
    score, item = data.split(b"\n", 1)
    index = names.index(item.decode())
    return b"true\n" if int(score) & (1 << index) else b"false\n"
