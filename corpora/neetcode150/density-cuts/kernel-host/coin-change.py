def kernel(coins, amount):
    dp = [0] + [amount + 1] * amount
    for i in range(1, amount + 1):
        for c in coins:
            if c <= i:
                dp[i] = min(dp[i], dp[i - c] + 1)
    return -1 if dp[-1] > amount else dp[-1]

def solve(data):
    q=iter(map(int,data.split()))
    coins=[next(q) for _ in range(next(q))]
    amount=next(q)
    result=kernel(coins,amount)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
