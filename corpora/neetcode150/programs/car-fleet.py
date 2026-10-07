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

def car_fleet(data):
    q=Numbers(data); target=q.one(); a=q.rows(2); a.sort(reverse=True)
    fleets=0; numerator=0; denominator=1
    for pos,speed in a:
        distance=target-pos
        if distance*denominator>numerator*speed:
            fleets+=1; numerator=distance; denominator=speed
    return scalar(fleets)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = car_fleet(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
