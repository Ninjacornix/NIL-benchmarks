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

def spiral_matrix(data):
    q=Numbers(data); r,c=q.one(),q.one(); a=[[q.one() for _ in range(c)] for _ in range(r)]; out=[]
    top,left,bottom,right=0,0,r,c
    while top<bottom and left<right:
        out.extend(a[top][left:right]); top+=1
        out.extend(a[i][right-1] for i in range(top,bottom)); right-=1
        if top<bottom: out.extend(reversed(a[bottom-1][left:right])); bottom-=1
        if left<right: out.extend(a[i][left] for i in range(bottom-1,top-1,-1)); left+=1
    return row(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = spiral_matrix(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
