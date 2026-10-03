def solve(input_path, output_path):
    with open(input_path, 'rb') as f:
        n = int(f.read())
    result = b''.join(f'{i}:{i*(i+1)//2}\n'.encode() for i in range(n))
    with open(output_path, 'wb') as f:
        f.write(result)
    return len(result)
