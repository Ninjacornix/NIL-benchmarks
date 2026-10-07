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

def kth_largest_element_in_an_array(data):
    q=Numbers(data); a=q.vector(); k=q.one()
    return scalar(sorted(a)[-k])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = kth_largest_element_in_an_array(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
