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

def insert_interval(data):
    q=Numbers(data); a=q.rows(2); lo,hi=q.one(),q.one(); out=[]; inserted=False
    for x,y in a:
        if y<lo: out.append((x,y))
        elif x>hi:
            if not inserted: out.append((lo,hi)); inserted=True
            out.append((x,y))
        else: lo=min(lo,x); hi=max(hi,y)
    if not inserted: out.append((lo,hi))
    return rows(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = insert_interval(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
