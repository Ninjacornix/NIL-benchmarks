//! Standalone audit helper: ordinary bounded execution of a callback back-edge.
use nil_compiler::{SourceProfile, compile_with_plugins, evaluator::{Limits, execute_values}, hir::FunctionId};
fn main() {
    let args = std::env::args().collect::<Vec<_>>();
    let source = std::fs::read_to_string(&args[1]).unwrap();
    let p = compile_with_plugins(&source, SourceProfile::ExprV5, &[&args[2]]).unwrap();
    println!("{:?}", execute_values(&p.hir, FunctionId(0), &[], Limits::default()));
}
