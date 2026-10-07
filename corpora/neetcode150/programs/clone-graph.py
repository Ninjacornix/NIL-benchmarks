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

def rows(values):
    return b''.join(row(x) for x in values)

def clone_graph(data):
    q=Numbers(data);n,m=q.one(),q.one();adj=[set() for _ in range(n)]
    for _ in range(m):u,v=q.one(),q.one();adj[u].add(v);adj[v].add(u)
    start=q.one();seen=set();stack=[start] if start!=-1 else []
    while stack:
        u=stack.pop()
        if u in seen:continue
        seen.add(u);stack.extend(adj[u]-seen)
    return row(sorted(seen))+rows([u]+sorted(adj[u]) for u in sorted(seen))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = clone_graph(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
