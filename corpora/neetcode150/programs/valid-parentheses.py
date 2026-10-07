def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def valid_parentheses(data):
    stack=[];pairs={41:40,93:91,125:123}
    for x in data:
        if x in pairs:
            if not stack or stack.pop()!=pairs[x]:return scalar(False)
        else:stack.append(x)
    return scalar(not stack)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = valid_parentheses(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
