from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    target, rest = data.split(b"\n", 1)
    values = list(map(int, rest.split(b","))) if rest else []
    left, right = 0, len(values)
    while left < right:
        middle = (left + right) // 2
        if values[middle] < int(target):
            left = middle + 1
        else:
            right = middle
    return (str(left) + "\n").encode() if left < len(values) and values[left] == int(target) else b"error\n"
