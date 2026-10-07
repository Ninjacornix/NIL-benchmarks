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

def reorder_list(data):
    a=Numbers(data).vector();out=[];l,r=0,len(a)-1
    while l<=r:
        out.append(a[l]);l+=1
        if l<=r:out.append(a[r]);r-=1
    return row(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = reorder_list(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
