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

def largest_rectangle_in_histogram(data):
    a=Numbers(data).vector();stack=[];best=0
    for i,h in enumerate(a+[0]):
        start=i
        while stack and stack[-1][1]>h:
            start,height=stack.pop();best=max(best,height*(i-start))
        stack.append((start,h))
    return scalar(best)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = largest_rectangle_in_histogram(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
