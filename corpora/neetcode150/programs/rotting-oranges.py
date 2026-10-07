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

def rotting_oranges(data):
    r,c,a=grid(data);queue=collections.deque((i,0) for i,x in enumerate(a) if x==2);fresh=a.count(1);time=0
    while queue:
        u,time=queue.popleft()
        for v in neighbours(u,r,c):
            if a[v]==1:a[v]=2;fresh-=1;queue.append((v,time+1))
    return scalar(-1 if fresh else time)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = rotting_oranges(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
