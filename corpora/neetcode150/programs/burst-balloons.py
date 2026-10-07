class Numbers:
    def __init__(self, data):
        self.it = iter(map(int, data.split()))
    def one(self):
        return next(self.it)
    def vector(self):
        return [self.one() for _ in range(self.one())]
    def rows(self, width):
        return [[self.one() for _ in range(width)] for _ in range(self.one())]

def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def burst_balloons(data):
    a=[1]+Numbers(data).vector()+[1];n=len(a);dp=[[0]*n for _ in range(n)]
    for width in range(2,n):
        for l in range(n-width):
            r=l+width;dp[l][r]=max((dp[l][k]+dp[k][r]+a[l]*a[k]*a[r] for k in range(l+1,r)),default=0)
    return scalar(dp[0][-1])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = burst_balloons(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
