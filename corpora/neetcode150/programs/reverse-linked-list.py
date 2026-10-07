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

def reverse_linked_list(data):
    q=Numbers(data); n=q.one(); head=q.one(); a=[[q.one(),q.one()] for _ in range(n)]; out=[]
    while head!=-1: out.append(a[head][0]); head=a[head][1]
    return row(out[::-1])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = reverse_linked_list(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
