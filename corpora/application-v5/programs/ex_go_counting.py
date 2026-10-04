from pathlib import Path

def solve(input_path, output_path):
    output = transform(Path(input_path).read_bytes())
    Path(output_path).write_bytes(output)
    return len(output)

import json


def transform(data):
    request = json.loads(data)
    board = request["board"]
    x, y = request["x"], request["y"]
    height, width = len(board), len(board[0])
    if not (0 <= x < width and 0 <= y < height):
        return b"error\n"
    todo = [(x, y)] if board[y][x] == " " else []
    territory, owners = set(todo), set()
    while todo:
        x, y = todo.pop()
        for xx, yy in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if not (0 <= xx < width and 0 <= yy < height):
                continue
            cell = board[yy][xx]
            if cell == " " and (xx, yy) not in territory:
                territory.add((xx, yy))
                todo.append((xx, yy))
            elif cell != " ":
                owners.add(cell)
    owner = "BLACK" if owners == {"B"} else "WHITE" if owners == {"W"} else "NONE"
    result = {"owner": owner, "territory": sorted(territory)}
    return json.dumps(result, separators=(",", ":")).encode()
