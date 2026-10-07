def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def valid_palindrome(data):
    a = bytes(x+32 if 65<=x<=90 else x for x in data if 48<=x<=57 or 65<=x<=90 or 97<=x<=122)
    return scalar(a==a[::-1])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = valid_palindrome(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
