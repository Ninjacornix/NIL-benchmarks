def kernel(a, target):
    total = sum(a)
    dp = [0] * (2 * total + 1)
    dp[total] = 1
    for x in a:
        new = [0] * len(dp)
        for i, count in enumerate(dp):
            if count:
                new[i + x] += count
                new[i - x] += count
        dp = new
    return dp[total + target] if -total <= target <= total else 0

def solve(data):
    q=iter(map(int,data.split()))
    a=[next(q) for _ in range(next(q))]
    target=next(q)
    result=kernel(a,target)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
