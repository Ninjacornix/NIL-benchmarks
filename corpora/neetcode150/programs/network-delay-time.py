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

def graph(data,weighted=False):
    q=Numbers(data); n,m=q.one(),q.one(); extra=q.one() if weighted else None
    width=3 if weighted else 2; edges=[[q.one() for _ in range(width)] for _ in range(m)]
    return n,edges,extra

def network_delay_time(data):
    n,edges,s=graph(data,True); adjacent=[[] for _ in range(n)]
    for u,v,w in edges: adjacent[u].append((v,w))
    dist=[10**18]*n; dist[s]=0; heap=[(0,s)]
    while heap:
        d,u=heapq.heappop(heap)
        if d!=dist[u]: continue
        for v,w in adjacent[u]:
            if d+w<dist[v]: dist[v]=d+w; heapq.heappush(heap,(d+w,v))
    return scalar(-1 if 10**18 in dist else max(dist,default=0))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = network_delay_time(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
