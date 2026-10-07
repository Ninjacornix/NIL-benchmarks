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

def merge_two_sorted_lists(data):
    q=Numbers(data);a=q.vector();b=q.vector();out=[];i=j=0
    while i<len(a) or j<len(b):
        if j==len(b) or (i<len(a) and a[i]<=b[j]):out.append(a[i]);i+=1
        else:out.append(b[j]);j+=1
    return row(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = merge_two_sorted_lists(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
