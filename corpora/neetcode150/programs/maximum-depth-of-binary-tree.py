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

def levels(a,root):
    queue=[root] if root!=-1 else [];out=[]
    while queue:
        out.append(queue);queue=[child for u in queue for child in a[u][1:] if child!=-1]
    return out

def maximum_depth_of_binary_tree(data):
    a,root=tree(data);return scalar(len(levels(a,root)))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = maximum_depth_of_binary_tree(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
