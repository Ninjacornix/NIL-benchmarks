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

def min_cost_to_connect_all_points(data):
    q=Numbers(data);a=q.rows(2);n=len(a);seen=[False]*n;dist=[10**18]*n;total=0
    if n:dist[0]=0
    for _ in range(n):
        u=min((i for i in range(n) if not seen[i]),key=lambda i:dist[i]);total+=dist[u];seen[u]=True
        for v in range(n):
            if not seen[v]:dist[v]=min(dist[v],abs(a[u][0]-a[v][0])+abs(a[u][1]-a[v][1]))
    return scalar(total)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = min_cost_to_connect_all_points(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
