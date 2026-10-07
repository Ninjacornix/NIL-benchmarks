def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def interleaving_string(data):
    a,b,c=data.split(b'\n')[:3]
    if len(a)+len(b)!=len(c):return scalar(False)
    dp=[False]*(len(b)+1);dp[0]=True
    for j in range(1,len(b)+1):dp[j]=dp[j-1] and b[j-1]==c[j-1]
    for i in range(1,len(a)+1):
        dp[0]=dp[0] and a[i-1]==c[i-1]
        for j in range(1,len(b)+1):dp[j]=(dp[j] and a[i-1]==c[i+j-1]) or (dp[j-1] and b[j-1]==c[i+j-1])
    return scalar(dp[-1])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = interleaving_string(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
