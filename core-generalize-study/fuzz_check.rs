//! Census-only oracle: the generated (v,s,s,s) entry receives its actual types.
//! The fixture is deliberately fixed and is not the fuzz campaign's random Host.
use nil_compiler::{application::{Host, next_random}, evaluator::{Limits, Value, execute_values_with_host}};
use nil_hir::{Diagnostic, FunctionId, Phase};
use std::{collections::BTreeMap, env, fs};

fn fault(code: &'static str) -> Diagnostic {
    Diagnostic::new(code, Phase::Execute, None, "census fixture host failure")
}
struct CensusHost {
    stdout: Vec<u8>,
    denied: bool,
    state: u64,
    invalid_seed: bool,
}
impl CensusHost {
    fn permitted(&self) -> Result<(), Diagnostic> {
        if self.denied { Err(fault("E018")) } else { Ok(()) }
    }
}
impl Host for CensusHost {
    fn read(&mut self, path: &[u8]) -> Result<Vec<u8>, Diagnostic> {
        self.permitted()?;
        if path == b"input.bin" { fs::read("input.bin").map_err(|_| fault("E015")) }
        else { Err(fault("E015")) }
    }
    fn write(&mut self, path: &[u8], bytes: &[u8]) -> Result<(), Diagnostic> {
        self.permitted()?;
        if path == b"output.bin" { fs::write("output.bin", bytes).map_err(|_| fault("E015")) }
        else { Err(fault("E015")) }
    }
    fn out(&mut self, bytes: &[u8]) -> Result<(), Diagnostic> {
        self.permitted()?; self.stdout.extend_from_slice(bytes); Ok(())
    }
    fn random(&mut self) -> Result<u64, Diagnostic> {
        self.permitted()?;
        if self.invalid_seed { Err(fault("E016")) } else { Ok(next_random(&mut self.state)) }
    }
    fn env(&mut self, name: &[u8]) -> Result<Vec<u8>, Diagnostic> {
        self.permitted()?;
        let values = BTreeMap::from([
            (b"NIL_FUZZ_PRESENT".as_slice(), b"abc 12".to_vec()),
            (b"NIL_FUZZ_EMPTY".as_slice(), vec![]),
            (b"NIL_FUZZ_RAW".as_slice(), vec![255,128,b'x']),
            (b"NIL_FUZZ_LARGE".as_slice(), vec![b'x';1024]),
        ]);
        Ok(values.get(name).cloned().unwrap_or_default())
    }
    fn directory(&mut self, path: &[u8]) -> Result<Vec<Vec<u8>>, Diagnostic> {
        self.permitted()?;
        let count = match path {
            b"input.bin.entries" => 16,
            b"input.bin.large" => 1024,
            b"input.bin.empty" => 0,
            _ => return Err(fault("E015")),
        };
        let mut names = (0..count).rev().map(|i| format!("entry-{i:04}-é").into_bytes()).collect::<Vec<_>>();
        if count == 16 { names.push(b"subdirectory".to_vec()); }
        Ok(names)
    }
}
fn render(value: &Value) -> Vec<u8> {
    match value {
        Value::Record(..) | Value::RecordBuffer(..) => panic!("unsupported census entry result"),
        Value::Map(v) => format!("{}\n", v.render()).into_bytes(),
        Value::I64(v) => format!("{v}\n").into_bytes(),
        Value::U64(_) | Value::U128(_) | Value::F64(_) => format!("{}\n", nil_compiler::numeric::format(value)).into_bytes(),
        Value::Bool(v) => format!("{v}\n").into_bytes(),
        Value::Bytes(v) => [v.as_ref(), b"\n"].concat(),
        Value::Buffer(v) => format!("[{}]\n", v.iter().map(i64::to_string).collect::<Vec<_>>().join(",")).into_bytes(),
        Value::Array(v) => format!("[{}]\n", v.iter().map(i64::to_string).collect::<Vec<_>>().join(",")).into_bytes(),
    }
}
fn oracle_main() {
    let args = env::args().skip(1).collect::<Vec<_>>();
    let source = fs::read_to_string(&args[0]).expect("source");
    let program = nil_fuzz::application::compile_case(&source).expect("generated source must compile");
    // MEASUREMENT: annotate the same HIR only in the isolated instrumented helper.
    let parameters = [
        Value::Buffer(vec![3,-2,9].into()), Value::Bytes(b"abc 12".to_vec().into()),
        Value::Bytes(b"input.bin".to_vec().into()), Value::Bytes(b"output.bin".to_vec().into()),
    ];
    let mut host = CensusHost { stdout: vec![], denied: env::var_os("NIL_DENY_HOST_IO").is_some(),
        state: env::var("NIL_CENSUS_SEED").expect("fixture seed").parse().expect("seed"),
        invalid_seed: env::var_os("NIL_CENSUS_INVALID_SEED").is_some() };
    let result = execute_values_with_host(&program.hir, FunctionId(0), &parameters,
        Limits { steps: 100_000, call_depth: 256, memory_bytes: nil_hir::MAX_DYNAMIC_BYTES }, &mut host);
    let code = match result {
        Ok(value) => { host.stdout.extend(render(&value)); "OK" }
        Err(ref d) => { eprintln!("{d}"); d.code }
    };
    fs::write(&args[3], host.stdout).expect("observable stdout");
    println!("RESULT\t{code}");
}
fn main() { oracle_main(); }
