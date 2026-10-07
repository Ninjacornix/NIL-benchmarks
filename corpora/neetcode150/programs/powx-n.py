def powx_n(data):
    tokens=data.split();out=[]
    for i in range(int(tokens[0])):
        a=float(tokens[1+2*i]);n=int(tokens[2+2*i]);negative=n<0;n=abs(n);result=1.0
        while n:
            if n%2:result*=a
            n//=2
            if n:a*=a
        if negative:result=1.0/result
        out.append(format(result,'.17e'))
    return ('\n'.join(out)+('\n' if out else '')).encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = powx_n(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
