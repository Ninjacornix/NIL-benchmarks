def kernel(a):
    carry = 1
    for i in range(len(a) - 1, -1, -1):
        a[i], carry = ((a[i] + carry) % 10, (a[i] + carry) // 10)
    return ([1] if carry else []) + a
