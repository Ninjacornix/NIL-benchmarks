import importlib.util
from pathlib import Path
import unittest
import tiktoken
spec=importlib.util.spec_from_file_location('kernel_attribution',Path(__file__).with_name('attribution.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class TokenLedgerTests(unittest.TestCase):
 def test_binding_semicolons_are_not_loop_delimiters(self):
  source='(v):v=@(a,0;b<#a;x=a[b];a[b:x+1],b+1;a)\n'
  labels=m.nil_labels(source)
  self.assertEqual(labels[source.index(';a[b')],'separator')
  self.assertEqual(labels[source.index(';x=')],'loop_delimiters')
  self.assertEqual(labels[source.index('x=a')],'identifier')
 def test_signature_includes_static_callback_type(self):
  source='(v,[i:i]):v=!map(^b,a)\n'
  labels=m.nil_labels(source)
  self.assertTrue(all(c=='signature' for c in labels[:source.index('=')+1]))
 def test_quoted_loop_marker_is_not_a_loop(self):
  source='0:s="@(not a loop)"\n'
  labels=m.nil_labels(source)
  self.assertEqual(labels[source.index('@')],'text_literal')
 def test_conditionals_classified_in_both_languages(self):
  nil='1=a>0?a:0\n';py='def solve(a):\n    return a if a > 0 else 0\n'
  self.assertEqual(m.nil_labels(nil)[nil.index('?')],'conditional')
  self.assertEqual(m.py_labels(py)[py.index('if')],'conditional')
 def test_update_colon_is_not_a_conditional(self):
  source='5=a[b?c:d:x]\n'
  labels=m.nil_labels(source)
  self.assertEqual(labels[source.index(':d')],'conditional')
  self.assertEqual(labels[source.index(':x')],'functional_update')
 def test_kernel_corpus_hashes_and_token_totals(self):
  import json,hashlib
  density=json.loads(m.DENSITY.read_text());totals={name:{lang:0 for lang in ['nil','python']} for name in ['cl100k_base','o200k_base']}
  original=m.ledger.__globals__['CATEGORIES'];m.ledger.__globals__['CATEGORIES']=(*original,'conditional','functional_update')
  try:
   for row in density['per_task']:
    if row['cut']!='kernel-only' or row['language'] not in totals['cl100k_base']:continue
    lang=row['language'];data=(m.KERNELS/(row['task']+('.nil' if lang=='nil' else '.py'))).read_bytes();text=data.decode()
    self.assertEqual(hashlib.sha256(data).hexdigest(),row['sha256'])
    labels=m.nil_labels(text) if lang=='nil' else m.py_labels(text)
    for name in totals:
     enc=tiktoken.get_encoding(name);ids=enc.encode(text,disallowed_special=())
     counts,_,_=m.ledger(text,labels,[enc.decode_single_token_bytes(t) for t in ids])
     self.assertEqual(sum(counts.values()),row['tokens'][name]);totals[name][lang]+=sum(counts.values())
  finally:m.ledger.__globals__['CATEGORIES']=original
  self.assertEqual(totals,{'cl100k_base':{'nil':4348,'python':2609},'o200k_base':{'nil':4368,'python':2620}})
if __name__=='__main__':unittest.main()
