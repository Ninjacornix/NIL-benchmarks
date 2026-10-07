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

def find_minimum_in_rotated_sorted_array(data):
    a=Numbers(data).vector();lo,hi=0,len(a)-1
    while lo<hi:
        m=(lo+hi)//2
        if a[m]>a[hi]:lo=m+1
        else:hi=m
    return scalar(a[lo])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = find_minimum_in_rotated_sorted_array(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
