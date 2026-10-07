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

def reverse_nodes_in_k_group(data):
    q=Numbers(data);a=q.vector();k=q.one()
    for i in range(0,len(a)-k+1,k):a[i:i+k]=reversed(a[i:i+k])
    return row(a)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = reverse_nodes_in_k_group(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
