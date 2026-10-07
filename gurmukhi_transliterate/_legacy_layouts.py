"""
Key maps for the typewriter-layout legacy Gurmukhi fonts, Asees and Joy.

Derived by rendering every glyph of the fonts and reading off the Gurmukhi
it draws (no converter's code was used), then checked against real text:
Sri Gur Sobha (Institute of Sikh Studies, 2014; Asees and Joy) and a 1990s
Chandi Charitar whose unnamed font is Joy-like. Entries marked ``# ?`` were
read from the glyphs but haven't been seen in real text yet.

Keys above U+007F are the Windows-1252 characters a PDF's text layer gives
for those bytes (byte 0x86 arrives as '†').
"""

ASEES_KEYS = {
    # letters
    'a': '਼', 'b': 'ਲ', 'c': 'ਫ', 'd': 'ਦ', 'e': 'ਕ', 'f': 'ਿ', 'g': 'ਪ', 'h': 'ੀ', 'i': 'ਜ',
    'j': 'ਹ', 'k': 'ਾ', 'l': ';', 'm': 'ਠ', 'n': 'ਅ', 'o': 'ਰ', 'p': 'ਬ', 'q': '੍ਰ', 'r': 'ਗ',
    's': 'ਤ', 't': 'ਵ', 'u': 'ਚ', 'v': 'ਡ', 'w': 'ਮ', 'x': 'ਘ', 'y': 'ਖ', 'z': 'ੰ',
    'A': 'ਂ', 'B': 'ਨ', 'C': 'ਙ', 'D': 'ਣ', 'E': 'ਥ', 'F': '',   # F: headline bar  # ?
    'G': 'ਭ', 'H': '.', 'I': 'ਜ਼', 'J': 'ੲ', 'K': 'ਾਂ', 'L': ':', 'M': 'ਝ', 'N': 'ਟ', 'O': '+',
    'P': 'ਸ਼', 'Q': '੍ਹ', 'R': 'ਞ', 'S': 'ਛ', 'T': 'ੳ', 'U': 'ਓ', 'V': 'ੜ', 'W': 'ਰੁ', 'X': 'ਧ',
    'Y': 'ਢ', 'Z': 'ੱ',
    # punctuation keys (digits are literal)
    '!': '*', '"': 'ੌ', '#': '%', '$': '/', '%': '×', '&': '=', "'": 'ੋ', '*': '’', '+': 'ਲ਼',
    '-': '੍', '.': '।', '/': 'ੇ', ':': 'ਯ', ';': 'ਸ', '<': '?', '=': '੍ਹ', '>': 'ੴ', '?': 'ੈ',
    '@': '”', '[': 'ੁ', '\\': 'ਖ਼', ']': '॥', '^': '–', '_': '੍ਵ', '`': '!', '{': 'ੂ', '|': 'ਫ਼',
    '}': 'ਗ਼', '~': 'ੱ',
    # upper range
    '\xa1': 'ੴ', '\xa4': 'ੱ', '\xa7': '੍ਹੂ', '\xa8': 'ੂ', '\xab': '#', '\xae': '੍ਰ', '\xb5': 'ੰ',
    '\xbb': '$', '\xc5': 'ੴ', '\xc6': 'ੴ', '\xc7': '☬', '\xce': 'ਜ', '\xcf': '੍ਯ',  # ? CE, CF
    '\xd2': '॥', '\xda': 'ਃ', '\xe5': 'ੴ', '\xe7': '੍ਚ', '\xfc': 'ੁ',
    '\xf1': '੧', '\xf2': '੨', '\xf3': '੩', '\xf4': '੪', '\xf5': '੫', '\xf6': '੬', '\xf7': '੭',
    '\xf8': '੮', '\xf9': '੯', '\xfa': '੦',
    'œ': '੍ਤ', 'ƒ': 'ਨੂੰ', 'ˆ': 'ਂ', '˜': '੍ਨ', 'μ': 'ੰ', '‐': '੍',
    '†': '੍ਟ', '‹': 'ੴ',
}

# Joy shares Asees's letter keys; punctuation and the upper range differ, and
# the upper range holds whole syllables (ਕੇ, ਪ੍ਰ, ਹੈ).
JOY_KEYS = {
    **{k: ASEES_KEYS[k] for k in 'abcdefghijklmnopqrstuvwxyz'},
    'A': 'ੱ', 'B': 'ਨ', 'C': 'ਙ', 'D': 'ਣ', 'E': 'ਥ', 'F': '-', 'G': 'ਭ', 'H': '.', 'I': 'ਂ',
    'J': 'ੲ', 'K': 'ਾਂ', 'L': ':', 'M': 'ਝ', 'N': 'ਟ', 'O': '+', 'P': '੍ਵ', 'Q': '੍ਹ', 'R': 'ਞ',
    'S': 'ਛ', 'T': 'ੳ', 'U': 'ਓ', 'V': 'ੜ', 'W': '੍ਰੁ', 'X': 'ਧ', 'Y': 'ਢ', 'Z': 'ੱ',  # ? W
    '!': '!', '"': 'ੌ', '#': '‘', '$': 'ਜ', '%': '×', '&': '=', "'": 'ੋ', '*': "'", '+': 'ੈਂ',
    '-': '-', '.': '।', '/': 'ੇ', ':': 'ਯ', ';': 'ਸ', '<': '?', '=': '=', '>': 'ੴ', '?': 'ੈ',
    '@': '"', '[': 'ੁ', '\\': '!', ']': 'ੀਂ', '^': '–', '_': 'ਂ', '`': 'ੰ', '{': 'ੂ', '|': '/',
    '}': 'ਜ਼', '~': 'ੰ',
    '\x80': '੍ਨ', '\x81': '੦', '‚': '੧', 'ƒ': '੨', '„': '੩', '…': '੪',
    '†': '੫', '‡': '੬', 'ˆ': '੭', '‰': '੮', 'Š': '੯', '\x8d': 'ੇ',
    'Œ': '—', '∙': 'ਤੇ', '\xd1': '੧',
    '\xa1': 'ਸ੍ਰ', '\xac': 'ਸ਼੍ਰ',  # ? both
    '\xa2': 'ਉ', '\xa3': 'ਐ', '\xa4': 'ਕੇ', '\xa5': 'ਖ਼', '\xa6': '੍ਹੋ', '\xa7': 'ੁੰ', '\xa8': 'ੂੰ',
    '\xa9': '੍ਰੰ', '\xaa': '‘', '\xab': '’', '\xae': '੍ਹੈ', '\xaf': 'ੌਂ', '\xb0': 'ਜ਼', '\xb1': '੍ਵ',
    '\xb2': 'ਤ੍ਰ', '\xb3': 'ਦ੍ਰ', '\xb4': 'ਹੈ', '\xb5': 'ਸ਼', '\xb6': 'ੰ', '\xb7': 'ਤੇ', '\xb8': 'ੋਂ',
    '\xb9': 'ਨੇ', '\xba': '੍ਹੇ', '\xbb': 'ਰੂ', '\xbc': '÷', '\xbd': 'ਕ੍ਰ', '\xbe': 'ਲ਼', '\xbf': '-',
    '\xc0': '“', '\xc1': '”', '\xc2': '੍ਵੇ', '\xc3': '੍ਵੈ', '\xc4': 'ਏ', '\xc5': 'ਦੇ', '\xc6': 'ੁੱ',
    '\xc7': 'ਗ਼', '\xc8': 'ੴ', '\xc9': 'ੇਂ', '\xca': 'ੲੈ',  # ? CA
    '\xcb': 'ਪ੍ਰ', '\xcc': 'ਨੂੰ', '\xcd': 'ੁੰ', '\xce': 'ੁੰ', '\xcf': 'ਨਾਂ', '\xd0': 'ਿ', '\xd2': '[',
    '\xd3': ']', '\xd4': '॥', '\xd5': 'ਫ਼', '\xd6': 'ਨੈ', '\xd7': 'ਲੇ', '\xd8': 'ਲੈ', '\xdd': '”',
    # older Joy-like fonts (the 1990s Chandi Charitar): lavan on è
    '\xe8': 'ੇ',
}
# the 1990s Chandi Charitar font writes ੍ਯ as ¤ before ਯ (Joy's ¤ alone is ਕੇ)
JOY_COMBOS = {'\xa4:': '੍ਯ'}
