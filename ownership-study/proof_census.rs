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

fn audit(list:&[Instruction],input_types:Vec<Type>,result:&[nil_hir::ValueId],summaries:&[Origins],counts:&mut [usize;3]) {
 let n=input_types.len();let last=nil_hir::liveness::last_uses(list,result,n);
 let mut types=input_types;let mut physical=vec![BTreeSet::from([0usize]);n];
 for (pos,i) in list.iter().enumerate(){
  let mut origins=BTreeSet::new();
  match &i.operation{
   O::Call{function,arguments}=>{
    if summaries[function.0].iter().any(|(_,u)|*u){
     counts[0]+=1;
     let eligible=summaries[function.0].iter().filter(|(_,u)|*u).any(|(p,_)|{
      let id=arguments[*p].0;
      matches!(types[id],Type::Bytes|Type::Buffer|Type::RecordBuffer(..)) && last[id]==Some(pos)
     });
     if eligible{counts[1]+=1;}
     let unique=summaries[function.0].iter().filter(|(_,u)|*u).any(|(p,_)|{
      let id=arguments[*p].0;let origin=&physical[id];
      eligible && last[id]==Some(pos) && matches!(types[id],Type::Bytes|Type::Buffer) && origin.len()==1 && !origin.contains(&0)
      && physical.iter().enumerate().all(|(other,o)|other==id || last[other].is_none_or(|p|p<pos) || o.is_disjoint(origin))
      && arguments.iter().enumerate().all(|(other,arg)|other==*p || physical[arg.0].is_disjoint(origin))
     });
     if unique{counts[2]+=1;}
    }
    for id in arguments {if owned(types[id.0]){origins.extend(&physical[id.0]);}}
    origins.insert(n+pos+1);
   }
   O::Intrinsic{op:Intrinsic::Buffer|Intrinsic::Bytes|Intrinsic::Read|Intrinsic::Slice|Intrinsic::Format|Intrinsic::ParseBuffer,..}|O::Bytes(_)=>{origins.insert(n+pos+1);}
   O::RecordBuffer{fill,..}=>{origins=physical[fill.0].clone();origins.insert(n+pos+1);}
   O::Replace{array,..}=>{origins=physical[array.0].clone();origins.insert(n+pos+1);}
   O::Field{record,..}|O::Index{array:record,..}=>{origins=physical[record.0].clone();}
   O::UpdateField{record,value,..}=>{origins=physical[record.0].union(&physical[value.0]).copied().collect();}
   O::Record{fields,..}=>{for id in fields{origins.extend(&physical[id.0]);}}
   O::Intrinsic{arguments,..}|O::PluginCall{arguments,..}=>{for id in arguments{origins.extend(&physical[id.0]);}origins.insert(n+pos+1);}
   O::If{then_region,else_region,..}=>{
    audit(&then_region.instructions,types.clone(),&then_region.results,summaries,counts);
    audit(&else_region.instructions,types.clone(),&else_region.results,summaries,counts);for o in &physical{origins.extend(o);}origins.insert(0);
   }
   O::Loop{initial,condition,body,finish}=>{
    let ts=initial.iter().map(|id|types[id.0]).collect::<Vec<_>>();
    for r in [condition,body,finish]{audit(&r.instructions,ts.clone(),&r.results,summaries,counts);}for id in initial{origins.extend(&physical[id.0]);}origins.insert(0);
   }
   _=>{}
  }
  types.push(i.ty);physical.push(if owned(i.ty){origins}else{BTreeSet::new()});
 }
}
fn main(){for name in std::env::args().skip(1){
 let source=std::fs::read_to_string(&name).unwrap();let p=compile_with_profile(&source,SourceProfile::ExprV5).unwrap();let fs=&p.hir.program().functions;let mut summaries=vec![Origins::new();fs.len()];
 loop{let next=fs.iter().map(|f|{let inputs=f.parameters.iter().enumerate().map(|(i,t)|if owned(*t){BTreeSet::from([(i,false)])}else{Origins::new()}).collect();items(&f.instructions,inputs,&summaries)[f.result.0].clone()}).collect::<Vec<_>>();if next==summaries{break;}summaries=next;}
 let mut count=[0usize;3];for f in fs{audit(&f.instructions,f.parameters.clone(),&[f.result],&summaries,&mut count);}
 println!("{}\t{}\t{}\t{}",name,count[0],count[1],count[2]);
}}
