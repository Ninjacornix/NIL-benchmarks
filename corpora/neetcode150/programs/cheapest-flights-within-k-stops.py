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

def cheapest_flights_within_k_stops(data):
    q=Numbers(data); n,m,s,t,k=[q.one() for _ in range(5)]; edges=[[q.one() for _ in range(3)] for _ in range(m)]
    dist=[10**18]*n; dist[s]=0
    for _ in range(k+1):
        new=dist.copy()
        for u,v,w in edges: new[v]=min(new[v],dist[u]+w)
        dist=new
    return scalar(-1 if dist[t]==10**18 else dist[t])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = cheapest_flights_within_k_stops(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
