def palindrome_partitioning(data):
    text=data.rstrip(b'\n');out=[]
    def visit(i,path):
        if i==len(text):out.append(b' '.join(path));return
        for j in range(i+1,len(text)+1):
            s=text[i:j]
            if s==s[::-1]:visit(j,path+[s])
    visit(0,[]);return b''.join(s+b'\n' for s in sorted(out))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = palindrome_partitioning(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
