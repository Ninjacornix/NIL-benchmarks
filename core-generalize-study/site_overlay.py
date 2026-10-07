"""Measurement-only HIR site labels, preserved through cloned/inlined bodies.

Labels do not replace source spans. Native physical-copy joins are incomplete
until every storage path and aggregate lowering has a coverage receipt.
"""
import hashlib,re

def patch(shadow):
 changes={}
 def edit(name, transform):
  path=shadow/name;old=path.read_text();new=transform(old);assert new!=old,name;path.write_text(new)
  changes[name]={'original_sha256':hashlib.sha256(old.encode()).hexdigest(),'instrumented_sha256':hashlib.sha256(new.encode()).hexdigest()}
 edit('crates/nil-hir/src/lib.rs', lambda s:s.replace('pub struct Instruction {\n','pub struct Instruction {\n    pub measurement_site: u64,\n',1))
 for name in ['crates/nil-compiler/src/lower.rs','crates/nil-hir/src/liveness.rs','crates/nil-llvm/src/loop_storage.rs','crates/nil-llvm/src/bulk_compare.rs','plugins/sequence/provider.rs']:
  def constructors(s):
   def insert(m):
    prefix=s[s.rfind('\n',0,m.start())+1:m.start()]
    return m[0] if '->' in prefix else 'Instruction {\n            measurement_site: 0,\n'
   return re.sub(r'(?<!struct )Instruction \{\n',insert,s)
  edit(name,constructors)
 edit('crates/nil-llvm/src/emit.rs',lambda s:s.replace('            let span = instruction.span;\n            self.tick(span);','            let span = instruction.span;\n            self.tick(span);\n            self.line(format!("call void @nil_measure_site(i64 {})", instruction.measurement_site));',1).replace('        out.push_str(APPLICATION_HELPERS);','        out.push_str(APPLICATION_HELPERS);\n        out.push_str("declare void @nil_measure_site(i64)\\n");',1))
 return changes
ANNOTATE='''
fn measurement_program(program: &nil_hir::ValidatedProgram, next: &mut u64) -> nil_hir::ValidatedProgram {
    fn instructions(list: &mut [nil_hir::Instruction], next: &mut u64) {
        for instruction in list {
            *next+=1; instruction.measurement_site=*next;
            match &mut instruction.operation {
                nil_hir::Operation::If {then_region,else_region,..} => {
                    instructions(&mut then_region.instructions,next);
                    instructions(&mut else_region.instructions,next);
                }
                nil_hir::Operation::Loop {condition,body,finish,..} => {
                    for region in [condition,body,finish] {instructions(&mut region.instructions,next);}
                }
                nil_hir::Operation::PluginCall {provider,..} => {
                    let annotated=measurement_program(provider.program(),next);
                    **provider=nil_hir::plugin::Provider::new(provider.id,provider.operation,annotated,provider.entry()).expect("measurement must retain provider proofs");
                }
                _=>{}
            }
        }
    }
    let mut raw=program.program().clone();
    for function in &mut raw.functions {instructions(&mut function.instructions,next);}
    nil_hir::validate(raw).expect("measurement must retain HIR invariants")
}
'''
