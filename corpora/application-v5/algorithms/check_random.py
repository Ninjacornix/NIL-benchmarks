"""Supplement frozen fixtures; never changes tasks/goldens or density selection."""
import argparse
import json
from pathlib import Path
import random
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import verify
from external_suite import load_tasks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=30030)
    parser.add_argument('--cases', type=int, default=30)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    verify.application.prepare()
    verify.application.expected = verify.expected
    totals = dict(reference=0, native=0, python=0, cpp=0)
    with tempfile.TemporaryDirectory(prefix='nil-algorithm-random-') as tmp:
        for frozen in load_tasks('external'):
            task_id = frozen['id']
            if not task_id.startswith('ex_algo_'):
                continue
            inputs = []
            for _ in range(args.cases):
                n = rng.randrange(0, 32)
                if task_id.endswith('linked_list'):
                    order = list(range(1, n)); rng.shuffle(order)
                    order = [0] + order if n else []
                    successors = {a:b for a,b in zip(order,order[1:])}
                    text = '\n'.join(f'{rng.randrange(-100,100)},{successors.get(i,-1)}' for i in range(n))
                elif task_id.endswith('bst_walk'):
                    text = ','.join(str(rng.randrange(-10,11)) for _ in range(n))
                elif task_id.endswith('graph_bfs'):
                    rows = [[rng.randrange(n) for _ in range(rng.randrange(0,n+1))] for _ in range(n)]
                    text = '\n'.join(','.join(map(str,[len(row)]+row)) for row in rows)
                else:
                    pairs = [sorted([rng.randrange(-30,31),rng.randrange(-30,31)]) for _ in range(n)]
                    text = '\n'.join(f'{a},{b}' for a,b in pairs)
                inputs.append(text.encode().hex())
            task = frozen | {'inputs':inputs}
            folder = Path(tmp)/task_id; folder.mkdir()
            for language, extension in [('expr-v5','nil'),('python','py'),('cpp','cpp')]:
                path = verify.HERE/'programs'/f'{task_id}.{extension}'
                result = verify.application.evaluate(path.read_text(),language,task,folder) if language == 'expr-v5' else verify.baseline(task,path,folder,language)
                if not result['semantic_ok']:
                    raise RuntimeError((task_id,language,result))
                if language == 'expr-v5':
                    totals['reference'] += result['tests_passed']; totals['native'] += result['native_tests_passed']
                else:
                    totals[language] += result['tests_passed']
                print(task_id,language,'PASS',result,flush=True)
    report = dict(seed=args.seed,cases_per_task=args.cases,totals=totals)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print('TOTALS '+json.dumps(report),flush=True)


if __name__ == '__main__':
    main()
