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

def merge_intervals(data):
    a=sorted(Numbers(data).rows(2));out=[]
    for x,y in a:
        if out and x<=out[-1][1]:out[-1][1]=max(out[-1][1],y)
        else:out.append([x,y])
    return rows(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = merge_intervals(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
