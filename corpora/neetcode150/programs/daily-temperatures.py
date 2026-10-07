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

def daily_temperatures(data):
    a=Numbers(data).vector();stack=[];out=[0]*len(a)
    for i,x in enumerate(a):
        while stack and a[stack[-1]]<x:
            j=stack.pop();out[j]=i-j
        stack.append(i)
    return row(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = daily_temperatures(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
