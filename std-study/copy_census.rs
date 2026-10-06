//! Source lineage census, not alias/ownership proof. Returns can have several origins.
use nil_compiler::{SourceProfile,compile_with_profile};
use nil_hir::{Operation as O,Instruction,Type,Intrinsic};
use std::collections::BTreeSet;
type Origins=BTreeSet<(usize,bool)>;
fn owned(t:Type)->bool{matches!(t,Type::Bytes|Type::Buffer|Type::RecordBuffer(..)|Type::Record(..)|Type::MapI64|Type::MapBytes|Type::MapRecord(..))}
fn region(r:&nil_hir::Region,inputs:Vec<Origins>,summaries:&[Origins])->Vec<Origins>{let values=items(&r.instructions,inputs,summaries);r.results.iter().map(|id|values[id.0].clone()).collect()}
fn items(list:&[Instruction],mut values:Vec<Origins>,summaries:&[Origins])->Vec<Origins>{for i in list{
let orig=match &i.operation{
 O::Replace{..}|O::Intrinsic{op:Intrinsic::Concat|Intrinsic::Put|Intrinsic::Insert,..} => {
  let index=match &i.operation{O::Replace{array,..}=>array.0,O::Intrinsic{arguments,..}=>arguments[0].0,_=>unreachable!()};
  values[index].iter().map(|(p,_)|(*p,true)).collect()
 },
 O::Field{record,..}=>values[record.0].clone(),
 O::Index{array,..}=>values[array.0].clone(),
 O::UpdateField{record,value,..}=>values[record.0].union(&values[value.0]).copied().collect(),
 O::Record{fields,..}=>fields.iter().flat_map(|id|values[id.0].iter().copied()).collect(),
 O::Call{function,arguments}=>summaries[function.0].iter().flat_map(|(p,updated)|values[arguments[*p].0].iter().map(move |(origin,old)|(*origin,*old||*updated))).collect(),
 O::If{then_region,else_region,..}=>region(then_region,values.clone(),summaries)[0].union(&region(else_region,values.clone(),summaries)[0]).copied().collect(),
 O::Loop{initial,body,finish,..}=>{
  let mut state=initial.iter().map(|id|values[id.0].clone()).collect::<Vec<_>>();
  // Origin sets form a finite lattice: 2 * parameter count, monotonic joins.
  loop{let next=region(body,state.clone(),summaries);let joined=state.iter().zip(next).map(|(a,b)|a.union(&b).copied().collect::<Origins>()).collect::<Vec<_>>();if joined==state{break;}state=joined;}
  region(finish,state,summaries)[0].clone()
 },_=>Origins::new()};
values.push(if owned(i.ty){orig}else{Origins::new()});}values}
fn walk<'a>(items:&'a [Instruction],all:&mut Vec<&'a Instruction>){for i in items{all.push(i);match &i.operation{O::If{then_region,else_region,..}=>{walk(&then_region.instructions,all);walk(&else_region.instructions,all)},O::Loop{condition,body,finish,..}=>{walk(&condition.instructions,all);walk(&body.instructions,all);walk(&finish.instructions,all)},_=>{}}}}
fn main(){for name in std::env::args().skip(1){let source=std::fs::read_to_string(&name).unwrap();let p=compile_with_profile(&source,SourceProfile::ExprV5).unwrap();let fs=&p.hir.program().functions;let mut summaries=vec![Origins::new();fs.len()];
loop {let next=fs.iter().map(|f|{let inputs=f.parameters.iter().enumerate().map(|(i,t)|if owned(*t){BTreeSet::from([(i,false)])}else{Origins::new()}).collect();items(&f.instructions,inputs,&summaries)[f.result.0].clone()}).collect::<Vec<_>>();if next==summaries{break;}summaries=next;}
let update=summaries.iter().map(|o|o.iter().any(|(_,u)|*u)).collect::<Vec<_>>();
let mut calls=0;let mut updated=0;let mut replace=0;
for f in fs{let mut list=vec![];walk(&f.instructions,&mut list);for i in list{match &i.operation{O::Call{function,..}=>{calls+=1;if update[function.0]{updated+=1;}},O::Replace{..}=>replace+=1,_=>{}}}}
println!("{}\t{}\t{}\t{}\t{}",name,calls,updated,update.iter().filter(|b|**b).count(),replace);
}}
