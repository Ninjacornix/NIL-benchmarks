//! Direct reference boundary check; compile against the existing release crates.
use nil_compiler::{SourceProfile, compile_with_profile, evaluator::{Limits, Value, execute_values}};
fn main() {
    let source = std::fs::read_to_string(std::env::args().nth(1).expect("source path")).unwrap();
    let program = compile_with_profile(&source,SourceProfile::ExprV5).unwrap();
    for count in [262144,262145,262146] {
        let result = execute_values(&program.hir,nil_compiler::hir::FunctionId(0),&[Value::I64(count)],Limits{steps:100_000_000,..Default::default()});
        match result {
            Ok(Value::I64(value)) => { assert_eq!(value,count);println!("{count}: OK {value}"); }
            Err(error) => { assert_eq!(count,262146);assert_eq!(error.code,"E013");println!("{count}: {error}"); }
            other => panic!("unexpected result: {other:?}"),
        }
    }
}
