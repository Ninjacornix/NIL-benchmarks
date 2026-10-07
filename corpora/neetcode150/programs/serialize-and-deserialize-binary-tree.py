class Numbers:
    def __init__(self, data):
        self.it = iter(map(int, data.split()))
    def one(self):
        return next(self.it)
    def vector(self):
        return [self.one() for _ in range(self.one())]
    def rows(self, width):
        return [[self.one() for _ in range(width)] for _ in range(self.one())]

def tree(data):
    q=Numbers(data); n=q.one(); root=q.one(); a=[[q.one(),q.one(),q.one()] for _ in range(n)]
    return a,root

def tree_tokens(a,root):
    stack=[root];out=[]
    while stack:
        u=stack.pop()
        if u==-1:out.append(None)
        else:out.append(a[u][0]);stack.extend(reversed(a[u][1:]))
    return out

def serialize_and_deserialize_binary_tree(data):
    a,r=tree(data);return (' '.join('#' if x is None else str(x) for x in tree_tokens(a,r))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = serialize_and_deserialize_binary_tree(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
