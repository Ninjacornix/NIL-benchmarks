def multiply_strings(data):
    a,b=data.splitlines()[:2];out=[0]*(len(a)+len(b))
    for i in range(len(a)-1,-1,-1):
        for j in range(len(b)-1,-1,-1):
            x=out[i+j+1]+(a[i]-48)*(b[j]-48);out[i+j+1]=x%10;out[i+j]+=x//10
    result=''.join(map(str,out)).lstrip('0') or '0';return (result+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = multiply_strings(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
