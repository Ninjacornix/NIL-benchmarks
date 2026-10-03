from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    header, rest = data.split(b"\n", 1)
    target = int(header)
    coins = list(map(int, rest.split(b","))) if rest else []
    if target < 0:
        return b"error\n"
    best = [0] + [target+1] * target
    previous = [0] * (target+1)
    for value in range(1, target+1):
        for coin in coins:
            if coin <= value and best[value-coin]+1 < best[value]:
                best[value] = best[value-coin]+1
                previous[value] = coin
    if best[target] > target:
        return b"error\n"
    result = []
    while target:
        result.append(previous[target])
        target -= previous[target]
    return b"".join((str(coin) + "\n").encode() for coin in sorted(result))
