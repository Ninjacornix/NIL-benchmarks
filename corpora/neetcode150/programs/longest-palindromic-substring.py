def palindrome_spans(text):
    for center in range(2*len(text)-1):
        l=center//2;r=l+center%2
        while l>=0 and r<len(text) and text[l]==text[r]:yield l,r+1;l-=1;r+=1

def longest_palindromic_substring(data):
    best=(0,0)
    for l,r in palindrome_spans(data):
        if r-l>best[1]-best[0] or (r-l==best[1]-best[0] and l<best[0]):best=(l,r)
    return data[best[0]:best[1]]+b'\n'

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = longest_palindromic_substring(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
