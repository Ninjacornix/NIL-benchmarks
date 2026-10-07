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

def merge_k_sorted_lists(data):
    q=Numbers(data);lists=[q.vector() for _ in range(q.one())];heap=[(a[0],i,0) for i,a in enumerate(lists) if a];heapq.heapify(heap);out=[]
    while heap:
        x,i,j=heapq.heappop(heap);out.append(x);j+=1
        if j<len(lists[i]):heapq.heappush(heap,(lists[i][j],i,j))
    return row(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = merge_k_sorted_lists(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
