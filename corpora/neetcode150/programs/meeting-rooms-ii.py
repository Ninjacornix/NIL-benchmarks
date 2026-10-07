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

def meeting_rooms_ii(data):
    a=Numbers(data).rows(2);events=sorted([(x,1) for x,y in a]+[(y,-1) for x,y in a]);count=best=0
    for _,d in events:count+=d;best=max(best,count)
    return scalar(best)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = meeting_rooms_ii(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
