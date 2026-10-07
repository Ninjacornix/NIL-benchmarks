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
