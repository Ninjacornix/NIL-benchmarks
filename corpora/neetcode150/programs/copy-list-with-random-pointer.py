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

def rows(values):
    return b''.join(row(x) for x in values)

def copy_list_with_random_pointer(data):
    q=Numbers(data);n,head=q.one(),q.one();a=[[q.one() for _ in range(3)] for _ in range(n)];order=[]
    while head!=-1:order.append(head);head=a[head][1]
    index={old:i for i,old in enumerate(order)};index[-1]=-1
    return rows([a[u][0],index[a[u][1]],index[a[u][2]]] for u in order)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = copy_list_with_random_pointer(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
