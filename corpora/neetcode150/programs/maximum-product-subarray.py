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

def maximum_product_subarray(data):
    a=Numbers(data).vector();low=high=best=a[0]
    for x in a[1:]:low,high=min(x,low*x,high*x),max(x,low*x,high*x);best=max(best,high)
    return scalar(best)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = maximum_product_subarray(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
