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

def coin_change(data):
    q=Numbers(data); coins=q.vector(); amount=q.one(); dp=[0]+[amount+1]*amount
    for i in range(1,amount+1):
        for c in coins:
            if c<=i: dp[i]=min(dp[i],dp[i-c]+1)
    return scalar(-1 if dp[-1]>amount else dp[-1])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = coin_change(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
