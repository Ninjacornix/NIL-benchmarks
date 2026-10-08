"""Build an isolated, measurement-only reference evaluator overlay outside git.

Heap liveness comes from the evaluator's existing liveness traversal. Prospective
quota reservations are separately sampled after successful charge checks. No
compiler checkout file or semantic operation is changed.
"""
import argparse,hashlib,json,subprocess,tarfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;SUITE=HERE.parent;ROOT=SUITE.parent
PREFIX='''thread_local! {
    static PROFILE_LIVE: std::cell::Cell<usize> = const { std::cell::Cell::new(0) };
    static PROFILE_RESERVATION: std::cell::Cell<usize> = const { std::cell::Cell::new(0) };
}
pub fn reset_profile() {
    PROFILE_LIVE.with(|p| p.set(0));
    PROFILE_RESERVATION.with(|p| p.set(0));
}
pub fn measured_profile() -> (usize, usize) {
    (PROFILE_LIVE.with(|p| p.get()), PROFILE_RESERVATION.with(|p| p.get()))
}
pub(crate) fn observe_profile_charge(bytes: usize) {
    PROFILE_RESERVATION.with(|p| p.set(p.get().max(bytes)));
}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--copies',action='store_true');p.add_argument('--working-tree',action='store_true');p.add_argument('--revision',default='HEAD');a=p.parse_args();out=a.output.resolve()
 if out.is_relative_to(ROOT):p.error('overlay must be outside the checkout')
 out.mkdir(parents=True,exist_ok=True);shadow=out/'source';shadow.mkdir(exist_ok=True)
 if any(shadow.iterdir()):p.error('use a fresh output folder')
 revision=subprocess.check_output(['git','rev-parse',a.revision],cwd=ROOT,text=True).strip()
 process=subprocess.Popen(['git','archive',revision],cwd=ROOT,stdout=subprocess.PIPE)
 with tarfile.open(fileobj=process.stdout,mode='r|') as archive:archive.extractall(shadow,filter='data')
 assert process.wait()==0
 working_patch=None
 if a.working_tree:
  patch=subprocess.check_output(['git','diff','--binary',revision,'--','crates','cli','tools','std','Cargo.toml','Cargo.lock'],cwd=ROOT)
  subprocess.run(['git','apply','--unsafe-paths','-'],input=patch,cwd=shadow,check=True)
  working_patch=hashlib.sha256(patch).hexdigest()
 changes={}
 path=shadow/'crates/nil-compiler/src/evaluator.rs';source=path.read_text();original=hashlib.sha256(source.encode()).hexdigest()
 anchor='        allocated.bytes = live;' if 'Memory::new' in source else '        allocated = live;';assert source.count(anchor)==1
 source=PREFIX+source.replace(anchor,'        PROFILE_LIVE.with(|p| p.set(p.get().max(live)));\n'+anchor)
 path.write_text(source);changes[str(path.relative_to(shadow))]=dict(original_sha256=original,instrumented_sha256=hashlib.sha256(source.encode()).hexdigest())
 path=shadow/'crates/nil-compiler/src/application.rs';source=path.read_text();original=hashlib.sha256(source.encode()).hexdigest()
 anchor='    Ok(())\n}\npub(crate) fn intrinsic(';assert source.count(anchor)==1
 source=source.replace(anchor,'    crate::evaluator::observe_profile_charge('+('used.bytes' if 'pub(crate) struct Memory' in source else '*used')+');\n'+anchor)
 path.write_text(source);changes[str(path.relative_to(shadow))]=dict(original_sha256=original,instrumented_sha256=hashlib.sha256(source.encode()).hexdigest())
 if a.copies:
  import copy_overlay,site_overlay,native_copy_overlay
  changes.update(site_overlay.patch(shadow))
  changes.update(native_copy_overlay.patch(shadow))
  for name,receipt in copy_overlay.patch(shadow).items():
   if name in changes:
    receipt['liveness_overlay_sha256']=receipt['original_sha256']
    receipt['original_sha256']=changes[name]['original_sha256']
   changes[name]=receipt
 helper=(SUITE/'helpers/core_check.rs').read_text();helper=helper.replace('fn main() {','fn main() {\n    nil_compiler::evaluator::reset_profile();',1)
 # One expression owns the evaluator call; main returns normally on all existing
 # paths. Print separately on stderr so existing oracle stdout stays byte-exact.
 helper=helper.replace('fn main() {','fn oracle_main() {',1)
 helper+='''\nfn main() {
    oracle_main();
    let (live, reservation) = nil_compiler::evaluator::measured_profile();
    eprintln!("NIL_REFERENCE_PROFILE live={} reservation={}", live, reservation);
}
'''
 if a.copies:
  helper=helper.replace('    let program = match compile_with_plugins', '    let mut program = match compile_with_plugins')
  helper=helper.replace('    if args[1] == "build-O0"', '    program.hir=measurement_program(&program.hir, &mut 0);\n    if args[1] == "build-O0"',1)
  helper=helper.replace('args[1] == "build-O2" ||', 'args[1] == "build-O2" || args[1] == "perf-O0" ||')
  helper=helper.replace('if args[1] == "perf-O2" {', 'if args[1] == "perf-O2" || args[1] == "perf-O0" {')
  helper=helper.replace('if args[1] == "build-O0" {', 'if args[1] == "build-O0" || args[1] == "perf-O0" {')
  helper+=site_overlay.ANNOTATE
  helper=helper.replace('    oracle_main();', '    nil_compiler::copy_trace::reset();\n    oracle_main();\n    if let Some(path)=std::env::var_os("NIL_COPY_TRACE_FILE") { nil_compiler::copy_trace::finish(std::path::Path::new(&path)); }')
 helper_dir=out/'helper';helper_dir.mkdir();(helper_dir/'main.rs').write_text(helper)
 extra_helpers={}
 if a.copies:
  app=(SUITE/'helpers/application_check.rs').read_text()
  app=app.replace('fn main() {','fn oracle_main() {',1)
  app=app.replace('    let program = match compile_with_plugins','    let mut program = match compile_with_plugins',1)
  app=app.replace('    let mut host = MemoryHost {','    program.hir=measurement_program(&program.hir, &mut 0);\n    let mut host = MemoryHost {',1)
  app+=site_overlay.ANNOTATE
  app+='\nfn main() {\n    nil_compiler::copy_trace::reset();\n    oracle_main();\n    if let Some(path)=std::env::var_os("NIL_COPY_TRACE_FILE") { nil_compiler::copy_trace::finish(std::path::Path::new(&path)); }\n}\n'
  extra_helpers['reference-application']=app
  extra_helpers['native-copy-build']=(HERE/'native_copy_build.rs').read_text()+site_overlay.ANNOTATE
  extra_helpers['fuzz-sources']=(HERE/'fuzz_sources.rs').read_text()
  fuzz=(HERE/'fuzz_check.rs').read_text()
  fuzz=fuzz.replace('    let program = nil_fuzz::', '    let mut program = nil_fuzz::')
  fuzz=fuzz.replace('    // MEASUREMENT: annotate the same HIR only in the isolated instrumented helper.', '    program.hir = measurement_program(&program.hir, &mut 0);')
  fuzz=fuzz.replace('fn main() { oracle_main(); }','fn main() { nil_compiler::copy_trace::reset(); oracle_main(); if let Some(path)=std::env::var_os("NIL_COPY_TRACE_FILE") { nil_compiler::copy_trace::finish(std::path::Path::new(&path)); } }')
  extra_helpers['reference-fuzz']=fuzz+site_overlay.ANNOTATE
  for name,content in extra_helpers.items():(helper_dir/(name+'.rs')).write_text(content)

 manifest='[package]\nname="nil-generalize-reference-profile"\nversion="0.0.0"\nedition="2024"\n[workspace]\n[dependencies]\n'
 for name in ['nil-compiler','nil-hir','nil-llvm']:manifest+=name+'={path='+json.dumps(str(shadow/'crates'/name))+'}\n'
 if a.copies:manifest+='nil-fuzz={path='+json.dumps(str(shadow/'tools/nil-fuzz'))+'}\n'
 manifest+='[[bin]]\nname="reference-profile"\npath="main.rs"\n';
 
 for name in extra_helpers:manifest+='[[bin]]\nname='+json.dumps(name)+'\npath='+json.dumps(name+'.rs')+'\n'
 manifest+='[[bin]]\nname="reference-controls"\npath='+json.dumps(str(HERE/'reference_controls.rs'))+'\n';(helper_dir/'Cargo.toml').write_text(manifest)
 subprocess.run(['cargo','generate-lockfile','--manifest-path',str(helper_dir/'Cargo.toml'),'--offline'],check=True)
 subprocess.run(['cargo','build','--manifest-path',str(helper_dir/'Cargo.toml'),'--release','--locked','--offline'],check=True)
 if a.copies:
  ordinary=out/'ordinary-fuzz';ordinary.mkdir()
  (ordinary/'main.rs').write_text((HERE/'fuzz_check.rs').read_text())
  ordinary_manifest='[package]\nname="nil-census-fuzz-oracle"\nversion="0.0.0"\nedition="2024"\n[workspace]\n[dependencies]\n'
  for name,path in [('nil-compiler',ROOT/'crates/nil-compiler'),('nil-hir',ROOT/'crates/nil-hir'),('nil-fuzz',ROOT/'tools/nil-fuzz')]:ordinary_manifest+=name+'={path='+json.dumps(str(path))+'}\n'
  ordinary_manifest+='[[bin]]\nname="ordinary-fuzz"\npath="main.rs"\n'
  (ordinary/'Cargo.toml').write_text(ordinary_manifest)
  subprocess.run(['cargo','generate-lockfile','--manifest-path',str(ordinary/'Cargo.toml'),'--offline'],check=True)
  subprocess.run(['cargo','build','--manifest-path',str(ordinary/'Cargo.toml'),'--release','--locked','--offline'],check=True)
 receipt=dict(schema=1,compiler_revision=revision,working_tree_patch_sha256=working_patch,method=__doc__,patches=changes,helper_sha256=hashlib.sha256(helper.encode()).hexdigest(),controls_helper_sha256=hashlib.sha256((HERE/"reference_controls.rs").read_bytes()).hexdigest(),extra_helpers={name:hashlib.sha256(content.encode()).hexdigest() for name,content in extra_helpers.items()},binary=str(helper_dir/'target/release/reference-profile'))
 (out/'MANIFEST.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
