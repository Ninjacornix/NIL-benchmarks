"""Extend a temporary reference checkout with physical storage-copy tracing.

This is incomplete instrumentation until its coverage receipt and native join are
accepted. It does not alter checked-in compiler files or count quota as a copy.
"""
from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent

def patch(shadow):
 changes={}
 def edit(name,transform):
  p=shadow/name;old=p.read_text();new=transform(old);assert new!=old,name;p.write_text(new)
  changes[name]={'original_sha256':hashlib.sha256(old.encode()).hexdigest(),'instrumented_sha256':hashlib.sha256(new.encode()).hexdigest()}
 def replacements(s, pairs):
  for old,new in pairs:
   assert s.count(old)==1,(old,s.count(old));s=s.replace(old,new)
  return s
 trace=(HERE/'copy_trace.rs').read_text();(shadow/'crates/nil-compiler/src/copy_trace.rs').write_text(trace)
 changes['crates/nil-compiler/src/copy_trace.rs']={'instrumented_sha256':hashlib.sha256(trace.encode()).hexdigest()}
 edit('crates/nil-compiler/src/lib.rs',lambda s:s+'\npub mod copy_trace;\n')
 edit('crates/nil-compiler/src/sequence.rs',lambda s:replacements(s,[
  ('        let mut data = Vec::with_capacity(self.capacity);','        crate::copy_trace::copied(self as *const Self as usize, self.data.len()*std::mem::size_of::<T>(), "sequence_cow");\n        let mut data = Vec::with_capacity(self.capacity);'),
  ('        &self.0.data','        crate::copy_trace::observe(self.identity(), true);\n        &self.0.data'),
  ('        &mut Arc::make_mut(&mut self.0).data','        let storage = Arc::make_mut(&mut self.0);\n        crate::copy_trace::fresh(storage as *const Storage<T> as usize);\n        &mut storage.data'),
  ('        let mut data = Vec::with_capacity(capacity);','        crate::copy_trace::copied(self.identity(), self.0.data.len()*std::mem::size_of::<T>(), "concat_left");\n        crate::copy_trace::copied(other.identity(), other.0.data.len()*std::mem::size_of::<T>(), "concat_right");\n        let mut data = Vec::with_capacity(capacity);'),
  ('        let storage = Arc::make_mut(&mut self.0);\n        if storage.capacity', '        crate::copy_trace::copied(other.identity(), other.0.data.len()*std::mem::size_of::<T>(), "append_right");\n        let storage = Arc::make_mut(&mut self.0);\n        crate::copy_trace::fresh(storage as *const Storage<T> as usize);\n        if storage.capacity'),
  ('            storage.data.reserve_exact(capacity - storage.data.len());',
   '            let physical = storage.data.capacity();\n'
   '            storage.data.reserve_exact(capacity - storage.data.len());\n'
   '            if storage.data.capacity() != physical {\n'
   '                crate::copy_trace::copied(storage as *const Storage<T> as usize, storage.data.len()*std::mem::size_of::<T>(), "sequence_growth");\n'
   '            }'),
 ])+'\nimpl<T> Drop for Storage<T> { fn drop(&mut self) { crate::copy_trace::forget(self as *const Self as usize); } }\n')
 edit('crates/nil-compiler/src/evaluator.rs',lambda s:replacements(s,[
  ('        Self::Array(values.into())', '        let value = Self::Array(values.into());\n        if let Self::Array(values)=&value { crate::copy_trace::fresh(values.as_ptr() as usize); }\n        value'),
  ('        let (live, root_counts) = live_bytes(&mut frames);','        crate::copy_trace::pause();\n        let (live, root_counts) = live_bytes(&mut frames);'),
  ('            frame.values.push(value);', '            if matches!(instruction.operation, Operation::Record {..} | Operation::UpdateField {..}) { if let Value::Record(_,fields)=&value { crate::copy_trace::fresh(fields.as_ptr() as usize); } }\n            frame.values.push(value);'),
  ('            frame.next += 1;','            frame.next += 1;\n            crate::copy_trace::begin(instruction.measurement_site, &copy_operands(&instruction.operation, &frame.values));'),
  ('                    let mut updated = fields.to_vec();','                    crate::copy_trace::copied(fields.as_ptr() as usize, fields.len()*std::mem::size_of::<Value>(), "record_update");\n                    let mut updated = fields.to_vec();'),
  ('                                let mut next = original.elements().to_vec();','                                if let Value::Array(values) = &original { crate::copy_trace::copied(values.as_ptr() as usize, values.len()*8, "array_update"); }\n                                let mut next = original.elements().to_vec();'),
  ('                    Value::RecordBuffer(*ty, v[a..end].to_vec().into())', '                    crate::copy_trace::copied(v.identity(), n*std::mem::size_of::<Value>(), "record_buffer_slice");\n                    Value::RecordBuffer(*ty, v[a..end].to_vec().into())'),
  ('                Operation::Length(array) => Value::I64(frame.values[array.0].len() as i64),','                Operation::Length(array) => {\n                    crate::copy_trace::pause();\n                    let value = frame.values[array.0].len() as i64;\n                    crate::copy_trace::tick();\n                    frame.values[array.0].observe_copy(false);\n                    Value::I64(value)\n                },'),
  ('                        return Ok(results[0].clone());','                        crate::copy_trace::tick();\n                        results[0].observe_copy(true);\n                        return Ok(results[0].clone());'),
  ('                    fields[*field].clone()','                    crate::copy_trace::observe(fields.as_ptr() as usize, true);\n                    fields[*field].clone()'),
  ('            Self::Array(values) => values,','            Self::Array(values) => { crate::copy_trace::observe(values.as_ptr() as usize, true); values },'),
  # Insert/Put duplicate the key and byte-value argument payloads before the map
  # takes its own copies; these are payload copies of a live logical version.
  ('                    let key = frame.values[arguments[1].0].bytes().to_vec();',
   '                    let key = { let source = &frame.values[arguments[1].0];\n'
   '                        if let Value::Bytes(v) = source { crate::copy_trace::copied(v.identity(), v.len(), "map_key_argument"); }\n'
   '                        source.bytes().to_vec() };'),
  ('                        Value::Bytes(v) => crate::keyed::EntryValue::Bytes(v.to_vec()),',
   '                        Value::Bytes(v) => { crate::copy_trace::copied(v.identity(), v.len(), "map_value_argument"); crate::keyed::EntryValue::Bytes(v.to_vec()) },'),
 ])+'''\nfn copy_operands(op: &Operation, values: &[Value]) -> Vec<Option<usize>> {
    let ids: Vec<ValueId> = match op {
        Operation::Replace {array,index,value} => vec![*array,*index,*value],
        Operation::UpdateField {record,value,..} => vec![*record,*value],
        Operation::Field {record,..} => vec![*record],
        Operation::RecordBuffer {length,fill,..} => vec![*length,*fill],
        Operation::Index {array,index} => vec![*array,*index],
        Operation::Intrinsic {arguments,..} => arguments.clone(),
        Operation::Record {fields,..} => fields.clone(),
        _ => vec![],
    };
    ids.iter().map(|id| match &values[id.0] {
        Value::Record(_,fields) => Some(fields.as_ptr() as usize),
        Value::Array(v) => Some(v.as_ptr() as usize),
        value => value.identity(),
    }).collect()
}
impl Value {
    pub(crate) fn observe_copy(&self, payload: bool) {
        match self {
            Self::Record(_, fields) => {
                crate::copy_trace::observe(fields.as_ptr() as usize, payload);
                if payload { for child in fields.iter() { child.observe_copy(true); } }
            }
            Self::RecordBuffer(_, values) => {
                crate::copy_trace::observe(values.identity(), payload);
                if payload { for child in values.iter() { child.observe_copy(true); } }
            }
            Self::Array(values) => crate::copy_trace::observe(values.as_ptr() as usize, payload),
            _ => if let Some(id)=self.identity() { crate::copy_trace::observe(id,payload); },
        }
    }
}
''')
 edit('crates/nil-compiler/src/application.rs',lambda s:replacements(s,[
  ('                    Value::Bytes(entry.0.clone().into())', '                    crate::copy_trace::copied(map.identity(), entry.0.len(), "map_key_extract");\n                    Value::Bytes(entry.0.clone().into())'),
  ('                            Value::Bytes(v.clone().into())', '                            crate::copy_trace::copied(map.identity(), v.len(), "map_value_extract");\n                            Value::Bytes(v.clone().into())'),
  ('Value::Bytes(v) => Value::Bytes(v[start..end].to_vec().into()),','Value::Bytes(v) => { crate::copy_trace::copied(v.identity(), end-start, "bytes_slice"); Value::Bytes(v[start..end].to_vec().into()) },'),
  ('Value::Buffer(v) => Value::Buffer(v[start..end].to_vec().into()),','Value::Buffer(v) => { crate::copy_trace::copied(v.identity(), (end-start)*8, "buffer_slice"); Value::Buffer(v[start..end].to_vec().into()) },'),
 ]))
 edit('crates/nil-compiler/src/keyed.rs',lambda s:replacements(s,[
  ('#[derive(Clone, Debug)]\nstruct Storage', '#[derive(Debug)]\nstruct Storage'),
  ('        &self.0.entries', '        crate::copy_trace::observe(self.identity(), true);\n        &self.0.entries'),
  ('        self.0.index.get(key).map', '        crate::copy_trace::observe(self.identity(), true);\n        self.0.index.get(key).map'),
  ('        let position = self.0.index.get(key).copied();', '        crate::copy_trace::observe(self.identity(), true);\n        let position = self.0.index.get(key).copied();'),
  # The map takes its own owned key copies from a transient scratch slice that
  # carries no logical version; both land in CONSTRUCTION against the new map.
  ('            storage.index.insert(key.to_vec(), storage.entries.len());\n            storage.entries.push((key.to_vec(), value));',
   '            let own = storage as *const Storage as usize;\n'
   '            crate::copy_trace::copied(own, key.len(), "map_key_own_index");\n'
   '            storage.index.insert(key.to_vec(), storage.entries.len());\n'
   '            let before = storage.entries.capacity();\n'
   '            crate::copy_trace::copied(own, key.len(), "map_key_own_entry");\n'
   '            storage.entries.push((key.to_vec(), value));\n'
   '            if storage.entries.capacity() != before {\n'
   '                crate::copy_trace::copied(own, before * std::mem::size_of::<(Vec<u8>, EntryValue)>(), "map_entries_growth");\n'
   '            }'),
  ('            storage.index.insert(key.clone(), i);',
   '            crate::copy_trace::copied(storage as *const Storage as usize, key.len(), "map_reindex_key");\n'
   '            storage.index.insert(key.clone(), i);'),
 ]).replace('        let storage = Arc::make_mut(&mut self.0);', '        let storage = Arc::make_mut(&mut self.0);\n        crate::copy_trace::fresh(storage as *const Storage as usize);')+'''\nimpl Clone for Storage {
    fn clone(&self) -> Self {
        let entry_bytes=self.entries.len()*std::mem::size_of::<(Vec<u8>, EntryValue)>();
        let payload_bytes:usize=self.entries.iter().map(|(k,v)| k.len()+v.bytes_len()).sum();
        let index_bytes:usize=self.index.keys().map(|k| k.len()+std::mem::size_of::<usize>()).sum();
        crate::copy_trace::copied(self as *const Self as usize, entry_bytes+payload_bytes+index_bytes, "map_cow");
        Self {entries:self.entries.clone(),index:self.index.clone(),entry_capacity:self.entry_capacity,
            byte_capacity:self.byte_capacity,used:self.used,ty:self.ty}
    }
}
impl Drop for Storage { fn drop(&mut self) { crate::copy_trace::forget(self as *const Self as usize); } }
''')
 edit('crates/nil-compiler/src/records.rs',lambda s:replacements(s,[
  ('pub fn pack(value: &Value, out: &mut Vec<u8>) {','pub fn pack(value: &Value, out: &mut Vec<u8>) {\n    value.observe_copy(true);'),
 ]))
 return changes
