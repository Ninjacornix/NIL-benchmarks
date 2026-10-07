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
