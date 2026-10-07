def kernel(data):
    last = {}
    left = best = 0
    for i, x in enumerate(data):
        left = max(left, last.get(x, -1) + 1)
        last[x] = i
        best = max(best, i - left + 1)
    return best
