def encode_and_decode_strings(data):
    pos=data.index(b'\n')+1;count=int(data[:pos]);out=b''
    for _ in range(count):
        end=data.index(b'\n',pos);n=int(data[pos:end]);pos=end+1;value=data[pos:pos+n];pos+=n
        out+=str(n).encode()+b':'+value
    return out

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = encode_and_decode_strings(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
