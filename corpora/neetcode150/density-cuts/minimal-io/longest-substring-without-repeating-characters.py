def kernel(data):
    last = {}
    left = best = 0
    for i, x in enumerate(data):
        left = max(left, last.get(x, -1) + 1)
        last[x] = i
        best = max(best, i - left + 1)
    return best

def solve(data):
    result=kernel(data)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
