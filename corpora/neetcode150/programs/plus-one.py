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

def plus_one(data):
    a=Numbers(data).vector(); carry=1
    for i in range(len(a)-1,-1,-1): a[i],carry=(a[i]+carry)%10,(a[i]+carry)//10
    return row(([1] if carry else [])+a)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = plus_one(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
