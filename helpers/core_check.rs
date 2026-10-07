//! Benchmark-only application oracle; the compiler and runtime are unchanged.
use nil_compiler::{
    SourceProfile,
    application::Host,
    compile_with_plugins,
    evaluator::{Limits, Value, execute_values_with_host},
};
use nil_hir::{Diagnostic, FunctionId, Phase};
use std::{env, fs};

struct MemoryHost {
    input: Vec<u8>,
    output: Option<Vec<u8>>,
    stdout: Vec<u8>,
}
impl Host for MemoryHost {
    fn read(&mut self, path: &[u8]) -> Result<Vec<u8>, Diagnostic> {
        if path == b"input.bin" {
            Ok(self.input.clone())
        } else {
            Err(Diagnostic::new(
                "E015",
                Phase::Execute,
                None,
                "fixture read denied",
            ))
        }
    }
    fn write(&mut self, path: &[u8], bytes: &[u8]) -> Result<(), Diagnostic> {
        if path != b"output.bin" {
            return Err(Diagnostic::new(
                "E015",
                Phase::Execute,
                None,
                "fixture write denied",
            ));
        }
        self.output = Some(bytes.to_vec());
        Ok(())
    }
    fn out(&mut self, bytes: &[u8]) -> Result<(), Diagnostic> {
        self.stdout.extend_from_slice(bytes);
        Ok(())
    }
}
fn main() {
    let args = env::args().skip(1).collect::<Vec<_>>();
    let source = fs::read_to_string(&args[0]).expect("source");
    let program = match compile_with_plugins(&source, SourceProfile::ExprV5, &[] as &[&str]) {
        Ok(p) => p,
        Err(d) => {
            println!("ERR\t{:?}\t{}", d.phase, d);
            return;
        }
    };
    if args[1] == "build-O0" || args[1] == "build-O2" || args[1] == "perf-O2" {
        let options = nil_llvm::Options {
            steps: 1_000_000_000,
            call_depth: 256,
            instrumentation: if args[1] == "perf-O2" {
                nil_llvm::Instrumentation::Unbounded
            } else {
                nil_llvm::Instrumentation::Bounded
            },
            optimization: if args[1] == "build-O0" {
                nil_llvm::Optimization::O0
            } else {
                nil_llvm::Optimization::O2
            },
            ..nil_llvm::Options::default()
        };
        match nil_llvm::build(&program.hir, std::path::Path::new(&args[2]), options) {
            Ok(_) => println!("BUILD\tOK"),
            Err(d) => println!("ERR\tBackend\t{d}"),
        }
        return;
    }
    let mut host = MemoryHost {
        input: fs::read(&args[1]).expect("fixture"),
        output: None,
        stdout: Vec::new(),
    };
    let parameters = [
        Value::Bytes(b"input.bin".to_vec().into()),
        Value::Bytes(b"output.bin".to_vec().into()),
    ];
    match execute_values_with_host(
        &program.hir,
        FunctionId(0),
        &parameters,
        Limits {
            steps: 1_000_000_000,
            call_depth: 256,
        },
        &mut host,
    ) {
        Ok(Value::I64(value)) => {
            if let Some(output) = host.output {
                fs::write(&args[2], output).expect("reference output");
            }
            fs::write(&args[3], &host.stdout).expect("reference stdout");
            println!("VALUE\t{value}");
        }
        Ok(_) => println!("ERR\tTypeCheck\twrong entry result"),
        Err(d) => println!("ERR\tExecute\t{}", d),
    }
}
