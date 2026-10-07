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

def grid(data):
    q=Numbers(data);r,c=q.one(),q.one();return r,c,[q.one() for _ in range(r*c)]

def neighbours(u,r,c):
    i,j=divmod(u,c)
    if i:yield u-c
    if i+1<r:yield u+c
    if j:yield u-1
    if j+1<c:yield u+1

def island_sizes(data):
    r,c,a=grid(data);out=[]
    for start in range(len(a)):
        if a[start]!=1:continue
        a[start]=0;stack=[start];size=0
        while stack:
            u=stack.pop();size+=1
            for v in neighbours(u,r,c):
                if a[v]==1:a[v]=0;stack.append(v)
        out.append(size)
    return out

def max_area_of_island(data):return scalar(max(island_sizes(data),default=0))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = max_area_of_island(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
