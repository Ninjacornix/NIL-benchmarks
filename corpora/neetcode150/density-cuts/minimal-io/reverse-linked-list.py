def kernel(n, head, a):
    out = []
    while head != -1:
        out.append(a[head][0])
        head = a[head][1]
    return out[::-1]

def solve(data):
    q=iter(map(int,data.split()))
    n=next(q)
    head=next(q)
    a=[[next(q), next(q)] for _ in range(n)]
    result=kernel(n,head,a)
    return (' '.join(map(str,result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
