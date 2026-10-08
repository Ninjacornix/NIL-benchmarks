//! Measurement-only native builder. Sites are assigned before lowering/proofs.
fn main() {
    let args=std::env::args().skip(1).collect::<Vec<_>>();
    let source=std::fs::read_to_string(&args[0]).expect("source");
    let compiled=if std::env::var_os("NIL_COPY_FUZZ").is_some() {
        nil_fuzz::application::compile_case(&source)
    } else { nil_compiler::compile_with_plugins(&source,nil_compiler::SourceProfile::ExprV5,&args[3..]) };
    let mut program=match compiled {
        Ok(p)=>p,Err(d)=>{println!("ERR\t{:?}\t{}",d.phase,d);return;}
    };
    program.hir=measurement_program(&program.hir,&mut 0);
    let options=nil_llvm::Options {
        steps:100_000,call_depth:256,
        memory_bytes:if args[2]=="bounded" {nil_hir::MAX_DYNAMIC_BYTES as u64} else {nil_hir::DEFAULT_MEMORY_BYTES as u64},
        instrumentation:if args[2]=="bounded" {nil_llvm::Instrumentation::Bounded} else {assert_eq!(args[2],"unbounded");nil_llvm::Instrumentation::Unbounded},
        optimization:nil_llvm::Optimization::O0,
        ..nil_llvm::Options::default()
    };
    match nil_llvm::build(&program.hir,std::path::Path::new(&args[1]),options) {
        Ok(_)=>println!("BUILD\tOK"),Err(d)=>println!("ERR\tBackend\t{d}")
    }
}
