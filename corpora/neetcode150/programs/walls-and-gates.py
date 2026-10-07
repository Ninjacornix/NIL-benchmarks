import collections

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

def walls_and_gates(data):
    r,c,a=grid(data);dist=[-1 if x==-1 else 2147483647 for x in a];queue=collections.deque()
    for i,x in enumerate(a):
        if x==0:dist[i]=0;queue.append(i)
    while queue:
        u=queue.popleft()
        for v in neighbours(u,r,c):
            if dist[v]==2147483647:dist[v]=dist[u]+1;queue.append(v)
    return row(dist)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = walls_and_gates(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
