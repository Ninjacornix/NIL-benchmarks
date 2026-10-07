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

def tree(data):
    q=Numbers(data); n=q.one(); root=q.one(); a=[[q.one(),q.one(),q.one()] for _ in range(n)]
    return a,root

def count_good_nodes_in_binary_tree(data):
    a,r=tree(data);stack=[(r,-10**18)] if r!=-1 else [];count=0
    while stack:
        u,peak=stack.pop();count+=a[u][0]>=peak;stack.extend((v,max(peak,a[u][0])) for v in a[u][1:] if v!=-1)
    return scalar(count)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = count_good_nodes_in_binary_tree(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
