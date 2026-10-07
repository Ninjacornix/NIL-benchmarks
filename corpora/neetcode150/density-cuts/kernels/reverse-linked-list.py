def kernel(n, head, a):
    out = []
    while head != -1:
        out.append(a[head][0])
        head = a[head][1]
    return out[::-1]
