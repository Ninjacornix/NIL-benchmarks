def kernel(target, a):
    a.sort(reverse=True)
    fleets = 0
    numerator = 0
    denominator = 1
    for pos, speed in a:
        distance = target - pos
        if distance * denominator > numerator * speed:
            fleets += 1
            numerator = distance
            denominator = speed
    return fleets

def solve(data):
    q=iter(map(int,data.split()))
    target=next(q)
    a=[[next(q) for _ in range(2)] for _ in range(next(q))]
    result=kernel(target,a)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
