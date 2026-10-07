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

def linked_list_cycle(data):
    q=Numbers(data);n,head=q.one(),q.one();a=[[q.one(),q.one()] for _ in range(n)];slow=fast=head
    while fast!=-1 and a[fast][1]!=-1:
        slow=a[slow][1];fast=a[a[fast][1]][1]
        if slow==fast:return scalar(True)
    return scalar(False)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = linked_list_cycle(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
