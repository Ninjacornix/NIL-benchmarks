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

def kth_largest_element_in_a_stream(data):
    q=Numbers(data);k=q.one();a=q.vector();stream=q.vector();heap=sorted(a,reverse=True)[:k];heapq.heapify(heap);out=[]
    for x in stream:
        if len(heap)<k:heapq.heappush(heap,x)
        elif x>heap[0]:heapq.heapreplace(heap,x)
        out.append(heap[0])
    return row(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = kth_largest_element_in_a_stream(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
