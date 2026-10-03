from pathlib import Path


def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = b"".join(f"{i}:{i * (i + 1) // 2}\n".encode("ascii") for i in range(int(data)))
    Path(output_path).write_bytes(output)
    return len(output)
