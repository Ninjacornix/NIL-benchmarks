from pathlib import Path

def solve(input_path, output_path):
    data = Path(input_path).read_bytes()
    output = transform(data)
    Path(output_path).write_bytes(output)
    return len(output)

def transform(data):
    start, end = map(int, data.split(b","))
    animals = ["", "fly", "spider", "bird", "cat", "dog", "goat", "cow", "horse"]
    remarks = ["", "", "It wriggled and jiggled and tickled inside her.", "How absurd to swallow a bird!", "Imagine that, to swallow a cat!", "What a hog, to swallow a dog!", "Just opened her throat and swallowed a goat!", "I don't know how she swallowed a cow!", "She's dead, of course!"]
    verses = []
    for verse in range(start, end+1):
        lines = [f"I know an old lady who swallowed a {animals[verse]}."]
        if verse > 1:
            lines.append(remarks[verse])
        if verse != 8:
            for n in range(verse, 1, -1):
                target = animals[n-1] + (" that wriggled and jiggled and tickled inside her" if n == 3 else "")
                lines.append(f"She swallowed the {animals[n]} to catch the {target}.")
            lines.append("I don't know why she swallowed the fly. Perhaps she'll die.")
        verses.append("\n".join(lines) + "\n")
    return "\n".join(verses).encode()
