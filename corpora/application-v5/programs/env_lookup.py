from pathlib import Path
import os


def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = os.environ.get(data.decode("ascii"), "").encode("utf-8")
    Path(output_path).write_bytes(output)
    return len(output)
