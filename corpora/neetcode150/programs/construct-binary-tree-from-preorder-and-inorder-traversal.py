class Numbers:
    def __init__(self, data):
        self.it = iter(map(int, data.split()))
    def one(self):
        return next(self.it)
    def vector(self):
        return [self.one() for _ in range(self.one())]
    def rows(self, width):
        return [[self.one() for _ in range(width)] for _ in range(self.one())]

def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def rows(values):
    return b''.join(row(x) for x in values)

def construct_binary_tree_from_preorder_and_inorder_traversal(data):
    q=Numbers(data);pre=q.vector();ino=q.vector();a=[[x,-1,-1] for x in pre];stack=[];j=0
    for i,x in enumerate(pre):
        if stack:
            if a[stack[-1]][0]!=ino[j]:a[stack[-1]][1]=i
            else:
                while stack and a[stack[-1]][0]==ino[j]:parent=stack.pop();j+=1
                a[parent][2]=i
        stack.append(i)
    return rows(a)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = construct_binary_tree_from_preorder_and_inorder_traversal(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
