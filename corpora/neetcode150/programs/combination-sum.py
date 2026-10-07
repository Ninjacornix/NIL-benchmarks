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

def combinations(data,reusable):
    q=Numbers(data);a=sorted(q.vector());target=q.one();out=[]
    def visit(i,left,path):
        if left==0:out.append(path);return
        for j in range(i,len(a)):
            if j>i and a[j]==a[j-1]:continue
            if a[j]>left:break
            visit(j if reusable else j+1,left-a[j],path+[a[j]])
    visit(0,target,[]);return rows(out)

def combination_sum(data):return combinations(data,True)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = combination_sum(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
