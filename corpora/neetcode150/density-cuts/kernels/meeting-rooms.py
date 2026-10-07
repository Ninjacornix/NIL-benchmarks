def kernel(a):
    a = sorted(a)
    return all((a[i - 1][1] <= a[i][0] for i in range(1, len(a))))
