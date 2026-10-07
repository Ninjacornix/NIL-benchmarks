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

def koko_eating_bananas(data):
    q=Numbers(data);a=q.vector();h=q.one();lo,hi=1,max(a)
    while lo<hi:
        m=(lo+hi)//2
        if sum((x+m-1)//m for x in a)<=h:hi=m
        else:lo=m+1
    return scalar(lo)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = koko_eating_bananas(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
