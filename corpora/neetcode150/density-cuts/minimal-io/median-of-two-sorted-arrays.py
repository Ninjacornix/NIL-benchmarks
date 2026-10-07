import math

def kernel(a, b):
    if len(a) > len(b):
        a, b = (b, a)
    lo, hi = (0, len(a))
    half = (len(a) + len(b) + 1) // 2
    while lo <= hi:
        i = (lo + hi) // 2
        j = half - i
        al = a[i - 1] if i else -math.inf
        ar = a[i] if i < len(a) else math.inf
        bl = b[j - 1] if j else -math.inf
        br = b[j] if j < len(b) else math.inf
        if al > br:
            hi = i - 1
        elif bl > ar:
            lo = i + 1
        else:
            return 2 * max(al, bl) if (len(a) + len(b)) % 2 else max(al, bl) + min(ar, br)
    raise AssertionError('sorted inputs')

def solve(data):
    q=iter(map(int,data.split()))
    a=[next(q) for _ in range(next(q))]
    b=[next(q) for _ in range(next(q))]
    result=kernel(a,b)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
