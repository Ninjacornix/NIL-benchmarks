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

def two_sum_ii_input_array_is_sorted(data):
    q=Numbers(data);a=q.vector();t=q.one();l,r=0,len(a)-1
    while l<r:
        s=a[l]+a[r]
        if s==t:return row([l,r])
        if s<t:l+=1
        else:r-=1
    raise ValueError('unique pair required')

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = two_sum_ii_input_array_is_sorted(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
