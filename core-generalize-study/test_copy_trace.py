import subprocess,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
class CopyTraceTests(unittest.TestCase):
 def test_version_and_observation_tracker(self):
  with tempfile.TemporaryDirectory(prefix='nil-copy-trace-test-') as d:
   binary=Path(d)/'tracker-tests'
   subprocess.run(['rustc','--edition=2024','--test',str(HERE/'copy_trace.rs'),'-o',str(binary)],check=True,capture_output=True)
   result=subprocess.run([str(binary)],check=True,capture_output=True,text=True)
   self.assertIn('9 passed; 0 failed',result.stdout)
if __name__=='__main__':unittest.main()
