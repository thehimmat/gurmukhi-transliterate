"""
Common informal / 3HO spellings of Sikh terms, names and greetings.

Informal romanization follows no system, so it can't be reversed by rule.
Instead this is a small table of well-known terms (fewer than 100), each with
the spellings people commonly use. Matching ignores case, spaces, hyphens and
apostrophes, and treats w/v, ee/i, oo/u and doubled letters alike, so
"Waheguru", "Vaheguru" and "Waaheguroo" are one entry.

    from gurmukhi_transliterate.informal import lookup_informal
    lookup_informal('Sat Sri Akaal')     # 'ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ'
"""

from __future__ import annotations

import re

# canonical Gurmukhi → informal spellings (variants that normalize differently)
TERMS: dict[str, tuple[str, ...]] = {
    # greetings and jaikaras
    'ਵਾਹਿਗੁਰੂ': ('Waheguru', 'Wahiguru', 'Vahiguru'),
    'ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖ਼ਾਲਸਾ ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫ਼ਤਿਹ': (
        'Waheguru Ji Ka Khalsa Waheguru Ji Ki Fateh', 'Waheguru Ji Ka Khalsa Waheguru Ji Ki Fatehi'),
    'ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ': ('Sat Sri Akal', 'Sat Shri Akal', 'Sat Siri Akal'),
    'ਬੋਲੇ ਸੋ ਨਿਹਾਲ ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ': ('Bole So Nihal Sat Sri Akal', 'Jo Bole So Nihal Sat Sri Akal'),
    'ੴ': ('Ik Onkar', 'Ek Onkar', 'Ik Oankar', 'Ek Ong Kar', 'Ik Ongkar', 'Ekankar'),
    'ਸਤਿ ਨਾਮੁ': ('Sat Nam', 'Satnam', 'Sat Naam'),
    # scripture and banis
    'ਗੁਰੂ ਗ੍ਰੰਥ ਸਾਹਿਬ': ('Guru Granth Sahib', 'Sri Guru Granth Sahib', 'Siri Guru Granth Sahib'),
    'ਦਸਮ ਗ੍ਰੰਥ': ('Dasam Granth',),
    'ਗੁਰਬਾਣੀ': ('Gurbani',),
    'ਬਾਣੀ': ('Bani',),
    'ਮੂਲ ਮੰਤਰ': ('Mool Mantar', 'Mul Mantar', 'Mool Mantra'),
    'ਜਪੁਜੀ ਸਾਹਿਬ': ('Japji Sahib', 'Japuji Sahib'),
    'ਜਪੁਜੀ': ('Japji', 'Japuji'),
    'ਜਾਪੁ ਸਾਹਿਬ': ('Jaap Sahib', 'Jap Sahib'),
    'ਤ੍ਵ ਪ੍ਰਸਾਦਿ ਸਵੱਯੇ': ('Tav Prasad Savaiye', 'Tav Prasad Swaiye', 'Tav Prasad Savaiyye'),
    'ਚੌਪਈ ਸਾਹਿਬ': ('Chaupai Sahib', 'Chopai Sahib', 'Benti Chaupai'),
    'ਅਨੰਦ ਸਾਹਿਬ': ('Anand Sahib', 'Anandu Sahib'),
    'ਰਹਿਰਾਸ ਸਾਹਿਬ': ('Rehras Sahib', 'Rehraas Sahib', 'Rahras Sahib'),
    'ਕੀਰਤਨ ਸੋਹਿਲਾ': ('Kirtan Sohila', 'Keertan Sohila', 'Sohila'),
    'ਸੁਖਮਨੀ ਸਾਹਿਬ': ('Sukhmani Sahib', 'Sukhmani'),
    'ਆਸਾ ਦੀ ਵਾਰ': ('Asa Di Var', 'Asa Di Vaar'),
    'ਨਿਤਨੇਮ': ('Nitnem',),
    'ਅਰਦਾਸ': ('Ardas', 'Ardaas'),
    'ਹੁਕਮਨਾਮਾ': ('Hukamnama', 'Hukumnama'),
    'ਗੁਟਕਾ': ('Gutka', 'Gutka Sahib'),
    'ਸ਼ਬਦ': ('Shabad', 'Shabd'),
    'ਪਾਠ': ('Path', 'Paath'),
    'ਅਖੰਡ ਪਾਠ': ('Akhand Path', 'Akhand Paath'),
    'ਸਹਿਜ ਪਾਠ': ('Sehaj Path', 'Sahaj Path', 'Sehaj Paath'),
    'ਕੀਰਤਨ': ('Kirtan', 'Keertan'),
    'ਰਾਗ': ('Raag', 'Rag'),
    'ਅੰਗ': ('Ang',),
    # practice and community
    'ਸਿੱਖ': ('Sikh',),
    'ਸਿੱਖੀ': ('Sikhi', 'Sikhee'),
    'ਖ਼ਾਲਸਾ': ('Khalsa', 'Khaalsa'),
    'ਪੰਥ': ('Panth',),
    'ਸੰਗਤ': ('Sangat',),
    'ਸਾਧ ਸੰਗਤ': ('Sadh Sangat', 'Saadh Sangat'),
    'ਲੰਗਰ': ('Langar',),
    'ਸੇਵਾ': ('Seva', 'Sewa'),
    'ਸਿਮਰਨ': ('Simran',),
    'ਨਾਮ': ('Naam', 'Nam'),
    'ਨਾਮ ਸਿਮਰਨ': ('Naam Simran', 'Nam Simran'),
    'ਅੰਮ੍ਰਿਤ': ('Amrit', 'Amrita'),
    'ਕੜਾਹ ਪ੍ਰਸ਼ਾਦ': ('Karah Prashad', 'Karah Parshad', 'Kara Prasad', 'Karah Prasad'),
    'ਪ੍ਰਸ਼ਾਦ': ('Prashad', 'Parshad', 'Prasad'),
    'ਗੁਰਦੁਆਰਾ': ('Gurdwara', 'Gurudwara', 'Gurduara'),
    'ਗੁਰਪੁਰਬ': ('Gurpurab', 'Gurpurb', 'Gurpurbh'),
    'ਵਿਸਾਖੀ': ('Vaisakhi', 'Baisakhi', 'Visakhi'),
    'ਬੰਦੀ ਛੋੜ': ('Bandi Chhor', 'Bandi Chhorh', 'Bandi Chor'),
    'ਪੰਜ ਪਿਆਰੇ': ('Panj Pyare', 'Panj Piare', 'Panj Pyaare'),
    'ਨਿਸ਼ਾਨ ਸਾਹਿਬ': ('Nishan Sahib', 'Nishaan Sahib'),
    'ਖੰਡਾ': ('Khanda',),
    'ਰੁਮਾਲਾ': ('Rumala', 'Rumalla'),
    'ਚੌਰ': ('Chaur', 'Chaur Sahib'),
    'ਗ੍ਰੰਥੀ': ('Granthi',),
    'ਰਾਗੀ': ('Ragi', 'Raagi'),
    'ਢਾਡੀ': ('Dhadi', 'Dhaadi'),
    'ਗਿਆਨੀ': ('Giani', 'Gyani'),
    'ਦਸਤਾਰ': ('Dastar', 'Dastaar'),
    # five Ks
    'ਕੇਸ': ('Kes', 'Kesh'),
    'ਕੰਘਾ': ('Kangha', 'Kanga'),
    'ਕੜਾ': ('Kara', 'Karra'),
    'ਕਿਰਪਾਨ': ('Kirpan', 'Kirpaan'),
    'ਕਛਹਿਰਾ': ('Kachera', 'Kachhera', 'Kachhehra'),
    # people and titles
    'ਜੀ': ('Ji', 'Jee'),
    'ਸਾਹਿਬ': ('Sahib', 'Saheb'),
    'ਸਿੰਘ': ('Singh',),
    'ਕੌਰ': ('Kaur',),
    'ਭਾਈ': ('Bhai',),
    'ਬੀਬੀ': ('Bibi',),
    'ਸੰਤ': ('Sant',),
    'ਸਤਿਗੁਰੂ': ('Satguru', 'Satiguru'),
    'ਗੁਰੂ ਨਾਨਕ ਦੇਵ': ('Guru Nanak Dev',),
    'ਗੁਰੂ ਨਾਨਕ': ('Guru Nanak',),
    'ਗੁਰੂ ਅੰਗਦ ਦੇਵ': ('Guru Angad Dev',),
    'ਗੁਰੂ ਅਮਰ ਦਾਸ': ('Guru Amar Das', 'Guru Amardas'),
    'ਗੁਰੂ ਰਾਮ ਦਾਸ': ('Guru Ram Das', 'Guru Ramdas'),
    'ਗੁਰੂ ਅਰਜਨ ਦੇਵ': ('Guru Arjan Dev', 'Guru Arjun Dev'),
    'ਗੁਰੂ ਹਰਿਗੋਬਿੰਦ': ('Guru Hargobind', 'Guru Hargobind Sahib'),
    'ਗੁਰੂ ਹਰਿ ਰਾਇ': ('Guru Har Rai',),
    'ਗੁਰੂ ਹਰਿ ਕ੍ਰਿਸ਼ਨ': ('Guru Har Krishan', 'Guru Harkrishan'),
    'ਗੁਰੂ ਤੇਗ ਬਹਾਦਰ': ('Guru Tegh Bahadur', 'Guru Teg Bahadur'),
    'ਗੁਰੂ ਗੋਬਿੰਦ ਸਿੰਘ': ('Guru Gobind Singh',),
    # places
    'ਹਰਿਮੰਦਰ ਸਾਹਿਬ': ('Harmandir Sahib', 'Harimandir Sahib', 'Darbar Sahib'),
    'ਅਕਾਲ ਤਖ਼ਤ': ('Akal Takht', 'Akal Takhat'),
    'ਅੰਮ੍ਰਿਤਸਰ': ('Amritsar',),
    'ਅਨੰਦਪੁਰ ਸਾਹਿਬ': ('Anandpur Sahib',),
    'ਨਨਕਾਣਾ ਸਾਹਿਬ': ('Nankana Sahib',),
    'ਕੇਸਗੜ੍ਹ ਸਾਹਿਬ': ('Kesgarh Sahib',),
    'ਦਮਦਮਾ ਸਾਹਿਬ': ('Damdama Sahib',),
    'ਪਟਨਾ ਸਾਹਿਬ': ('Patna Sahib',),
    'ਹਜ਼ੂਰ ਸਾਹਿਬ': ('Hazur Sahib', 'Hazoor Sahib'),
    'ਪੰਜਾਬ': ('Punjab', 'Panjab'),
    'ਪੰਜਾਬੀ': ('Punjabi', 'Panjabi'),
    'ਗੁਰਮੁਖੀ': ('Gurmukhi',),
}

_MAX_WORDS = max(len(v.split()) for vs in TERMS.values() for v in vs)


def _key(text: str) -> str:
    """Spelling-insensitive key: lowercase letters only, w→v, ee→i, oo→u, no doubles."""
    k = re.sub(r'[^a-z]', '', text.lower()).replace('w', 'v')
    k = k.replace('ee', 'i').replace('oo', 'u')
    return re.sub(r'(.)\1+', r'\1', k)


_INDEX: dict[str, str] = {}
for _gurmukhi, _spellings in TERMS.items():
    for _s in _spellings:
        _INDEX.setdefault(_key(_s), _gurmukhi)


def lookup_informal(text: str) -> str | None:
    """Gurmukhi for *text* if the whole of it is a known informal spelling."""
    return _INDEX.get(_key(text)) if _key(text) else None


def reverse_informal(text: str) -> tuple[str | None, list[str]]:
    """Convert *text* phrase by phrase (longest match first).

    Returns (Gurmukhi or None, words not covered). Punctuation-only tokens pass
    through; any word not in a known phrase makes the result None.
    """
    tokens = text.split()
    out: list[str] = []
    missing: list[str] = []
    i = 0
    while i < len(tokens):
        for n in range(min(_MAX_WORDS, len(tokens) - i), 0, -1):
            hit = lookup_informal(' '.join(tokens[i:i + n]))
            if hit:
                out.append(hit)
                i += n
                break
        else:
            tok = tokens[i]
            if re.search(r'[A-Za-z]', tok):
                missing.append(tok)
            else:
                out.append(tok)
            i += 1
    return (' '.join(out) if not missing else None), missing
