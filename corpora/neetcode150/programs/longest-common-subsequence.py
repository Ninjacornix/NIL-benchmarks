def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def longest_common_subsequence(data):
    a,b=data.split(b'\n')[:2];dp=[0]*(len(b)+1)
    for x in a:
        old=0
        for j,y in enumerate(b,1):prev=dp[j];dp[j]=old+1 if x==y else max(dp[j],dp[j-1]);old=prev
    return scalar(dp[-1])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = longest_common_subsequence(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
