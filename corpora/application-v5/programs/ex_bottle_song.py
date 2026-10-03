from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    start, count = map(int, data.split(b","))
    names = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
    verses = []
    for n in range(start, start-count, -1):
        line = f"{names[n].capitalize()} green {'bottle' if n == 1 else 'bottles'} hanging on the wall,\n"
        last = f"There'll be {names[n-1]} green {'bottle' if n-1 == 1 else 'bottles'} hanging on the wall.\n"
        verses.append(line * 2 + "And if one green bottle should accidentally fall,\n" + last)
    return "\n".join(verses).encode()
