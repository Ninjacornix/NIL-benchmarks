import collections

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

def sliding_window_maximum(data):
    q=Numbers(data);a=q.vector();k=q.one();queue=collections.deque();out=[]
    for i,x in enumerate(a):
        while queue and queue[0]<=i-k:queue.popleft()
        while queue and a[queue[-1]]<=x:queue.pop()
        queue.append(i)
        if i>=k-1:out.append(a[queue[0]])
    return row(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = sliding_window_maximum(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
