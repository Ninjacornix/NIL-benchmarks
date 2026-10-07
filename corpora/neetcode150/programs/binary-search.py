import bisect

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

def binary_search(data):
    q=Numbers(data);a=q.vector();t=q.one();i=bisect.bisect_left(a,t);return scalar(i if i<len(a) and a[i]==t else -1)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = binary_search(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
