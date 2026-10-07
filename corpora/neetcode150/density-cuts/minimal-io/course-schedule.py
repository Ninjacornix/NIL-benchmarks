import heapq

def topological(n, edges):
    adjacent = [[] for _ in range(n)]
    degree = [0] * n
    for u, v in edges:
        adjacent[u].append(v)
        degree[v] += 1
    heap = [i for i in range(n) if degree[i] == 0]
    heapq.heapify(heap)
    out = []
    while heap:
        u = heapq.heappop(heap)
        out.append(u)
        for v in adjacent[u]:
            degree[v] -= 1
            if degree[v] == 0:
                heapq.heappush(heap, v)
    return out if len(out) == n else None

def kernel(n, edges):
    return topological(n, edges) is not None

def solve(data):
    q=iter(map(int,data.split()))
    n=next(q)
    m=next(q)
    edges=[[next(q),next(q)] for _ in range(m)]
    result=kernel(n,edges)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
