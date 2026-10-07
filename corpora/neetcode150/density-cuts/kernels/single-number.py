def kernel(a):
    result = 0
    for value in a:
        result ^= value
    return result
