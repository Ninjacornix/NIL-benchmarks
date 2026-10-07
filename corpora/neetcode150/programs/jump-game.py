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

def jump_game(data):
    a=Numbers(data).vector();reach=0
    for i,x in enumerate(a):
        if i>reach:return scalar(False)
        reach=max(reach,i+x)
    return scalar(bool(a))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = jump_game(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
