from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    rolls = list(map(int, data.split(b","))) if data else []
    if any(value < 0 or value > 10 for value in rolls):
        return b"error\n"
    position = score = 0
    for frame in range(9):
        if position + 1 >= len(rolls):
            return b"error\n"
        if rolls[position] == 10:
            if position + 2 >= len(rolls):
                return b"error\n"
            score += sum(rolls[position:position+3])
            position += 1
        else:
            total = sum(rolls[position:position+2])
            if total > 10:
                return b"error\n"
            score += total
            if total == 10:
                if position + 2 >= len(rolls):
                    return b"error\n"
                score += rolls[position+2]
            position += 2
    last = rolls[position:]
    if len(last) < 2 or (last[0] < 10 and sum(last[:2]) > 10):
        return b"error\n"
    bonus = last[0] == 10 or sum(last[:2]) == 10
    if len(last) != (3 if bonus else 2) or (last[0] == 10 and last[1] < 10 and sum(last[1:]) > 10):
        return b"error\n"
    return (str(score + sum(last)) + "\n").encode()
