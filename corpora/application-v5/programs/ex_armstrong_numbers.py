from pathlib import Path

def solve(input_path, output_path):
    output = transform(Path(input_path).read_bytes())
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    number = int(data)
    digits = str(number)
    matches = sum(int(digit) ** len(digits) for digit in digits) == number
    return b'true\n' if matches else b'false\n'
