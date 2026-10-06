"""Check candidates against core, retaining diagnostic/quota counterexamples."""
import argparse,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
if out.is_relative_to(ROOT):p.error('results must stay outside checkout')
out.mkdir(parents=True,exist_ok=True)
compiler=ROOT/'target/release/nil'
parse=re.sub(r'\b([a-e])(?=\()',lambda m:chr(ord(m[1])+1),(HERE/'parse_candidate.nil').read_text())
find=(HERE/'find_candidate.nil').read_text();has=(HERE/'has_candidate.nil').read_text()
rows=[]
def compare(name,core,candidate):
 for opt in ['-O0','-O2']:
  values=[]
  for kind,source in [('core',core),('candidate',candidate)]:
   src=out/(name+'-'+kind+'.nil');src.write_text(source+'\n');binary=out/(name+'-'+kind+opt)
   subprocess.run([str(compiler),'--profile','expr-v5','build',str(src),'-o',str(binary),opt],check=True,capture_output=True)
   r=subprocess.run([str(binary)],capture_output=True);code=re.match(rb'E\d+',r.stderr)
   values.append(dict(kind=kind,status=r.returncode,stdout=r.stdout.decode('utf8','replace'),code=code[0].decode() if code else 'OK',stderr=r.stderr.decode('utf8','replace')))
  rows.append(dict(name=name,opt=opt,values=values,equivalent_codes_and_output=values[0]['code']==values[1]['code'] and values[0]['stdout']==values[1]['stdout']))
for text in ['0','12345','-6789','9223372036854775807','-9223372036854775808','-0','01','9223372036854775808','invalid','']:
 arg=json.dumps(text);compare('parse-'+str(len(rows)), '=!parse('+arg+')','=b('+arg+')\n'+parse)
compare('find-valid','=!find("abc",98,0)','=b("abc",98,0)\n'+find)
compare('find-trap-order','=!find("abc",256,-1)','=b("abc",256,-1)\n'+find)
compare('find-quota','=b(!bytes(67108824,0))\n(s)=!find(a,0,0)+#a','=b(!bytes(67108824,0))\n(s)=c(a,0,0)+#a\n'+find)
compare('has-valid',':b=!has(!insert(!map(),"x",1),"x")',':b=b(!insert(!map(),"x",1),"x")\n'+has)
# A live large value and live needle leave less than one copied key of headroom.
base='=b(!insert(!map(),!bytes(512,120),1))\n(m)=c(a,!bytes(67107408,0),!bytes(512,120))\n(m,s,s)='
compare('has-quota',base+'(!has(a,c)?1:0)+#b',base+'(d(a,c)?1:0)+#b\n'+has)
result=dict(rows=rows,migration_verdict={'find':'retained: valid search can acquire new E013 from zero-byte guard allocation','has':'retained: copying keys introduces E013 and linear search versus borrowed hashing','parse':'retained: source candidate still relies on core parse to raise E016, not a complete migration'},scope='Native O0/O2 prototype checks; Rust core/std tests and full differential campaigns separately cover the shipped compiler')
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
