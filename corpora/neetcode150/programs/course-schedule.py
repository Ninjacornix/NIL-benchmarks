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

def topological(n,edges):
    adjacent=[[] for _ in range(n)]; degree=[0]*n
    for u,v in edges: adjacent[u].append(v); degree[v]+=1
    heap=[i for i in range(n) if degree[i]==0]; heapq.heapify(heap); out=[]
    while heap:
        u=heapq.heappop(heap); out.append(u)
        for v in adjacent[u]:
            degree[v]-=1
            if degree[v]==0: heapq.heappush(heap,v)
    return out if len(out)==n else None

def course_schedule(data):
    n,edges,_=graph(data)
    return scalar(topological(n,edges) is not None)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = course_schedule(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
