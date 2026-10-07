"""Export minimal standalone originals, preserving transitive helper source."""
import ast
import json
from pathlib import Path
import reference
import cpp
HERE=Path(__file__).resolve().parent
PY_DRIVER='''\nif __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = SOLVE(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
'''
def python_source(slug):
    text=(HERE/'reference.py').read_text(); tree=ast.parse(text)
    defs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    target=reference.SOLVERS[slug].__name__; needed={target}; pending=[target]
    while pending:
        for name in (n.id for n in ast.walk(defs[pending.pop()]) if isinstance(n,ast.Name)):
            if name in defs and name not in needed: needed.add(name); pending.append(name)
    imports=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))]
    used={n.id for name in needed for n in ast.walk(defs[name]) if isinstance(n,ast.Name)}
    imports=[n for n in imports if any((a.asname or a.name.split('.')[0]) in used for a in n.names)]
    parts=[ast.get_source_segment(text,n) for n in imports]
    parts += [ast.get_source_segment(text,n) for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in needed]
    return '\n\n'.join(parts)+'\n'+PY_DRIVER.replace('SOLVE(',target+'(')
def main():
    out=HERE/'programs'; out.mkdir(exist_ok=True)
    tasks=json.loads((HERE/'tasks.json').read_text())['tasks']
    for t in tasks:
        slug=t['id']
        if slug in reference.SOLVERS: (out/(slug+'.py')).write_text(python_source(slug))
        if slug in cpp.B: (out/(slug+'.cpp')).write_text(cpp.source(slug))
    print('exported',len(list(out.glob('*.py'))),'Python,',len(list(out.glob('*.cpp'))),'C++')
if __name__=='__main__': main()
