from pathlib import Path


def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    counts = [data.count(bytes([digit])) for digit in range(48, 58)]
    output = b"".join(f"{i}:{count}\n".encode("ascii") for i, count in enumerate(counts))
    Path(output_path).write_bytes(output)
    return len(output)
