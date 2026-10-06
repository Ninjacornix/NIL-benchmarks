"""Preregistered source std controls; keep every result including failed migrations."""
import argparse,hashlib,json,re,statistics,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--repeats',type=int,default=25);a=p.parse_args()
if a.repeats<25:p.error('at least 25 repeats')
out=a.output.resolve()
if out.is_relative_to(ROOT):p.error('results must stay outside checkout')
out.mkdir(parents=True,exist_ok=True)
subprocess.run(['cargo','build','--release','--locked','--offline','-p','nil'],cwd=ROOT,check=True)
compiler=ROOT/'target/release/nil'
data=(b'alpha,beta,gamma\n'*(16*1024*1024//16+1))[:16*1024*1024];file=out/'input.bin';file.write_bytes(data)
root='(s)='
hand_map='@(a,!bytes(#a,0),0;c<#a;a,b[c:255-a[c]],c+1;b)'
hand_filter='@(a,"",0;c<#a;a,a[c]==10?!concat(b,!bytes(1,a[c])):b,c+1;b)'
hand_fold='@(a,0,0;b<#a;a,b+1,c+a[b];c)'
programs={
 'map_direct':root+'b(!read(a))\n(s):s='+hand_map,
 'map_std':root+'!map(&b,!read(a))\n1=255-a',
 'map_module':root+'!7.0(&b,!read(a))\n1=255-a',
 'filter_direct':root+'b(!read(a))\n(s):s='+hand_filter,
 'filter_std':root+'!filter(&b,!read(a))\n1:b=a==10',
 'fold_direct':root+'b(!read(a))\n(s)='+hand_fold,
 'fold_std':root+'!fold(&b,!read(a),0)\n2=a+b',
 'find_core':root+'!find(!read(a),255,0)',
 'find_candidate':root+'b(!read(a),255,0)\n'+(HERE/'find_candidate.nil').read_text(),
 'has_core':'(s)=@( !insert(!map(),"k",1),0,0;b<100000;a,b+1,c+(!has(a,b/2*2==b?"k":"j")?1:0);c)',
 'has_candidate':'(s)=@( !insert(!map(),"k",1),0,0;b<100000;a,b+1,c+(b(a,b/2*2==b?"k":"j")?1:0);c)\n'+(HERE/'has_candidate.nil').read_text(),
 'parse_core':'(s)=@(0,0;a<100000;a+1,b+!parse(a/2*2==a?"12345":"-6789");b)',
 'parse_candidate':'(s)=@(0,0;a<100000;a+1,b+b(a/2*2==a?"12345":"-6789");b)\n'+re.sub(r'\b([a-e])(?=\()',lambda m:chr(ord(m[1])+1),(HERE/'parse_candidate.nil').read_text()),
}
programs.update({
 'scan_inline':(ROOT/'benchmarks/hof-study/performance/inline.nil').read_text().strip(),
 'scan_hof_local':(ROOT/'benchmarks/hof-study/performance/map.nil').read_text().strip(),
 'scan_hof_module':root+'!9.0(&b,!read(a))\n1=a==10?1:0',
})
# Source callbacks returning bytes use a bytes entry for valid CLI wrapping.
for name in ['map_direct','map_std','map_module','filter_direct','filter_std']:
 programs[name]=programs[name].replace('(s)=','(s):s=',1)
module=out/'std.nil-module';module.write_text('nil-module 1\nid 7\nsource std.nil\nexport 0 0\n')
(out/'std.nil').write_text('([i:i],s):s=!map(^a,b)\n')
scan_module=out/'scan.nil-module';scan_module.write_text('nil-module 1\nid 9\nsource scan.nil\nexport 0 0\n')
(out/'scan.nil').write_text('([i:i],s)=@(b,0,0;b<#a;a,b+1,c+^a(a[b]);c)\n')
# A separate provider ID, with mirrored comparisons and increment: no identity privilege.
(out/'eq.nil').write_text('(s,s):b=#b==#a?@(a,b,0,true;c<#a?d:false;a,b,1+c,b[c]==a[c];d):false\n')
eq=out/'eq.nil-plugin';eq.write_text('nil-plugin 1\nid 8\nsource eq.nil\neffect borrow\nexport 0 0\n')
programs['equal_mirrored']=root+':b=!8.0(!read(a),!read(a))' # normalize signature below
programs['equal_mirrored']='(s):b=!8.0(b(!read(a)),b(!read(a)))\n(s):s=a'
expected={n: (bytes(255-v for v in data)+b'\n' if n.startswith('map_') else bytes(v for v in data if v==10)+b'\n' if n.startswith('filter_') else f'{sum(data)}\n'.encode() if n.startswith('fold_') else f'{len(data)}\n'.encode() if n.startswith('find_') else b'50000\n' if n.startswith('has_') else b'277800000\n' if n.startswith('parse_') else f'{data.count(10)}\n'.encode() if n.startswith('scan_') else b'true\n') for n in programs}
binaries={};proofs={}
for name,source in programs.items():
 src=out/(name+'.nil');src.write_text(source+'\n');binary=out/name
 flags=['--module',str(scan_module)] if name=='scan_hof_module' else ['--module',str(module)] if name=='map_module' else ['--plugin',str(eq)] if name=='equal_mirrored' else []
 cmd=[str(compiler),'--profile','expr-v5',*flags,'build',str(src),'-o',str(binary),'-O2']
 subprocess.run(cmd,check=True,capture_output=True);binaries[name]=binary
 ir=subprocess.check_output([str(compiler),'--profile','expr-v5',*flags,'llvm',str(src)],text=True);(out/(name+'.ll')).write_text(ir)
 asm=subprocess.check_output(['otool','-tvV',str(binary)],text=True);(out/(name+'.asm')).write_text(asm)
 entry=asm.split('_nil_entry:',1)[-1].split('\n_',1)[0]
 proofs[name]={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'ir_sha256':hashlib.sha256(ir.encode()).hexdigest(),'vector_compare': 'cmeq.16b' in entry,'vector_load':'ldp\tq' in entry,'bulk_compare_call':'call i1 @nil_bulk_compare' in ir}
rows=[]
# Rotate paired controls; big-output verification outside the timed subprocess.
for names in [('map_direct','map_std','map_module'),('filter_direct','filter_std'),('fold_direct','fold_std'),('find_core','find_candidate'),('has_core','has_candidate'),('parse_core','parse_candidate'),('equal_mirrored',),('scan_inline','scan_hof_local','scan_hof_module')]:
 samples={n:[] for n in names}
 for repeat in range(a.repeats+1):
  for name in names[repeat%len(names):]+names[:repeat%len(names)]:
   start=time.perf_counter_ns();r=subprocess.run([str(binaries[name]),str(file)],capture_output=True);elapsed=time.perf_counter_ns()-start
   assert r.returncode==0 and not r.stderr and r.stdout==expected[name],(name,r.returncode,r.stderr,r.stdout[:40],expected[name][:40])
   if repeat:samples[name].append(elapsed)
 for name in names:rows.append(dict(name=name,min_ns=min(samples[name]),median_ns=statistics.median(samples[name]),max_ns=max(samples[name]),samples_ns=samples[name]))
result=dict(repeats=a.repeats,warmups=1,rows=rows,proofs=proofs,input_bytes=len(data),input_sha256=hashlib.sha256(data).hexdigest(),method='Warm rotating whole-process wall times, output verified every execution; no CPU isolation',compiler=str(compiler),clang=subprocess.check_output(['clang','--version'],text=True))
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
