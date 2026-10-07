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

def jump_game_ii(data):
    a=Numbers(data).vector();end=reach=count=0
    for i in range(len(a)-1):
        reach=max(reach,i+a[i])
        if i==end:count+=1;end=reach
    return scalar(count)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = jump_game_ii(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
