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

def find_the_duplicate_number(data):
    a=Numbers(data).vector();s=f=a[0]
    while True:
        s=a[s];f=a[a[f]]
        if s==f:break
    s=a[0]
    while s!=f:s=a[s];f=a[f]
    return scalar(s)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = find_the_duplicate_number(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
