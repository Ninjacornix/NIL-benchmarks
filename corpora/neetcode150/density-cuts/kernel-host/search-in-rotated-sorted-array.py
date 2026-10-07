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

def solve(data):
    q=iter(map(int,data.split()))
    a=[next(q) for _ in range(next(q))]
    target=next(q)
    result=kernel(a,target)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
