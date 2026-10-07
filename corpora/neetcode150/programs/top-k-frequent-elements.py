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

def top_k_frequent_elements(data):
    q=Numbers(data);counts=collections.Counter(q.vector());k=q.one();return row(sorted(counts,key=lambda x:(-counts[x],x))[:k])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = top_k_frequent_elements(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
