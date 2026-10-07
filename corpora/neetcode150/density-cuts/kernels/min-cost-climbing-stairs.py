def kernel(a):
    x = y = 0
    for cost in a:
        x, y = (y, cost + min(x, y))
    return min(x, y)
