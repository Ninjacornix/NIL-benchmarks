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

def container_with_most_water(data):
    a=Numbers(data).vector();l,r,best=0,len(a)-1,0
    while l<r:
        best=max(best,(r-l)*min(a[l],a[r]))
        if a[l]<a[r]:l+=1
        else:r-=1
    return scalar(best)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = container_with_most_water(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
