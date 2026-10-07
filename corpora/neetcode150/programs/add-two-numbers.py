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

def add_two_numbers(data):
    q=Numbers(data);a=q.vector();b=q.vector();out=[];carry=0
    for i in range(max(len(a),len(b))):
        x=(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0)+carry;out.append(x%10);carry=x//10
    if carry:out.append(carry)
    return row(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = add_two_numbers(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
