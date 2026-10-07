def kernel(gas, costs):
    prefix = 0
    low = 0
    start = 0
    for i, (g, c) in enumerate(zip(gas, costs)):
        prefix += g - c
        if prefix < low:
            low = prefix
            start = i + 1
    return start if gas and prefix >= 0 else -1

def solve(data):
    q=iter(map(int,data.split()))
    gas=[next(q) for _ in range(next(q))]
    costs=[next(q) for _ in range(next(q))]
    result=kernel(gas,costs)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
