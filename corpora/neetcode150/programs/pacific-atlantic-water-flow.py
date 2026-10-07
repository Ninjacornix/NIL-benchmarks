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

def grid(data):
    q=Numbers(data);r,c=q.one(),q.one();return r,c,[q.one() for _ in range(r*c)]

def neighbours(u,r,c):
    i,j=divmod(u,c)
    if i:yield u-c
    if i+1<r:yield u+c
    if j:yield u-1
    if j+1<c:yield u+1

def pacific_atlantic_water_flow(data):
    r,c,a=grid(data)
    if not a:return b''
    def flood(starts):
        seen=set(starts);stack=list(seen)
        while stack:
            u=stack.pop()
            for v in neighbours(u,r,c):
                if v not in seen and a[v]>=a[u]:seen.add(v);stack.append(v)
        return seen
    first=flood(list(range(c))+list(range(0,r*c,c)));second=flood(list(range((r-1)*c,r*c))+list(range(c-1,r*c,c)))
    return rows(divmod(u,c) for u in sorted(first&second))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = pacific_atlantic_water_flow(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
