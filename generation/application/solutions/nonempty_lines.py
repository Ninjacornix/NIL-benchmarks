def solve(input_path, output_path):
    with open(input_path, 'rb') as f:
        data = f.read()
    result = b''.join(row+b'\n' for row in data.split(b'\n') if row)
    with open(output_path, 'wb') as f:
        f.write(result)
    return len(result)
