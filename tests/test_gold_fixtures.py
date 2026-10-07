import csv
import pathlib
import unicodedata

GOLD = pathlib.Path(__file__).parent / 'fixtures' / 'gold'
COLUMNS = ['id', 'source', 'gurmukhi', 'gurbaniakhar', 'banidb', 'banidb_ipa', 'shabados']


def rows():
    with open(GOLD / 'lines.tsv', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\'))


def test_shape():
    r = rows()
    assert len(r) == 500
    assert list(r[0]) == COLUMNS
    assert {x['source'] for x in r} == {'sggs', 'dasam', 'bhai_gurdas'}
    assert all(x[c] for x in r for c in COLUMNS)


def test_gurmukhi_is_nfc_and_has_no_vishraams():
    for x in rows():
        assert unicodedata.normalize('NFC', x['gurmukhi']) == x['gurmukhi']
        assert not set(x['gurmukhi']) & set(';,.')


def test_romanizations_are_latin():
    for x in rows():
        for c in ('gurbaniakhar', 'banidb', 'shabados'):
            assert not any('਀' <= ch <= '੿' for ch in x[c]), (c, x[c])


def test_english_negatives():
    lines = [l for l in (GOLD / 'english.txt').read_text().splitlines() if l.strip()]
    assert len(lines) >= 30
