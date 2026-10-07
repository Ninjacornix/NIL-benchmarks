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

def trapping_rain_water(data):
    a=Numbers(data).vector();l,r=0,len(a)-1;left=right=total=0
    while l<=r:
        if left<=right:left=max(left,a[l]);total+=left-a[l];l+=1
        else:right=max(right,a[r]);total+=right-a[r];r-=1
    return scalar(total)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = trapping_rain_water(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
