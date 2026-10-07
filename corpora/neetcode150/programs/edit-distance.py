def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def edit_distance(data):
    a,b=data.split(b'\n')[:2];dp=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        old=dp[0];dp[0]=i
        for j,y in enumerate(b,1):prev=dp[j];dp[j]=old if x==y else 1+min(old,dp[j],dp[j-1]);old=prev
    return scalar(dp[-1])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = edit_distance(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
