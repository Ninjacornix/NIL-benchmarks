//! Quota/read-order audit driver; executes the unmodified reference FileHost.
use nil_compiler::{
    SourceProfile, application::FileHost, compile_with_profile,
    evaluator::{Limits, Value, execute_values_with_host},
};
use nil_hir::FunctionId;
fn main() {
    let source = std::fs::read_to_string(std::env::args().nth(1).unwrap()).unwrap();
    let program = compile_with_profile(&source, SourceProfile::ExprV5).unwrap();
    match execute_values_with_host(
        &program.hir, FunctionId(0), &[], Limits::default(), &mut FileHost::default(),
    ) {
        Ok(Value::I64(value)) => println!("{value}"),
        Ok(other) => panic!("unexpected audit result: {other:?}"),
        Err(diagnostic) => {
            eprintln!("{diagnostic}");
            std::process::exit(1);
        }
    }
}
