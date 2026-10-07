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

def house_value(a):
    skip=take=0
    for x in a:skip,take=max(skip,take),skip+x
    return max(skip,take)

def house_robber_ii(data):
    a=Numbers(data).vector();return scalar(a[0] if len(a)==1 else max(house_value(a[:-1]),house_value(a[1:])))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = house_robber_ii(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
