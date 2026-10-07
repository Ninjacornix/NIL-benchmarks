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

def reverse_integer(data):
    out=[]
    for value in Numbers(data).vector():
        negative=value<0; reversed_value=int(str(abs(value))[::-1]); reversed_value= -reversed_value if negative else reversed_value
        out.append(reversed_value if -(2**31)<=reversed_value<2**31 else 0)
    return row(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = reverse_integer(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
