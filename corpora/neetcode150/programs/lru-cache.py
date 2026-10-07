import collections

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

def rows(values):
    return b''.join(row(x) for x in values)

def lru_cache(data):
    q=Numbers(data); cap=q.one(); count=q.one(); cache=collections.OrderedDict(); out=[]
    for _ in range(count):
        op,key=q.one(),q.one()
        if op==0:
            val=q.one(); cache.pop(key,None)
            if cap: cache[key]=val
            while len(cache)>cap: cache.popitem(last=False)
        elif key in cache:
            val=cache.pop(key); cache[key]=val; out.append(val)
        else: out.append(-1)
    return rows([x] for x in out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = lru_cache(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
