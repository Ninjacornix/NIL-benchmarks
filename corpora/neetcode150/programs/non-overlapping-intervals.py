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

def non_overlapping_intervals(data):
    a=sorted(Numbers(data).rows(2),key=lambda p:p[1]);end=-10**18;removed=0
    for x,y in a:
        if x<end:removed+=1
        else:end=y
    return scalar(removed)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = non_overlapping_intervals(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
