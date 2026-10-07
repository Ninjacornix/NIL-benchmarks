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

def lowest_common_ancestor_of_a_binary_search_tree(data):
    q=Numbers(data);a,u=tree_from(q);p,s=q.one(),q.one();lo,hi=sorted([a[p][0],a[s][0]])
    while True:
        if a[u][0]<lo:u=a[u][2]
        elif a[u][0]>hi:u=a[u][1]
        else:return scalar(u)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = lowest_common_ancestor_of_a_binary_search_tree(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
