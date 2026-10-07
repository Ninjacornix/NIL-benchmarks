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

def rows(values):
    return b''.join(row(x) for x in values)

def k_closest_points_to_origin(data):
    q=Numbers(data);n,k=q.one(),q.one();a=[(q.one(),q.one()) for _ in range(n)];a.sort(key=lambda p:(p[0]**2+p[1]**2,p));return rows(a[:k])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = k_closest_points_to_origin(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
