def kernel(a):
    running = best = a[0]
    for x in a[1:]:
        running = max(x, running + x)
        best = max(best, running)
    return best

def solve(data):
    a=list(map(int, data.split()))[1:]
    result=kernel(a)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
