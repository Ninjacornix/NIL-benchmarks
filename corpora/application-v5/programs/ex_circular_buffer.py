from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    from collections import deque
    lines = data.splitlines()
    capacity = int(lines[0])
    items = deque()
    output = []
    for line in lines[1:]:
        operation, value = map(int, line.split(b","))
        if operation == 0:
            output.append(str(items.popleft()) if items else "error")
        elif operation == 3:
            items.clear()
            output.append("ok")
        elif len(items) == capacity and operation == 1:
            output.append("error")
        else:
            if len(items) == capacity:
                items.popleft()
            items.append(value)
            output.append("ok")
    return "".join(value + "\n" for value in output).encode()
