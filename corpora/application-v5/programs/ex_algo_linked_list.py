from pathlib import Path
import json

def solve(input_path, output_path):
    text=Path(input_path).read_text('ascii')
    values=[int(x) for x in text.replace('\n', ',').split(',') if x]
    nodes=list(zip(values[::2],values[1::2])); result=[]
    index=0 if nodes else -1
    while index!=-1:
        value,index=nodes[index]; result.append(value)
    output=json.dumps(result,separators=(',',':')).encode()
    Path(output_path).write_bytes(output)
    return len(output)
