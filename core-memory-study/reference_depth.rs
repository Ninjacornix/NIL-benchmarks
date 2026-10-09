//! Depth admission probe: use the unmodified compiler/evaluator/backend APIs.
use nil_compiler::{
    SourceProfile, compile_with_profile,
    evaluator::{Limits, Value, execute_values},
};
use nil_hir::FunctionId;
use nil_llvm::{Instrumentation, Optimization, Options};
fn main() {
    let args = std::env::args().collect::<Vec<_>>();
    let source = std::fs::read_to_string(&args[2]).unwrap();
    let p = compile_with_profile(&source, SourceProfile::ExprV5).unwrap();
    let depth = args[3].parse::<usize>().unwrap();
    if args[1] == "reference" {
        let values = args[4..]
            .iter()
            .map(|n| Value::I64(n.parse().unwrap()))
            .collect::<Vec<_>>();
        match execute_values(
            &p.hir,
            FunctionId(0),
            &values,
            Limits {
                steps: u64::MAX,
                call_depth: depth,
                memory_bytes: 0,
            },
        ) {
            Ok(Value::I64(n)) => println!("{n}"),
            Ok(v) => panic!("unexpected audit result: {v:?}"),
            Err(e) => {
                eprintln!("{e}");
                std::process::exit(1);
            }
        }
    } else {
        let options = Options {
            steps: u64::MAX,
            call_depth: depth as u64,
            memory_bytes: 0,
            instrumentation: if args[1] == "bounded" {
                Instrumentation::Bounded
            } else {
                Instrumentation::Unbounded
            },
            optimization: if args[5] == "O0" {
                Optimization::O0
            } else {
                Optimization::O2
            },
            ..Default::default()
        };
        if let Err(e) = nil_llvm::build(&p.hir, std::path::Path::new(&args[4]), options) {
            eprintln!("{e}");
            std::process::exit(1);
        }
    }
}
