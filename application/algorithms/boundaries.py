"""Native O2 quota boundaries; full input+result reservation applies even on reuse."""
import argparse
import json
from pathlib import Path
import subprocess
from run import HERE, ROOT


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    out=args.output.resolve()
    if out.is_relative_to(ROOT):
        parser.error('Output must be outside source checkouts')
    out.mkdir(parents=True,exist_ok=True)
    records=[]
    for name,source,counts in [
        ('sort-bytes','1=#!sort(!bytes(a,0),0)\n',[33554392,33554393]),
        ('sort-buffer-limit','1=#!sort(!buffer(a,0),0)\n',[4194299,4194300]),
        ('sort-map',(HERE/'sort-map.nil').read_text(),[262144,262145]),
    ]:
        path=out/(name+'.nil');path.write_text(source)
        binary=out/name
        subprocess.run([str(ROOT/'target/release/nil'),'--profile','expr-v5','build',str(path),'-O2','-o',str(binary)],check=True)
        for index,count in enumerate(counts):
            result=subprocess.run([str(binary),str(count)],capture_output=True,timeout=60)
            assert result.returncode==(0 if index==0 else 1)
            assert result.stdout==(f'{1 if name=="sort-map" else count}\n'.encode() if index==0 else b'')
            assert result.stderr==(b'' if index==0 else result.stderr) and (index==0 or result.stderr.startswith(b'E013'))
            row={'workload':name,'count':count,'returncode':result.returncode,'stdout':result.stdout.decode(),'stderr':result.stderr.decode(),'source':source}
            records.append(row);print(json.dumps(row),flush=True)
    (out/'boundaries.json').write_text(json.dumps(records,indent=2)+'\n')


if __name__=='__main__':
    main()
