from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    import json
    values = json.loads(data)
    result = []
    def visit(items):
        for item in items:
            if isinstance(item, list):
                visit(item)
            elif item is not None:
                result.append(item)
    visit(values)
    return b"".join((str(value) + "\n").encode() for value in result)
