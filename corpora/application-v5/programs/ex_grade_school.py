from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    students = []
    seen = set()
    for row in data.splitlines():
        grade, name = row.split(b"\t", 1)
        if name not in seen:
            seen.add(name)
            students.append((int(grade), name))
    return b"".join(name + b"\n" for grade, name in sorted(students))
