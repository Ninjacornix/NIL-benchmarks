def kernel(a, lo, hi):
    lo, hi = (lo, hi)
    out = []
    inserted = False
    for x, y in a:
        if y < lo:
            out.append((x, y))
        elif x > hi:
            if not inserted:
                out.append((lo, hi))
                inserted = True
            out.append((x, y))
        else:
            lo = min(lo, x)
            hi = max(hi, y)
    if not inserted:
        out.append((lo, hi))
    return out

def solve(data):
    q=iter(map(int,data.split()))
    a=[[next(q) for _ in range(2)] for _ in range(next(q))]
    lo=next(q)
    hi=next(q)
    result=kernel(a,lo,hi)
    return b''.join((' '.join(map(str,r))+'\n').encode() for r in result)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
