def kernel(k, line):
    counts = [0] * 26
    left = best = peak = 0
    for i, x in enumerate(line):
        counts[x - 65] += 1
        peak = max(peak, counts[x - 65])
        if i - left + 1 - peak > k:
            counts[line[left] - 65] -= 1
            left += 1
        best = max(best, i - left + 1)
    return best
