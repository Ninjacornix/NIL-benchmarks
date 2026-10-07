def kernel(a):
    a = sorted(a)
    out = []
    for i in range(len(a) - 2):
        if i and a[i] == a[i - 1]:
            continue
        l, r = (i + 1, len(a) - 1)
        while l < r:
            s = a[i] + a[l] + a[r]
            if s < 0:
                l += 1
            elif s > 0:
                r -= 1
            else:
                out.append((a[i], a[l], a[r]))
                l += 1
                r -= 1
                while l < r and a[l] == a[l - 1]:
                    l += 1
                while l < r and a[r] == a[r + 1]:
                    r -= 1
    return out
