def solve(input_path, output_path):
    with open(input_path, 'rb') as f:
        data = f.read()
    result = bytes(c-32 if 97 <= c <= 122 else c for c in data)
    with open(output_path, 'wb') as f:
        f.write(result)
    return len(result)
