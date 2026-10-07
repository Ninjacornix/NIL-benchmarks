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

def balanced_binary_tree(data):
    a,root=tree(data); heights=[0]*len(a); stack=[(root,False)] if root!=-1 else []; okay=True
    while stack:
        i,ready=stack.pop()
        if not ready:
            stack.append((i,True))
            for child in a[i][1:]:
                if child!=-1: stack.append((child,False))
        else:
            lh=heights[a[i][1]] if a[i][1]!=-1 else 0
            rh=heights[a[i][2]] if a[i][2]!=-1 else 0
            okay &= abs(lh-rh)<=1; heights[i]=max(lh,rh)+1
    return scalar(okay)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = balanced_binary_tree(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
