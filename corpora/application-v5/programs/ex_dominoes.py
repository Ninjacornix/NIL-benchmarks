from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    from collections import Counter
    pairs = [tuple(map(int, row.split(b","))) for row in data.splitlines()]
    if not pairs:
        return b"true\n"
    degree = Counter(vertex for pair in pairs for vertex in pair)
    seen = {pairs[0][0]}
    changed = True
    while changed:
        old = len(seen)
        for left, right in pairs:
            if left in seen or right in seen:
                seen.update((left, right))
        changed = len(seen) != old
    return b"true\n" if all(count % 2 == 0 for count in degree.values()) and len(seen) == len(degree) else b"false\n"
