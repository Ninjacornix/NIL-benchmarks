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
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
 if out.is_relative_to(ROOT):p.error('overlay must be outside the checkout')
 out.mkdir(parents=True,exist_ok=True);shadow=out/'source';shadow.mkdir(exist_ok=True)
 if any(shadow.iterdir()):p.error('use a fresh output folder')
 revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 process=subprocess.Popen(['git','archive',revision],cwd=ROOT,stdout=subprocess.PIPE)
 with tarfile.open(fileobj=process.stdout,mode='r|') as archive:archive.extractall(shadow,filter='data')
 assert process.wait()==0
 changes={}
 path=shadow/'crates/nil-compiler/src/evaluator.rs';source=path.read_text();original=hashlib.sha256(source.encode()).hexdigest()
 anchor='        allocated = live;';assert source.count(anchor)==1
 source=PREFIX+source.replace(anchor,'        PROFILE_LIVE.with(|p| p.set(p.get().max(live)));\n'+anchor)
 path.write_text(source);changes[str(path.relative_to(shadow))]=dict(original_sha256=original,instrumented_sha256=hashlib.sha256(source.encode()).hexdigest())
 path=shadow/'crates/nil-compiler/src/application.rs';source=path.read_text();original=hashlib.sha256(source.encode()).hexdigest()
 anchor='    Ok(())\n}\npub(crate) fn intrinsic(';assert source.count(anchor)==1
 source=source.replace(anchor,'    crate::evaluator::observe_profile_charge(*used);\n'+anchor)
 path.write_text(source);changes[str(path.relative_to(shadow))]=dict(original_sha256=original,instrumented_sha256=hashlib.sha256(source.encode()).hexdigest())
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
 helper_dir=out/'helper';helper_dir.mkdir();(helper_dir/'main.rs').write_text(helper)
 manifest='[package]\nname="nil-generalize-reference-profile"\nversion="0.0.0"\nedition="2024"\n[workspace]\n[dependencies]\n'
 for name in ['nil-compiler','nil-hir','nil-llvm']:manifest+=name+'={path='+json.dumps(str(shadow/'crates'/name))+'}\n'
 manifest+='[[bin]]\nname="reference-profile"\npath="main.rs"\n';
 manifest+='[[bin]]\nname="reference-controls"\npath='+json.dumps(str(HERE/'reference_controls.rs'))+'\n';(helper_dir/'Cargo.toml').write_text(manifest)
 subprocess.run(['cargo','generate-lockfile','--manifest-path',str(helper_dir/'Cargo.toml'),'--offline'],check=True)
 subprocess.run(['cargo','build','--manifest-path',str(helper_dir/'Cargo.toml'),'--release','--locked','--offline'],check=True)
 receipt=dict(schema=1,compiler_revision=revision,method=__doc__,patches=changes,helper_sha256=hashlib.sha256(helper.encode()).hexdigest(),controls_helper_sha256=hashlib.sha256((HERE/"reference_controls.rs").read_bytes()).hexdigest(),binary=str(helper_dir/'target/release/reference-profile'))
 (out/'MANIFEST.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
