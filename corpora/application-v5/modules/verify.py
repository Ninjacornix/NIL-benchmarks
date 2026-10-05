"""Alternate module sources, unchanged corpus tasks/oracles/goldens/baselines."""
import sys,json,tempfile,argparse
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import verify as corpus
from external_suite import load_tasks,load_goldens
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
corpus.application.prepare();corpus.application.expected=corpus.expected
rows=[]
with tempfile.TemporaryDirectory(prefix='nil-split-corpus-') as directory:
 for task in load_tasks('original'):
  if task['id'] not in ['count_newlines','sum_integers']:continue
  golden=load_goldens()[task['id']]
  assert corpus.expected(task['id'],bytes.fromhex(golden['input']),golden['environment'])==bytes.fromhex(golden['output'])
  task=task|{'inputs':task['inputs']+[golden['input']]}
  folder=Path(directory)/task['id'];folder.mkdir()
  result=corpus.application.evaluate((HERE/(task['id']+'.nil')).read_text(),'expr-v5',task,folder,[HERE/'reports.nil-module'])
  rows.append({'task':task['id'],**result});print(rows[-1],flush=True)
report={'results':rows,'reference_checks':sum(r['tests_passed'] for r in rows),'native_checks':sum(r['native_tests_passed'] for r in rows),'all_passed':all(r['semantic_ok'] for r in rows)}
args.output.write_text(json.dumps(report,indent=2)+'\n');print('MODULE_TOTALS',json.dumps(report))
if not report['all_passed']:raise SystemExit(1)
