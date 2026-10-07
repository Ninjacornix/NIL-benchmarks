import heapq

def kernel(a):
    heap = [-x for x in a]
    heapq.heapify(heap)
    while len(heap) > 1:
        a, b = (-heapq.heappop(heap), -heapq.heappop(heap))
        if a != b:
            heapq.heappush(heap, b - a)
    return -heap[0] if heap else 0

def solve(data):
    a=list(map(int, data.split()))[1:]
    result=kernel(a)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
