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

def scalar(value):
    return row([int(value)])

def hand_of_straights(data):
    q=Numbers(data);a=q.vector();size=q.one();counts=collections.Counter(a)
    if len(a)%size:return scalar(False)
    for x in sorted(counts):
        count=counts[x]
        if count:
            for y in range(x,x+size):
                if counts[y]<count:return scalar(False)
                counts[y]-=count
    return scalar(True)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = hand_of_straights(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
