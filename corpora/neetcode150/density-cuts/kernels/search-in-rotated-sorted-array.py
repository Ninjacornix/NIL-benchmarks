def kernel(a, target):
    lo, hi = (0, len(a) - 1)
    while lo <= hi:
        m = (lo + hi) // 2
        if a[m] == target:
            return m
        if a[lo] <= a[m]:
            if a[lo] <= target < a[m]:
                hi = m - 1
            else:
                lo = m + 1
        elif a[m] < target <= a[hi]:
            lo = m + 1
        else:
            hi = m - 1
    return -1
