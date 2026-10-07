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

def neighbours(u,r,c):
    i,j=divmod(u,c)
    if i:yield u-c
    if i+1<r:yield u+c
    if j:yield u-1
    if j+1<c:yield u+1

def surrounded_regions(data):
    r,c,a=grid(data);stack=[]
    for u in range(len(a)):
        i,j=divmod(u,c)
        if (i==0 or j==0 or i==r-1 or j==c-1) and a[u]==1:a[u]=2;stack.append(u)
    while stack:
        u=stack.pop()
        for v in neighbours(u,r,c):
            if a[v]==1:a[v]=2;stack.append(v)
    return row(1 if x==2 else 0 for x in a)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = surrounded_regions(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
