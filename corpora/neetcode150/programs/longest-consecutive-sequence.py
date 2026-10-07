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

def longest_consecutive_sequence(data):
    values=set(Numbers(data).vector());best=0
    for x in values:
        if x-1 not in values:
            end=x
            while end in values:end+=1
            best=max(best,end-x)
    return scalar(best)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = longest_consecutive_sequence(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
