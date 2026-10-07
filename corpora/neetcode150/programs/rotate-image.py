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

def rotate_image(data):
    q=Numbers(data);n=q.one();a=[q.one() for _ in range(n*n)];return row(a[(n-1-j)*n+i] for i in range(n) for j in range(n))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = rotate_image(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
