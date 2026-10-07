def kernel(coins, amount):
    dp = [0] + [amount + 1] * amount
    for i in range(1, amount + 1):
        for c in coins:
            if c <= i:
                dp[i] = min(dp[i], dp[i - c] + 1)
    return -1 if dp[-1] > amount else dp[-1]
