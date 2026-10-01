import json
from pathlib import Path
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import support
import bench


class CheckoutBoundaries(unittest.TestCase):
    def test_source_keys_resolve_for_separate_checkouts(self):
        for source in [support.SUITE / 'helpers/native_build.rs', support.ROOT / 'crates/nil-hir/src/lib.rs']:
            self.assertEqual(support.resolve_source(support.source_key(source)), source)

    def test_outputs_cannot_pollute_the_suite_checkout(self):
        with self.assertRaisesRegex(ValueError, 'outside the repository'):
            bench.output_directory('token', support.SUITE / 'results/forbidden')
        self.assertFalse((support.SUITE / 'results/forbidden').exists())

    def test_helper_manifest_uses_selected_compiler_and_external_sources(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict('os.environ', {'NIL_BENCH_HOME': temporary}):
            path = support.helper_manifest()
            data = tomllib.loads(path.read_text())
            self.assertEqual(Path(data['dependencies']['nil-compiler']['path']), support.ROOT / 'crates/nil-compiler')
            self.assertTrue(all(Path(example['path']).is_relative_to(support.SUITE) for example in data['example']))
            self.assertEqual((path.parent / 'Cargo.lock').read_bytes(), (support.SUITE / 'helpers/Cargo.lock').read_bytes())
