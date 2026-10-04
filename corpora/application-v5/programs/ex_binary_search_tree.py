from pathlib import Path
import json

def solve(input_path, output_path):
    values=json.loads(Path(input_path).read_text())['treeData']
    root=None
    for value in values:
        node={'data':value,'left':None,'right':None}
        if root is None: root=node; continue
        parent=root
        while True:
            side='left' if value<=parent['data'] else 'right'
            if parent[side] is None: parent[side]=node; break
            parent=parent[side]
    output=json.dumps(root,separators=(',',':')).encode()
    Path(output_path).write_bytes(output)
    return len(output)
