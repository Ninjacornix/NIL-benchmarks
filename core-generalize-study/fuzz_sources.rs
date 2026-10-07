//! Measurement-only: dump every generated expr-v5 family source for one seed.
//! Sources come from the fuzzer's public case constructor with the campaign's own
//! per-case seed derivation, so the census covers exactly the generated programs.
//! Inputs are the census's own fixture, not the fuzz oracle's randomized host;
//! the report states that explicitly.
fn main() {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    let seed: u64 = args[0].parse().expect("seed");
    let out = std::path::PathBuf::from(&args[1]);
    std::fs::create_dir_all(&out).expect("output directory");
    let count = nil_fuzz::application::FAMILY_COUNT;
    let mut denied = 0usize;
    for index in 0..count {
        // Identical to application::smoke_campaign.
        let case_seed = seed.wrapping_add(index as u64);
        let case = nil_fuzz::application::Case::new(case_seed, index);
        if case.denied {
            denied += 1;
        }
        std::fs::write(
            out.join(format!("family-{index:04}.nil")),
            format!("{}\n", case.source),
        )
        .expect("write source");
    }
    println!("DUMPED\t{count}\tdenied\t{denied}");
}
