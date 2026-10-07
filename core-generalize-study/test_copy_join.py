import tempfile,unittest
from pathlib import Path
from join_copy_trace import join
class JoinTests(unittest.TestCase):
 def files(self,root,site=7,role=1,version=9):
  ref=root/'reference.tsv';native=root/'native.tsv'
  ref.with_suffix('.sites.tsv').write_text(f'clock\tsite\toccurrence\tversions\n3\t7\t1\t{version}\n')
  ref.with_suffix('.versions.tsv').write_text('version\tlast_payload\tlast_metadata\n9\t2\t4\n')
  native.write_text(f'site\toccurrence\trole\tbytes\tkind\n{site}\t1\t{role}\t8\tset\n')
  return ref,native
 def test_metadata_only_source_is_not_payload_required(self):
  with tempfile.TemporaryDirectory() as d:
   events=join(*self.files(Path(d)));self.assertEqual(events[0]['any_observation'],'REQUIRED');self.assertEqual(events[0]['payload_observation'],'AVOIDABLE')
 def test_unknown_site_is_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(AssertionError,'unknown native site'):join(*self.files(Path(d),site=8))
 def test_unknown_role_is_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(AssertionError,'unknown operand role'):join(*self.files(Path(d),role=2))
 def test_unknown_version_is_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(AssertionError,'unknown semantic source version'):join(*self.files(Path(d),version=0))
if __name__=='__main__':unittest.main()
