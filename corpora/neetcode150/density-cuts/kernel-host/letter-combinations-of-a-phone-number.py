import itertools

def kernel(data):
    letters = [b'abc', b'def', b'ghi', b'jkl', b'mno', b'pqrs', b'tuv', b'wxyz']
    return [bytes(x) for x in itertools.product(*(letters[d - 50] for d in data))] if data else []

def solve(data):
    result=kernel(data)
    return b''.join((r.encode() if isinstance(r,str) else r)+b'\n' for r in result)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
