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

def target_sum(data):
    q=Numbers(data); a=q.vector(); target=q.one(); total=sum(a); dp=[0]*(2*total+1); dp[total]=1
    for x in a:
        new=[0]*len(dp)
        for i,count in enumerate(dp):
            if count:
                new[i+x]+=count; new[i-x]+=count
        dp=new
    return scalar(dp[total+target] if -total<=target<=total else 0)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = target_sum(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
