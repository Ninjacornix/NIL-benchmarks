def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def evaluate_reverse_polish_notation(data):
    tokens=data.split()[1:];stack=[]
    for x in tokens:
        if x in (b'+',b'-',b'*',b'/'):
            b,a=stack.pop(),stack.pop()
            value=a+b if x==b'+' else a-b if x==b'-' else a*b if x==b'*' else (abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1)
            stack.append(value)
        else:stack.append(int(x))
    return scalar(stack[-1])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = evaluate_reverse_polish_notation(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
