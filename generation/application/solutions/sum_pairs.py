def solve(input_path, output_path):
    with open(input_path, 'rb') as f:
        data = f.read()
    result = b''.join((str(sum(map(int, row.split(b','))))+'\n').encode() for row in data.splitlines())
    with open(output_path, 'wb') as f:
        f.write(result)
    return len(result)
