from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    rows = [row.replace(b" ", b"") for row in data.splitlines()]
    if not rows:
        return b""
    height, width = len(rows), len(rows[0])
    for symbol in (88, 79):
        starts = [(y, 0) for y in range(height)] if symbol == 88 else [(0, x) for x in range(width)]
        todo = [(y, x) for y, x in starts if rows[y][x] == symbol]
        seen = set(todo)
        while todo:
            y, x = todo.pop()
            if symbol == 88 and x == width-1 or symbol == 79 and y == height-1:
                return bytes([symbol])
            for dy, dx in [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]:
                yy, xx = y+dy, x+dx
                if 0 <= yy < height and 0 <= xx < width and (yy, xx) not in seen and rows[yy][xx] == symbol:
                    seen.add((yy, xx))
                    todo.append((yy, xx))
    return b""
