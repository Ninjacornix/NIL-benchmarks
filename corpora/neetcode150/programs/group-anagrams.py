def group_anagrams(data):
    lines=data.split(b'\n');groups={}
    for w in lines[1:1+int(lines[0])]:groups.setdefault(bytes(sorted(w)),[]).append(w)
    return b''.join(b' '.join(sorted(groups[k]))+b'\n' for k in sorted(groups))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = group_anagrams(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
