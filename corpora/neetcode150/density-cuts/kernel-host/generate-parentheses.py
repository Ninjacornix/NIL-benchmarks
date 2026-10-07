def kernel(n):
    out = []

    def visit(s, opened, closed):
        if closed == n:
            out.append(s)
            return
        if opened < n:
            visit(s + '(', opened + 1, closed)
        if closed < opened:
            visit(s + ')', opened, closed + 1)
    visit('', 0, 0)
    return out

def solve(data):
    n=int(data)
    result=kernel(n)
    return b''.join((r.encode() if isinstance(r,str) else r)+b'\n' for r in result)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
