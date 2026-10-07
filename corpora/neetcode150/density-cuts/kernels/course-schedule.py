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
