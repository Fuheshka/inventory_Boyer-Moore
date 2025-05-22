# search.py

def build_bad_char_table(pattern):
    table = {}
    for i in range(len(pattern) - 1):
        table[pattern[i]] = len(pattern) - 1 - i
    return table


def boyer_moore_search(text, pattern):
    if not pattern or not text:
        return False

    text = text.lower().strip()
    pattern = pattern.lower().strip()
    n, m = len(text), len(pattern)
    if m > n:
        return False

    bad_char = build_bad_char_table(pattern)

    s = 0
    while s <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
        if j < 0:
            return True
        else:
            char = text[s + j]
            shift = bad_char.get(char, m)
            s += max(1, j - shift)
    return False


def fuzzy_match(word, query):
    if len(query) <= len(word):
        return word.startswith(query)
    return query.startswith(word)

