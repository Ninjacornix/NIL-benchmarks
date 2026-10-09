#!/usr/bin/env python3
"""Fail-closed B4 admission matrix; known crashes remain failed comparisons.

This is an audit, not a passing regression gate or a production depth fix.
Commands, raw status/stdout/stderr and source hashes are retained outside git.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIAGNOSTIC = re.compile(rb"(E[0-9]{3})(?: @([0-9]+)\.\.([0-9]+))? [^\n]+\n$")


def definitions():
    array = "[" + ",".join(map(str, range(256))) + "]"
    large = ("record R(" + ",".join(f"f{i}:256" for i in range(15)) + ")\n"
             + "1=#b(a,R(" + ",".join([array] * 15) + "))\n"
             + "(i,R):s=a<1?!bytes(1,0):!concat(b(a-1,b),!bytes(1,b.f0[a%256]))\n")
    return [
        dict(id="reported-literal-recursion", source="=#b(200000)\n1:s=a<1?!bytes(1,0):!concat(b(a-1),!bytes(1,1))\n", arguments=[]),
        dict(id="mutual-sequence-recursion", source="1=#b(a)\n1:s=a<1?!bytes(1,0):!concat(c(a-1),\"x\")\n1:s=a<1?!bytes(1,0):!concat(b(a-1),\"x\")\n", arguments=["200000"]),
        dict(id="large-record-recursion", source=large, arguments=["200000"]),
    ]


def observe(result):
    # Never infer E008 from a signal or translate an ASan report into a depth error.
    if result.returncode < 0:
        return dict(kind="signal", signal=-result.returncode)
    match = DIAGNOSTIC.fullmatch(result.stderr)
    if result.returncode == 1 and match and not result.stdout:
        span = [int(match[2]), int(match[3])] if match[2] else None
        if span and span[0] > span[1]:
            return dict(kind="invalid-diagnostic")
        return dict(kind="diagnostic", code=match[1].decode(), span=span)
    if result.returncode == 0 and not result.stderr:
        return dict(kind="success", stdout_hex=result.stdout.hex())
    return dict(kind="infrastructure", exit=result.returncode)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    out = args.out.expanduser().resolve()
    if out.is_relative_to(ROOT):
        parser.error("raw artifacts must be outside the checkout")
    out.mkdir(parents=True, exist_ok=False)
    deps = ROOT / "target/release/deps"
    driver = out / "depth-driver"
    build_driver = ["rustc", "--edition=2024", str(HERE / "reference_depth.rs"), "-L", f"dependency={deps}"]
    for crate in ("nil_compiler", "nil_hir", "nil_llvm"):
        build_driver += ["--extern", f"{crate}={ROOT}/target/release/lib{crate}.rlib"]
    build_driver += ["-o", str(driver)]
    subprocess.run(build_driver, cwd=ROOT, check=True, capture_output=True)
    rows = []
    started = time.time()
    for case in definitions():
        work = out / case["id"]
        work.mkdir()
        path = work / "source.nil"
        path.write_text(case["source"])
        for depth in (32, 256, 1024):
            reference_command = [str(driver), "reference", str(path), str(depth), *case["arguments"]]
            reference = subprocess.run(reference_command, capture_output=True, timeout=60)
            expected = observe(reference)
            assert expected.get("code") == "E008" and expected.get("span") is not None, expected
            (work / f"reference-{depth}.stderr").write_bytes(reference.stderr)
            for mode in ("bounded", "unbounded"):
                for opt in ("O0", "O2"):
                    binary = work / f"native-{depth}-{mode}-{opt}"
                    build = [str(driver), mode, str(path), str(depth), str(binary), opt]
                    compiled = subprocess.run(build, capture_output=True, timeout=120)
                    (work / f"{binary.name}.build.stderr").write_bytes(compiled.stderr)
                    row = dict(family=case["id"], depth=depth, mode=mode, optimization=opt,
                               source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                               reference_command=reference_command, build_command=build, reference=expected)
                    if compiled.returncode:
                        row |= dict(native=dict(kind="build-failure", exit=compiled.returncode,
                                               stderr=compiled.stderr.decode(errors="replace")), equal=False)
                    else:
                        command = [str(binary), *case["arguments"]]
                        try:
                            result = subprocess.run(command, capture_output=True, timeout=30)
                            (work / f"{binary.name}.stdout").write_bytes(result.stdout)
                            (work / f"{binary.name}.stderr").write_bytes(result.stderr)
                            actual = observe(result)
                            row |= dict(run_command=command, native=actual, exit=result.returncode, equal=actual == expected)
                        except subprocess.TimeoutExpired:
                            row |= dict(run_command=command, native=dict(kind="timeout"), equal=False)
                    rows.append(row)
                    print(case["id"], depth, mode, opt, "PARITY" if row["equal"] else "FAIL", row["native"], flush=True)
    report = dict(schema=1, revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  benchmark_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=HERE, text=True).strip(),
                  started_unix=started, finished_unix=time.time(), driver_command=build_driver,
                  driver_source_sha256=hashlib.sha256((HERE / "reference_depth.rs").read_bytes()).hexdigest(),
                  clang=os.environ.get("NIL_CLANG", "clang"), rows=rows,
                  compared=len(rows), equal=sum(r["equal"] for r in rows), failed=sum(not r["equal"] for r in rows))
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"{report['equal']}/{report['compared']} exact; {report['failed']} failed", flush=True)
    raise SystemExit(1 if report["failed"] else 0)


if __name__ == "__main__":
    main()
