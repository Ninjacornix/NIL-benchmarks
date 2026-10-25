//! Benchmark-only oracle: explicit FileHost, frozen scalar/text controls only.
use nil_compiler::{
    SourceProfile,
    application::FileHost,
    compile_with_plugins,
    evaluator::{Limits, Value, execute_values_with_host},
};
use nil_hir::{FunctionId, Type};
fn main() {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    let source = std::fs::read_to_string(&args[0]).expect("source");
    let program = compile_with_plugins(&source, SourceProfile::ExprV5, &[] as &[&str])
        .expect("frozen control must compile");
    let parameters = &program.hir.program().functions[0].parameters;
    assert_eq!(parameters.len(), args.len() - 1);
    nil_compiler::evaluator::reset_profile();
    let values = parameters
        .iter()
        .zip(&args[1..])
        .map(|(ty, arg)| match ty {
            Type::I64 => Value::I64(arg.parse().expect("integer control argument")),
            Type::Bytes => Value::Bytes(arg.as_bytes().to_vec().into()),
            _ => panic!("unsupported control parameter"),
        })
        .collect::<Vec<_>>();
    let result = execute_values_with_host(
        &program.hir,
        FunctionId(0),
        &values,
        Limits {
            steps: 1_000_000_000,
            call_depth: 256,
            memory_bytes: nil_hir::MAX_DYNAMIC_BYTES,
            defer_slot_writes: true,
        },
        &mut FileHost::default(),
    );
    match result {
        Ok(Value::I64(value)) => println!("{value}"),
        other => panic!("control failed: {other:?}"),
    }
    let (live, reservation) = nil_compiler::evaluator::measured_profile();
    eprintln!("NIL_REFERENCE_PROFILE live={live} reservation={reservation}");
}
