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

def tree_tokens(a,root):
    stack=[root];out=[]
    while stack:
        u=stack.pop()
        if u==-1:out.append(None)
        else:out.append(a[u][0]);stack.extend(reversed(a[u][1:]))
    return out

def subtree_of_another_tree(data):
    q=Numbers(data);a,r=tree_from(q);b,s=tree_from(q)
    if s==-1:return scalar(True)
    text=tree_tokens(a,r);pattern=tree_tokens(b,s);prefix=[0]*len(pattern);j=0
    for i in range(1,len(pattern)):
        while j and pattern[i]!=pattern[j]:j=prefix[j-1]
        if pattern[i]==pattern[j]:j+=1
        prefix[i]=j
    j=0
    for x in text:
        while j and x!=pattern[j]:j=prefix[j-1]
        if x==pattern[j]:j+=1
        if j==len(pattern):return scalar(True)
    return scalar(False)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = subtree_of_another_tree(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
