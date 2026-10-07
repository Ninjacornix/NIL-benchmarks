def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def regular_expression_matching(data):
    text,pattern=data.split(b'\n')[:2];m=len(pattern);dp=[False]*(m+1);dp[0]=True
    for j in range(2,m+1):
        if pattern[j-1]==42:dp[j]=dp[j-2]
    for x in text:
        previous=dp;dp=[False]*(m+1)
        for j in range(1,m+1):
            if pattern[j-1]==42:dp[j]=dp[j-2] or (previous[j] and pattern[j-2] in (46,x))
            else:dp[j]=previous[j-1] and pattern[j-1] in (46,x)
    return scalar(dp[-1])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = regular_expression_matching(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
