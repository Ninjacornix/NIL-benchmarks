def kernel(a):
    a = sorted(a)
    return all((a[i - 1][1] <= a[i][0] for i in range(1, len(a))))

def solve(data):
    q=iter(map(int,data.split()))
    a=[[next(q) for _ in range(2)] for _ in range(next(q))]
    result=kernel(a)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
