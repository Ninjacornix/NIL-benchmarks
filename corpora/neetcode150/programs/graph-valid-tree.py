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

def union_count(data,mode):
    n,edges,_=graph(data);parent=list(range(n));rank=[0]*n;count=n;last=None
    def root(u):
        while u!=parent[u]:parent[u]=parent[parent[u]];u=parent[u]
        return u
    for u,v in edges:
        a,b=root(u),root(v)
        if a==b:last=(u,v);continue
        if rank[a]<rank[b]:a,b=b,a
        parent[b]=a;count-=1
        if rank[a]==rank[b]:rank[a]+=1
    if mode=='redundant':return row(last)
    return scalar(count if mode=='components' else n>0 and count==1 and len(edges)==n-1)

def graph_valid_tree(data):return union_count(data,'tree')

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = graph_valid_tree(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
