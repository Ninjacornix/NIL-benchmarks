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

def two_sum(data):
    q=Numbers(data);a=q.vector();target=q.one();seen={}
    for i,x in enumerate(a):
        if target-x in seen:return row([seen[target-x],i])
        seen[x]=i
    raise ValueError('unique pair required')

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = two_sum(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
