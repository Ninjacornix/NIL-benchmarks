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

def last_stone_weight(data):
    heap=[-x for x in Numbers(data).vector()]; heapq.heapify(heap)
    while len(heap)>1:
        a,b=-heapq.heappop(heap),-heapq.heappop(heap)
        if a!=b: heapq.heappush(heap,b-a)
    return scalar(-heap[0] if heap else 0)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = last_stone_weight(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
