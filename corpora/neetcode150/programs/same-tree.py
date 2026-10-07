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

def tree_from(q):
    n,root=q.one(),q.one();return [[q.one() for _ in range(3)] for _ in range(n)],root

def same_tree(data):
    q=Numbers(data);a,r=tree_from(q);b,s=tree_from(q);stack=[(r,s)]
    while stack:
        u,v=stack.pop()
        if u==-1 or v==-1:
            if u!=v:return scalar(False)
        elif a[u][0]!=b[v][0]:return scalar(False)
        else:stack.extend(zip(a[u][1:],b[v][1:]))
    return scalar(True)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = same_tree(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
