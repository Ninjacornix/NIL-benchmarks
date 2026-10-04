"""Candidate type-layout probes; explicitly NOT full corpus task solutions."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'corpora/application-v5'))
import verify


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    answers={'dot':b'116','camicia':b'5','forth':b'1','alphametics':b'10'}
    verify.application.prepare()
    verify.application.expected=lambda task,data:answers[task]
    rows=[]
    with tempfile.TemporaryDirectory(prefix='nil-layout-probe-') as tmp:
        for name in answers:
            folder=Path(tmp)/name;folder.mkdir()
            verdict=verify.application.evaluate((HERE/'probes'/(name+'.nil')).read_text(),'expr-v5',{'id':name,'inputs':['']},folder)
            assert verdict['semantic_ok'],(name,verdict)
            rows.append({'candidate':name,**verdict})
            print(name,'layout only PASS',verdict,flush=True)
    args.output.write_text(json.dumps({'scope':'Type/storage feasibility only, not complete task adapters; unsupported statuses unchanged.','results':rows},indent=2)+'\n')


if __name__=='__main__':
    main()
