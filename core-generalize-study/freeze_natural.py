import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent; suite=root.parent; corpus=suite/'corpora/neetcode150'
rows=[]
for p in sorted((corpus/'programs').glob('*.nil')):
 data=subprocess.check_output(['git','show','6fd268d:corpora/neetcode150/programs/'+p.name],cwd=suite)
 target=root/'natural'/p.name
 if target.exists() and target.read_bytes()!=data:raise RuntimeError('refusing to overwrite natural source '+p.name)
 target.write_bytes(data)
 rows.append(dict(task=p.stem,natural_sha256=hashlib.sha256(data).hexdigest(),tuned_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),differs=data!=p.read_bytes()))
(root/'NATURAL.json').write_text(json.dumps(dict(schema=1,revision='6fd268d',method='Byte-exact Round 19 admitted sources, before performance cliffs were known. No corrections or performance rewrites.',tasks=rows,held_out=114),indent=2)+'\n')
print('NATURAL',len(rows),'unchanged',sum(not r['differs'] for r in rows),'rewritten',sum(r['differs'] for r in rows))
