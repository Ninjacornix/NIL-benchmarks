from pathlib import Path
import json

def solve(input_path, output_path):
    text=Path(input_path).read_text('ascii')
    values=[int(x) for x in text.replace('\n', ',').split(',') if x]
    nodes=[]
    for value in values:
        if not nodes: nodes.append([value,-1,-1]); continue
        index=0
        while True:
            side=1 if value<=nodes[index][0] else 2
            child=nodes[index][side]
            if child<0:
                nodes[index][side]=len(nodes); nodes.append([value,-1,-1]); break
            index=child
    result=[]
    def visit(index):
        if index<0: return
        value,left,right=nodes[index]; visit(left); result.append(value); visit(right)
    if nodes: visit(0)
    output=json.dumps(result,separators=(',',':')).encode()
    Path(output_path).write_bytes(output)
    return len(output)
