import heapq

def kernel(a):
    heap = [-x for x in a]
    heapq.heapify(heap)
    while len(heap) > 1:
        a, b = (-heapq.heappop(heap), -heapq.heappop(heap))
        if a != b:
            heapq.heappush(heap, b - a)
    return -heap[0] if heap else 0
