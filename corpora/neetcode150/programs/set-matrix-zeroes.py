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

def grid(data):
    q=Numbers(data);r,c=q.one(),q.one();return r,c,[q.one() for _ in range(r*c)]

def set_matrix_zeroes(data):
    r,c,a=grid(data);rs=set();cs=set()
    for u,x in enumerate(a):
        if x==0:i,j=divmod(u,c);rs.add(i);cs.add(j)
    return row(0 if i in rs or j in cs else a[i*c+j] for i in range(r) for j in range(c))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = set_matrix_zeroes(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
