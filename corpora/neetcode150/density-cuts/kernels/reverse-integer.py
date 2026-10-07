def kernel(a):
    out = []
    for value in a:
        negative = value < 0
        reversed_value = int(str(abs(value))[::-1])
        reversed_value = -reversed_value if negative else reversed_value
        out.append(reversed_value if -2 ** 31 <= reversed_value < 2 ** 31 else 0)
    return out
