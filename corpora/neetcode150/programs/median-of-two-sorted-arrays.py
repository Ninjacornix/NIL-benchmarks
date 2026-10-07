import math

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

def median_of_two_sorted_arrays(data):
    q=Numbers(data); a=q.vector(); b=q.vector()
    if len(a)>len(b): a,b=b,a
    lo,hi=0,len(a); half=(len(a)+len(b)+1)//2
    while lo<=hi:
        i=(lo+hi)//2; j=half-i
        al=a[i-1] if i else -math.inf; ar=a[i] if i<len(a) else math.inf
        bl=b[j-1] if j else -math.inf; br=b[j] if j<len(b) else math.inf
        if al>br: hi=i-1
        elif bl>ar: lo=i+1
        else: return scalar(2*max(al,bl) if (len(a)+len(b))%2 else max(al,bl)+min(ar,br))
    raise AssertionError('sorted inputs')

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = median_of_two_sorted_arrays(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
