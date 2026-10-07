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

def minimum_interval_to_include_each_query(data):
    q=Numbers(data);a=sorted(q.rows(2));queries=q.vector();heap=[];i=0;out=[-1]*len(queries)
    for x,j in sorted((x,j) for j,x in enumerate(queries)):
        while i<len(a) and a[i][0]<=x:
            l,r=a[i];heapq.heappush(heap,(r-l+1,r));i+=1
        while heap and heap[0][1]<x:heapq.heappop(heap)
        if heap:out[j]=heap[0][0]
    return row(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = minimum_interval_to_include_each_query(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
