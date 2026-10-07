def reconstruct_itinerary(data):
    tokens=data.split();adj={}
    for i in range(int(tokens[0])):adj.setdefault(tokens[1+2*i],[]).append(tokens[2+2*i])
    for a in adj.values():a.sort(reverse=True)
    stack=[b'AAA'];out=[]
    while stack:
        a=adj.get(stack[-1],[])
        if a:stack.append(a.pop())
        else:out.append(stack.pop())
    return b' '.join(reversed(out))+b'\n'

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = reconstruct_itinerary(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
