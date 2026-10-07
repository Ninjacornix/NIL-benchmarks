def kernel(r, c, a):
    r, c = (r, c)
    out = []
    top, left, bottom, right = (0, 0, r, c)
    while top < bottom and left < right:
        out.extend(a[top][left:right])
        top += 1
        out.extend((a[i][right - 1] for i in range(top, bottom)))
        right -= 1
        if top < bottom:
            out.extend(reversed(a[bottom - 1][left:right]))
            bottom -= 1
        if left < right:
            out.extend((a[i][left] for i in range(bottom - 1, top - 1, -1)))
            left += 1
    return out

def solve(data):
    q=iter(map(int,data.split()))
    r=next(q)
    c=next(q)
    a=[[next(q) for _ in range(c)] for _ in range(r)]
    result=kernel(r,c,a)
    return (' '.join(map(str,result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
