def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def word_search(data):
    lines=data.split(b'\n');r,c=map(int,lines[0].split());board=lines[1:1+r];word=lines[1+r];seen=set()
    def visit(i,j,k):
        if k==len(word):return True
        if not (0<=i<r and 0<=j<c) or (i,j) in seen or board[i][j]!=word[k]:return False
        seen.add((i,j));result=any(visit(u,v,k+1) for u,v in ((i+1,j),(i-1,j),(i,j-1),(i,j+1)));seen.remove((i,j));return result
    return scalar(not word or any(visit(i,j,0) for i in range(r) for j in range(c)))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = word_search(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
