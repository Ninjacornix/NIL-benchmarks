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

def rows(values):
    return b''.join(row(x) for x in values)

def subsets(data):
    a=sorted(Numbers(data).vector());out=[[]]
    for x in a:out += [s+[x] for s in out]
    return rows(sorted(out))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = subsets(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
