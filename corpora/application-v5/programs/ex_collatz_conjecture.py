from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    number = int(data)
    if number <= 0:
        return b"error\n"
    steps = 0
    while number != 1:
        number = 3 * number + 1 if number % 2 else number // 2
        steps += 1
    return (str(steps) + "\n").encode()
