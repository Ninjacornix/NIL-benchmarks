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

def three_sum(data):
    a = sorted(Numbers(data).vector()); out = []
    for i in range(len(a)-2):
        if i and a[i] == a[i-1]: continue
        l,r = i+1,len(a)-1
        while l<r:
            s = a[i]+a[l]+a[r]
            if s<0: l+=1
            elif s>0: r-=1
            else:
                out.append((a[i],a[l],a[r])); l+=1; r-=1
                while l<r and a[l]==a[l-1]: l+=1
                while l<r and a[r]==a[r+1]: r-=1
    return rows(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = three_sum(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
