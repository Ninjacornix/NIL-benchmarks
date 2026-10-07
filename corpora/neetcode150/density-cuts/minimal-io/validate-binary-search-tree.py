def kernel(a, root):
    stack = []
    current = root
    previous = None
    while current != -1 or stack:
        while current != -1:
            stack.append(current)
            current = a[current][1]
        current = stack.pop()
        value = a[current][0]
        if previous is not None and value <= previous:
            return False
        previous = value
        current = a[current][2]
    return True

def solve(data):
    q=iter(map(int,data.split()))
    n=next(q)
    root=next(q)
    a=[[next(q),next(q),next(q)] for _ in range(n)]
    result=kernel(a,root)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
