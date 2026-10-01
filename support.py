"""Compiler checkout discovery and reproducible benchmark-only Rust helpers."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

SUITE = Path(__file__).resolve().parent
_default_root = SUITE.parent if (SUITE.parent / 'crates/nil-compiler').exists() else SUITE.parent / 'NIL'
ROOT = Path(os.environ.get('NIL_ROOT', _default_root)).expanduser().resolve()


def source_key(path):
    path = Path(path).resolve()
    if path.is_relative_to(SUITE):
        return 'benchmarks/' + str(path.relative_to(SUITE))
    return str(path.relative_to(ROOT))


def resolve_source(key):
    return SUITE / key.removeprefix('benchmarks/') if key.startswith('benchmarks/') else ROOT / key


def suite_provenance():
    return dict(repository='https://github.com/Ninjacornix/NIL-benchmarks',
                git_revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=SUITE, text=True).strip(),
                git_dirty=bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=SUITE, text=True).strip()))


def helper_manifest():
    if not (ROOT / 'crates/nil-compiler/Cargo.toml').is_file():
        raise ValueError('Set NIL_ROOT to a NIL compiler checkout, or initialize this suite as its benchmarks submodule.')
    home = Path(os.environ.get('NIL_BENCH_HOME', Path.home() / '.local/share/nil/benchmarks')).expanduser()
    key = hashlib.sha256((str(ROOT) + str(SUITE)).encode()).hexdigest()[:16]
    folder = home / 'build-helpers' / key
    folder.mkdir(parents=True, exist_ok=True)
    lines = ['[package]', 'name = "nil-benchmark-helpers"', 'version = "0.1.0"',
             'edition = "2024"', 'rust-version = "1.85"', 'publish = false', '', '[workspace]', '', '[dependencies]']
    for name in ['nil-compiler', 'nil-hir', 'nil-llvm']:
        lines.append(f'{name} = {{ path = {json.dumps(str(ROOT / "crates" / name))} }}')
    for source in sorted((SUITE / 'helpers').glob('*.rs')):
        lines.extend(['', '[[example]]', f'name = {json.dumps(source.stem)}', f'path = {json.dumps(str(source))}'])
    (folder / 'Cargo.toml').write_text('\n'.join(lines) + '\n')
    shutil.copyfile(SUITE / 'helpers/Cargo.lock', folder / 'Cargo.lock')
    return folder / 'Cargo.toml'


def build_helpers(*names):
    command = ['cargo', 'build', '--manifest-path', str(helper_manifest()), '--release', '--locked', '--offline',
               '--target-dir', str(ROOT / 'target')]
    for name in names:
        command.extend(['--example', name])
    subprocess.run(command, cwd=ROOT, check=True)
