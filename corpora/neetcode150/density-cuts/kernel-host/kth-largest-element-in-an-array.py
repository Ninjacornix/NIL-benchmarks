def kernel(a, k):
    return sorted(a)[-k]

def solve(data):
    q=iter(map(int,data.split()))
    a=[next(q) for _ in range(next(q))]
    k=next(q)
    result=kernel(a,k)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
