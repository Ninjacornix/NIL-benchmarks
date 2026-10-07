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

def postorder(a,root):
    stack=[(root,False)] if root!=-1 else [];out=[]
    while stack:
        u,done=stack.pop()
        if done:out.append(u)
        else:
            stack.append((u,True));stack.extend((v,False) for v in a[u][1:] if v!=-1)
    return out

def diameter_of_binary_tree(data):
    a,root=tree(data);heights=[0]*len(a);best=0
    for u in postorder(a,root):
        l=heights[a[u][1]] if a[u][1]!=-1 else 0;r=heights[a[u][2]] if a[u][2]!=-1 else 0;best=max(best,l+r);heights[u]=max(l,r)+1
    return scalar(best)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = diameter_of_binary_tree(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
