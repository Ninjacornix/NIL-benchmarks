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

def gas_station(data):
    q=Numbers(data); gas=q.vector(); costs=q.vector(); prefix=0; low=0; start=0
    for i,(g,c) in enumerate(zip(gas,costs)):
        prefix+=g-c
        if prefix<low: low=prefix; start=i+1
    return scalar(start if gas and prefix>=0 else -1)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = gas_station(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
