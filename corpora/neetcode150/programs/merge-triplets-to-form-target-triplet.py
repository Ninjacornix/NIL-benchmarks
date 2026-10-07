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

def merge_triplets_to_form_target_triplet(data):
    q=Numbers(data);a=q.rows(3);target=[q.one() for _ in range(3)];best=[-10**18]*3
    for p in a:
        if all(x<=t for x,t in zip(p,target)):best=[max(x,y) for x,y in zip(best,p)]
    return scalar(best==target)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = merge_triplets_to_form_target_triplet(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
