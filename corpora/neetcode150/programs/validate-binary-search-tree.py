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

def validate_binary_search_tree(data):
    a,root=tree(data); stack=[]; current=root; previous=None
    while current!=-1 or stack:
        while current!=-1: stack.append(current); current=a[current][1]
        current=stack.pop(); value=a[current][0]
        if previous is not None and value<=previous: return scalar(False)
        previous=value; current=a[current][2]
    return scalar(True)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = validate_binary_search_tree(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
