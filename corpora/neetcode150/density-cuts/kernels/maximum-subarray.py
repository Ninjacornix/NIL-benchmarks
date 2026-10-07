def kernel(a):
    running = best = a[0]
    for x in a[1:]:
        running = max(x, running + x)
        best = max(best, running)
    return best
