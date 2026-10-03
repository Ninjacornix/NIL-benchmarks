from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    start, count = map(int, data.split(b","))
    def bottles(n, capital=False):
        text = "no more bottles" if n == 0 else "1 bottle" if n == 1 else f"{n} bottles"
        return text.capitalize() if capital else text
    verses = []
    for n in range(start, start-count, -1):
        first = f"{bottles(n, True)} of beer on the wall, {bottles(n)} of beer."
        second = "Go to the store and buy some more, 99 bottles of beer on the wall." if n == 0 else f"Take {'it' if n == 1 else 'one'} down and pass it around, {bottles(n-1)} of beer on the wall."
        verses.append(first + "\n" + second + "\n")
    return "\n".join(verses).encode()
