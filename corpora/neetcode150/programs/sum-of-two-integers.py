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

def sum_of_two_integers(data):
    q=Numbers(data);out=[]
    for _ in range(q.one()):
        a,b=q.one()&0xffffffff,q.one()&0xffffffff
        while b:a,b=(a^b)&0xffffffff,((a&b)<<1)&0xffffffff
        out.append(a if a<0x80000000 else a-0x100000000)
    return row(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = sum_of_two_integers(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
