from pathlib import Path
import json

def solve(input_path, output_path):
    text=Path(input_path).read_text('ascii')
    values=[int(x) for x in text.replace('\n', ',').split(',') if x]
    rows=[]; index=0
    while index<len(values):
        count=values[index]; rows.append(values[index+1:index+count+1]); index+=count+1
    queue=[0] if rows else []; seen=set(queue); result=[]
    for vertex in queue:
        result.append(vertex)
        for neighbor in rows[vertex]:
            if neighbor not in seen: seen.add(neighbor); queue.append(neighbor)
    output=json.dumps(result,separators=(',',':')).encode()
    Path(output_path).write_bytes(output)
    return len(output)
