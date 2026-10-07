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

def partition_equal_subset_sum(data):
    a=Numbers(data).vector();total=sum(a)
    if total%2:return scalar(False)
    target=total//2;dp=bytearray(target+1);dp[0]=1
    for x in a:
        for j in range(target,x-1,-1):dp[j]|=dp[j-x]
    return scalar(dp[target])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = partition_equal_subset_sum(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
