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

def remove_nth_node_from_end_of_list(data):
    q=Numbers(data);a=q.vector();k=q.one();del a[len(a)-k];return row(a)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = remove_nth_node_from_end_of_list(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
