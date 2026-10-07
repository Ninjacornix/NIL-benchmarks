def generate_parentheses(data):
    n=int(data); out=[]
    def visit(s,opened,closed):
        if closed==n: out.append(s); return
        if opened<n: visit(s+'(',opened+1,closed)
        if closed<opened: visit(s+')',opened,closed+1)
    visit('',0,0)
    return ('\n'.join(out)+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = generate_parentheses(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
