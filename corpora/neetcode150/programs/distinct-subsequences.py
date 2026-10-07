def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def distinct_subsequences(data):
    a,b=data.split(b'\n')[:2];dp=[0]*(len(b)+1);dp[0]=1
    for x in a:
        for j in range(len(b),0,-1):
            if b[j-1]==x:dp[j]+=dp[j-1]
    return scalar(dp[-1])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = distinct_subsequences(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
