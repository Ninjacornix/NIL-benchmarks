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

def happy_number(data):
    def step(x):
        total=0
        while x:x,d=divmod(x,10);total+=d*d
        return total
    out=[]
    for x in Numbers(data).vector():
        slow=fast=x
        while True:
            slow=step(slow);fast=step(step(fast))
            if slow==fast:break
        out.append(int(slow==1))
    return row(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = happy_number(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
