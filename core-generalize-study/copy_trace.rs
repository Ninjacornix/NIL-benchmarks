//! Measurement-only trace. Never linked into normal compiler binaries.
//! Storage addresses are private lookup keys; only monotonic versions are emitted.
use std::cell::RefCell;
use std::collections::BTreeMap;
#[derive(Clone, Debug)]
struct CopyEvent { clock: u64, version: u64, bytes: usize, kind: &'static str }
#[derive(Default)]
struct Trace {
    enabled: bool,
    active: bool,
    clock: u64,
    next_version: u64,
    storage: BTreeMap<usize, u64>,
    last_payload: BTreeMap<u64, u64>,
    last_metadata: BTreeMap<u64, u64>,
    copies: Vec<CopyEvent>,
    occurrences: BTreeMap<u64,u64>,
    sites: Vec<(u64,u64,u64,Vec<u64>)>,
}
thread_local! { static TRACE: RefCell<Trace> = RefCell::new(Trace::default()); }
impl Trace {
    fn version(&mut self, key: usize) -> u64 {
        if let Some(v) = self.storage.get(&key) { return *v; }
        self.next_version += 1;
        self.storage.insert(key, self.next_version);
        self.next_version
    }
}
pub fn reset() { TRACE.with(|t| *t.borrow_mut() = Trace { enabled: true, ..Trace::default() }); }
pub fn pause() { TRACE.with(|t| t.borrow_mut().active = false); }
pub fn tick() { TRACE.with(|t| { let mut t=t.borrow_mut(); t.clock+=1; t.active=t.enabled; }); }
pub fn begin(site: u64, keys: &[Option<usize>]) {
    TRACE.with(|t| { let mut t=t.borrow_mut(); t.clock+=1; t.active=t.enabled;
        if !t.enabled {return;}
        let clock=t.clock;
        let occurrence=t.occurrences.entry(site).or_default();*occurrence+=1;let occurrence=*occurrence;
        let versions=keys.iter().map(|key| key.map_or(0,|key| t.version(key))).collect();
        if !keys.is_empty() {t.sites.push((clock,site,occurrence,versions));}
    });
}
pub fn forget(key: usize) { TRACE.with(|t| { t.borrow_mut().storage.remove(&key); }); }
pub fn fresh(key: usize) { TRACE.with(|t| { let mut t=t.borrow_mut(); if !t.enabled {return;} t.storage.remove(&key); t.version(key); }); }
pub fn observe(key: usize, payload: bool) {
    TRACE.with(|t| { let mut t=t.borrow_mut(); if !t.active {return;} let v=t.version(key); let clock=t.clock;
        if payload {t.last_payload.insert(v,clock);} else {t.last_metadata.insert(v,clock);} });
}
pub fn copied(key: usize, bytes: usize, kind: &'static str) {
    if bytes==0 { return; }
    TRACE.with(|t| { let mut t=t.borrow_mut(); if !t.active {return;} let version=t.version(key);let clock=t.clock;
        t.copies.push(CopyEvent {clock,version,bytes,kind}); });
}
fn report(t: &Trace) -> String {
    let mut out=String::from("clock\tversion\tbytes\tkind\tany_observation\tpayload_observation\n");
    for e in &t.copies {
        let payload=t.last_payload.get(&e.version).is_some_and(|c| *c>e.clock);
        let metadata=t.last_metadata.get(&e.version).is_some_and(|c| *c>e.clock);
        out.push_str(&format!("{}\t{}\t{}\t{}\t{}\t{}\n", e.clock,e.version,e.bytes,e.kind,
            if payload||metadata {"REQUIRED"} else {"AVOIDABLE"},if payload {"REQUIRED"} else {"AVOIDABLE"}));
    }
    out
}
pub fn finish(path: &std::path::Path) {
    TRACE.with(|t| {
        let t=t.borrow();
        std::fs::write(path,report(&t)).expect("write external copy trace");
        let mut sites=String::from("clock\tsite\toccurrence\tversions\n");
        for (clock,site,occurrence,versions) in &t.sites {
            let values=versions.iter().map(|v|v.to_string()).collect::<Vec<_>>().join(",");
            sites.push_str(&format!("{clock}\t{site}\t{occurrence}\t{values}\n"));
        }
        std::fs::write(path.with_extension("sites.tsv"),sites).expect("write semantic sites");
        let mut versions=String::from("version\tlast_payload\tlast_metadata\n");
        for v in 1..=t.next_version {
            versions.push_str(&format!("{}\t{}\t{}\n",v,t.last_payload.get(&v).copied().unwrap_or(0),t.last_metadata.get(&v).copied().unwrap_or(0)));
        }
        std::fs::write(path.with_extension("versions.tsv"),versions).expect("write semantic versions");
    });
}
#[cfg(test)]
mod tests {
    use super::*;
    fn rows() -> String { TRACE.with(|t| report(&t.borrow())) }
    #[test] fn observed_old_version_requires_copy() { reset();tick();copied(1,8,"cow");tick();observe(1,true);assert!(rows().ends_with("REQUIRED\tREQUIRED\n")); }
    #[test] fn dead_old_version_is_avoidable() { reset();tick();copied(1,8,"cow");fresh(2);tick();observe(2,true);assert!(rows().ends_with("AVOIDABLE\tAVOIDABLE\n")); }
    #[test] fn address_reuse_does_not_observe_old_version() { reset();tick();copied(1,8,"cow");forget(1);fresh(1);tick();observe(1,true);assert!(rows().ends_with("AVOIDABLE\tAVOIDABLE\n")); }
    #[test] fn in_place_update_starts_a_new_version() { reset();tick();copied(1,8,"snapshot");fresh(1);tick();observe(1,true);assert!(rows().ends_with("AVOIDABLE\tAVOIDABLE\n")); }
    #[test] fn snapshot_keeps_its_old_version() { reset();tick();copied(1,8,"snapshot");fresh(2);tick();observe(1,true);assert!(rows().ends_with("REQUIRED\tREQUIRED\n")); }
    #[test] fn bookkeeping_is_not_a_semantic_observation() { reset();tick();copied(1,8,"cow");tick();pause();observe(1,true);assert!(rows().ends_with("AVOIDABLE\tAVOIDABLE\n")); }
    #[test] fn metadata_only_observation_has_separate_classification() { reset();tick();copied(1,8,"cow");tick();observe(1,false);assert!(rows().ends_with("REQUIRED\tAVOIDABLE\n")); }
    #[test] fn same_instruction_copy_reads_are_not_later_observations() { reset();tick();copied(1,8,"concat");observe(1,true);assert!(rows().ends_with("AVOIDABLE\tAVOIDABLE\n")); }
    #[test] fn versions_are_monotonic_and_addresses_are_not_exported() { reset();tick();copied(900001,8,"cow");forget(900001);copied(900001,8,"cow");assert!(!rows().contains("900001"));assert!(rows().contains("1\t1\t8"));assert!(rows().contains("1\t2\t8")); }
}
