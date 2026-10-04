from pathlib import Path
import json

def solve(input_path, output_path):
    text=Path(input_path).read_text('ascii')
    values=[int(x) for x in text.replace('\n', ',').split(',') if x]
    result=[]
    for lo,hi in sorted(zip(values[::2],values[1::2])):
        if not result or lo>result[-1][1]: result.append([lo,hi])
        else: result[-1][1]=max(result[-1][1],hi)
    output=json.dumps(result,separators=(',',':')).encode()
    Path(output_path).write_bytes(output)
    return len(output)
