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

def product_of_array_except_self(data):
    a=Numbers(data).vector();out=[];prod=1
    for x in a:out.append(prod);prod*=x
    prod=1
    for i in range(len(a)-1,-1,-1):out[i]*=prod;prod*=a[i]
    return row(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = product_of_array_except_self(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
