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

def kth_smallest_element_in_a_bst(data):
    q=Numbers(data);a,u=tree_from(q);k=q.one();stack=[]
    while True:
        while u!=-1:stack.append(u);u=a[u][1]
        u=stack.pop();k-=1
        if not k:return scalar(a[u][0])
        u=a[u][2]

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = kth_smallest_element_in_a_bst(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
