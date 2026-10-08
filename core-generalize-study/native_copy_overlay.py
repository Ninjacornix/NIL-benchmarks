"""Partial native owning-storage instrumentation; coverage deliberately fail-closed.

Use only O0 mechanism-census binaries. Counters before optimization can change
which copies survive O2 and must never be reported as original O2 physical copies.
"""
from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent

def patch(shadow):
 path=shadow/'crates/nil-llvm/src/application.c';old=path.read_text();s=old
 # Each entry accounts for an actual C memcpy. This is not yet the complete
 # coverage ledger: map rebuilds and packed aggregates must be added before A1.
 hooks=[
  ('    memcpy(copy->data,value->data,(size_t)value->length*value->width);', '    nil_measure_copy(1,(uint64_t)value->length*value->width,"set");\n    memcpy(copy->data,value->data,(size_t)value->length*value->width);'),
  ('    memcpy(copy->data,a->data,(size_t)a->length*a->width);','    nil_measure_copy(1,(uint64_t)a->length*a->width,"concat_left");\n    memcpy(copy->data,a->data,(size_t)a->length*a->width);'),
  ('    memcpy(copy->data+(size_t)a->length*a->width,b->data,(size_t)b->length*b->width);','    nil_measure_copy(2,(uint64_t)b->length*b->width,"concat_right");\n    memcpy(copy->data+(size_t)a->length*a->width,b->data,(size_t)b->length*b->width);'),
  ('    memcpy(a->data+(size_t)a->length*a->width,b->data,(size_t)b->length*b->width);','    nil_measure_copy(2,(uint64_t)b->length*b->width,"append_right");\n    memcpy(a->data+(size_t)a->length*a->width,b->data,(size_t)b->length*b->width);'),
  ('    if(length) memcpy(copy->data,value->data+(size_t)offset*value->width,(size_t)length*value->width);','    nil_measure_copy(1,(uint64_t)length*value->width,"slice");\n    if(length) memcpy(copy->data,value->data+(size_t)offset*value->width,(size_t)length*value->width);'),
  ('        *nil_map_meta(out)=(NilMapMeta){ec,bc,0};', '        uint64_t measure_bytes=(uint64_t)m->length*sizeof(NilMapEntry);\n        for(int64_t j=0;j<m->length;j++) { const NilMapEntry *e=&nil_map_entries(m)[j]; measure_bytes+=e->key_len; if((uint64_t)j!=i)measure_bytes+=e->value_len; }\n        nil_measure_copy(1,measure_bytes,"map_rebuild");\n        *nil_map_meta(out)=(NilMapMeta){ec,bc,0};'),
  ('        memcpy(copy->data,value->data,(size_t)bytes); value=copy;', '        nil_measure_copy(1,bytes,"sort_cow");\n        memcpy(copy->data,value->data,(size_t)bytes); value=copy;'),
  ('    memcpy(out,nil_record_rows(v)+(uint64_t)index*width,(size_t)width);','    nil_measure_copy(1,width,"record_get");\n    memcpy(out,nil_record_rows(v)+(uint64_t)index*width,(size_t)width);'),
  ('        memcpy(nil_record_rows(copy),nil_record_rows(v),(size_t)v->length*width);','        nil_measure_copy(1,(uint64_t)v->length*width,"record_set_cow");\n        memcpy(nil_record_rows(copy),nil_record_rows(v),(size_t)v->length*width);'),
  ('        memcpy(nil_record_rows(copy)+(uint64_t)index*width,replacement,(size_t)width);','        nil_measure_copy(3,width,"record_set_replacement");\n        memcpy(nil_record_rows(copy)+(uint64_t)index*width,replacement,(size_t)width);'),
  ('    memcpy(row,replacement,(size_t)width);return v;','    nil_measure_copy(3,width,"record_set_replacement");\n    memcpy(row,replacement,(size_t)width);return v;'),
  ('        memcpy(nil_record_rows(copy),nil_record_rows(a),(size_t)a->length*width);','        nil_measure_copy(1,(uint64_t)a->length*width,"record_concat_left");\n        memcpy(nil_record_rows(copy),nil_record_rows(a),(size_t)a->length*width);'),
  ('        memcpy(nil_record_rows(copy)+(uint64_t)a->length*width,nil_record_rows(b),(size_t)b->length*width);','        nil_measure_copy(2,(uint64_t)b->length*width,"record_concat_right");\n        memcpy(nil_record_rows(copy)+(uint64_t)a->length*width,nil_record_rows(b),(size_t)b->length*width);'),
  ('    memcpy(nil_record_rows(a)+(uint64_t)a->length*width,nil_record_rows(b),(size_t)b->length*width);','    nil_measure_copy(2,(uint64_t)b->length*width,"record_append_right");\n    memcpy(nil_record_rows(a)+(uint64_t)a->length*width,nil_record_rows(b),(size_t)b->length*width);'),
  ('    memcpy(nil_record_rows(copy),nil_record_rows(v)+(uint64_t)offset*width,(size_t)length*width);','    nil_measure_copy(1,(uint64_t)length*width,"record_slice");\n    memcpy(nil_record_rows(copy),nil_record_rows(v)+(uint64_t)offset*width,(size_t)length*width);'),
  # Materializing a key or value out of a map duplicates map payload through the
  # shared literal allocator; the construction callers of nil_literal are excluded.
  ('    return nil_literal(nil_map_bytes(m)+e->value,(int64_t)e->value_len,start,end);','    nil_measure_copy(1,e->value_len,"map_value_extract");\n    return nil_literal(nil_map_bytes(m)+e->value,(int64_t)e->value_len,start,end);'),
  ('    return nil_literal(nil_map_bytes(m)+e->key,(int64_t)e->key_len,start,end);','    nil_measure_copy(1,e->key_len,"map_key_extract");\n    return nil_literal(nil_map_bytes(m)+e->key,(int64_t)e->key_len,start,end);'),
 ]
 for before,after in hooks:
  if s.count(before)==0 and before=='        memcpy(copy->data,value->data,(size_t)bytes); value=copy;':
   before='        memcpy(copy->data,value->data,(size_t)bytes);'
   after='        nil_measure_copy(1,bytes,"sort_cow");\n'+before
  if s.count(before)==0 and before=='    memcpy(row,replacement,(size_t)width);return v;':
   before='    memcpy(row,replacement,(size_t)width);'
   after='    nil_measure_copy(3,width,"record_set_replacement");\n'+before
  if s.count(before)==0 and before.startswith('    return nil_literal(nil_map_bytes(m)+e->'):
   field='value' if 'e->value' in before else 'key'
   before=f'    NilSequence *out=nil_literal(nil_map_bytes(m)+e->{field},(int64_t)e->{field}_len,start,end);'
   after=f'    nil_measure_copy(1,e->{field}_len,"map_{field}_extract");\n'+before
  assert s.count(before)==1,(before,s.count(before));s=s.replace(before,after)
 anchor='/* Application runtime: execution-owned immutable sequences. No public pointer ABI. */'
 assert s.count(anchor)==1;s=s.replace(anchor,(HERE/'native_copy_trace.c').read_text()+'\n'+anchor)
 path.write_text(s)
 return {'crates/nil-llvm/src/application.c': {'original_sha256':hashlib.sha256(old.encode()).hexdigest(),'instrumented_sha256':hashlib.sha256(s.encode()).hexdigest(),'coverage':'partial: sequence COW/concat/slice, sort, record-buffer read/update/concat/slice, map rebuild; constructors, key/value materialization, aggregate lowering, relocation remain pending'}}
