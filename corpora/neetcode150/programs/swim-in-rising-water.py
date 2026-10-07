import heapq

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

def neighbours(u,r,c):
    i,j=divmod(u,c)
    if i:yield u-c
    if i+1<r:yield u+c
    if j:yield u-1
    if j+1<c:yield u+1

def swim_in_rising_water(data):
    q=Numbers(data);n=q.one();a=[q.one() for _ in range(n*n)];dist=[10**18]*len(a);dist[0]=a[0];heap=[(a[0],0)]
    while heap:
        d,u=heapq.heappop(heap)
        if u==len(a)-1:return scalar(d)
        if d!=dist[u]:continue
        for v in neighbours(u,n,n):
            cost=max(d,a[v])
            if cost<dist[v]:dist[v]=cost;heapq.heappush(heap,(cost,v))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = swim_in_rising_water(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
