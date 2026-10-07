import tempfile
import unittest
from pathlib import Path

import copy_census


class FuzzCensusTests(unittest.TestCase):
    def test_four_argument_helper_is_used_and_arity_failure_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            helper = work / 'fake-helper'
            helper.write_text('#!/usr/bin/env python3\nprint("RESULT\\tE006")\n')
            helper.chmod(0o700)
            with self.assertRaisesRegex(AssertionError, 'wrong arity/types'):
                copy_census.run_pair(helper, helper, work / 'source.nil', work,
                                     b'fixture', work / 'trace.tsv', fuzz=True)

    def test_seed_and_denial_are_fixture_state(self):
        row = dict(index='371', seed='22001', denied='true', invalid_seed='true')
        environment = copy_census.fuzz_environment(row)
        self.assertEqual(environment['NIL_CENSUS_SEED'], '22001')
        self.assertEqual(environment['NIL_RANDOM_SEED'], '01')
        self.assertEqual(environment['NIL_DENY_HOST_IO'], '1')
        self.assertEqual(environment['NIL_FUZZ_RAW'], b'\xff\x80x')
        row.update(denied='false', invalid_seed='false')
        environment = copy_census.fuzz_environment(row)
        self.assertNotIn('NIL_DENY_HOST_IO', environment)
        self.assertNotIn('NIL_CENSUS_INVALID_SEED', environment)

    def test_directory_fixtures_have_deterministic_names(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            copy_census.prepare_fuzz_directories(work)
            copy_census.prepare_fuzz_directories(work)
            self.assertEqual(len(list((work / 'input.bin.entries').iterdir())), 17)
            self.assertEqual(len(list((work / 'input.bin.large').iterdir())), 1024)
            self.assertEqual(list((work / 'input.bin.empty').iterdir()), [])
            self.assertEqual((work / 'input.bin.unreadable').stat().st_mode & 0o777, 0)
            (work / 'input.bin.unreadable').chmod(0o700)


if __name__ == '__main__':
    unittest.main()
