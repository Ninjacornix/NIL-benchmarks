"""Candidate census, not an ownership proof. Existing corpus sources stay frozen."""
import argparse,importlib.util,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
if out.is_relative_to(ROOT):p.error('results must stay outside checkout')
out.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('suite',HERE.parent/'corpora/application-v5/external_suite.py');suite=importlib.util.module_from_spec(spec);spec.loader.exec_module(suite)
paths=[HERE.parent/'corpora/application-v5/programs'/(t['id']+'.nil') for t in suite.load_tasks() if t['nil_status']=='supported']
subprocess.run(['cargo','build','-p','nil-compiler','--locked','--offline'],cwd=ROOT,check=True)
rlib=max((ROOT/'target/debug/deps').glob('libnil_compiler-*.rlib'),key=lambda p:p.stat().st_mtime)
hir=max((ROOT/'target/debug/deps').glob('libnil_hir-*.rlib'),key=lambda p:p.stat().st_mtime)
bin=out/'census';subprocess.run(['rustc','--edition=2024',str(HERE/'proof_census.rs'),'--extern','nil_compiler='+str(rlib),'--extern','nil_hir='+str(hir),'-L','dependency='+str(ROOT/'target/debug/deps'),'-o',str(bin)],check=True)
text=subprocess.check_output([str(bin),*map(str,paths)],text=True)
rows=[]
for line in text.splitlines():
 path,candidates,last_use,fresh=line.split('\t');rows.append(dict(source=path,candidates=int(candidates),caller_last_use=int(last_use),fresh_entry_proofs=int(fresh)))
result={'method':'Conservative physical-origin sets plus semantic last uses. Fresh flat allocations have no earlier hidden aliases; live projections/aggregates and argument aliases prevent proof. Unknown calls/regions overapproximate. Entry proofs do not imply uniqueness after the callee creates aliases; runtime root guards remain mandatory.','corpus_programs':len(paths),'totals':{key:sum(r[key] for r in rows) for key in ['candidates','caller_last_use','fresh_entry_proofs']},'rows':rows}
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
