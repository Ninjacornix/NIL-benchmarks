from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    basket = list(map(int, data.split(b","))) if data else []
    counts = tuple(basket.count(volume) for volume in range(1, 6))
    from functools import lru_cache
    prices = [0, 800, 1520, 2160, 2560, 3000]
    @lru_cache(None)
    def cost(state):
        if not any(state):
            return 0
        best = sum(state) * 800
        for mask in range(1, 32):
            selected = [i for i in range(5) if mask & (1 << i)]
            if all(state[i] for i in selected):
                remainder = tuple(value - (i in selected) for i, value in enumerate(state))
                best = min(best, prices[len(selected)] + cost(remainder))
        return best
    return (str(cost(counts)) + "\n").encode()
