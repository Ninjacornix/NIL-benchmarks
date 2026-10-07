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

def subsets_ii(data):
    a=sorted(Numbers(data).vector());out=[[]];old=0
    for i,x in enumerate(a):
        start=old if i and a[i-1]==x else 0;old=len(out);out += [out[j]+[x] for j in range(start,old)]
    return rows(sorted(out))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = subsets_ii(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
