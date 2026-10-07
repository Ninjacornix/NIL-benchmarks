def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def palindrome_spans(text):
    for center in range(2*len(text)-1):
        l=center//2;r=l+center%2
        while l>=0 and r<len(text) and text[l]==text[r]:yield l,r+1;l-=1;r+=1

def palindromic_substrings(data):return scalar(sum(1 for _ in palindrome_spans(data)))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = palindromic_substrings(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
