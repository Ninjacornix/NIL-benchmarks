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

def find_median_from_data_stream(data):
    low=[];high=[];out=[]
    for x in Numbers(data).vector():
        heapq.heappush(low,-x);heapq.heappush(high,-heapq.heappop(low))
        if len(high)>len(low):heapq.heappush(low,-heapq.heappop(high))
        out.append(-2*low[0] if len(low)>len(high) else -low[0]+high[0])
    return row(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = find_median_from_data_stream(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
