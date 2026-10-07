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

def best_time_to_buy_and_sell_stock(data):
    low=10**18;best=0
    for x in Numbers(data).vector():low=min(low,x);best=max(best,x-low)
    return scalar(best)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = best_time_to_buy_and_sell_stock(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
