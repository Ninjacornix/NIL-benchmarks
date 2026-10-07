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

def grid(data):
    q=Numbers(data);r,c=q.one(),q.one();return r,c,[q.one() for _ in range(r*c)]

def neighbours(u,r,c):
    i,j=divmod(u,c)
    if i:yield u-c
    if i+1<r:yield u+c
    if j:yield u-1
    if j+1<c:yield u+1

def longest_increasing_path_in_a_matrix(data):
    r,c,a=grid(data);degree=[sum(a[v]<a[u] for v in neighbours(u,r,c)) for u in range(len(a))];front=[u for u in range(len(a)) if not degree[u]];length=0
    while front:
        length+=1;next_front=[]
        for u in front:
            for v in neighbours(u,r,c):
                if a[v]>a[u]:
                    degree[v]-=1
                    if not degree[v]:next_front.append(v)
        front=next_front
    return scalar(length)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = longest_increasing_path_in_a_matrix(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
