"""Smoke tests for tools/eval.py (the evaluation harness)."""

import importlib.util
import pathlib

import pytest

TOOLS = pathlib.Path(__file__).resolve().parents[1] / 'tools'


@pytest.fixture(scope='module')
def ev():
    spec = importlib.util.spec_from_file_location('gt_eval', TOOLS / 'eval.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_report_sections(ev):
    md = ev.report()
    for heading in ('Encoding detection', 'System identification', 'Forward fidelity',
                    'Reverse transliteration', 'Lexicon coverage'):
        assert f'## {heading}' in md


def test_detection_counts_every_line(ev):
    rows = ev.eval_detection(ev.load_gold(), ev.load_english())
    assert all(sum(r['labels'].values()) == r['n'] for r in rows)


def test_lexicon_covers_gold(ev):
    lx = ev.eval_lexicon(ev.load_gold())
    assert lx['in_lexicon'] == lx['words']


def test_overlap_is_multiset(ev):
    assert ev.overlap(['a', 'a', 'b'], ['a', 'b', 'b']) == 2


def test_dakshina_reader(ev, tmp_path):
    tsv = tmp_path / 'pa' / 'lexicons' / 'pa.translit.sampled.test.tsv'
    tsv.parent.mkdir(parents=True)
    tsv.write_text('ਸੰਤ\tsanta\t1\nਨਾਨਕ\tnānaka\t1\nਨਾਨਕ\tnanak\t2\n', encoding='utf-8')
    d = ev.eval_dakshina(tmp_path)
    assert d['pairs'] == 3 and d['top1'] == 2   # santa, nānaka reverse exactly; nanak does not


def test_dakshina_missing(ev, tmp_path):
    with pytest.raises(FileNotFoundError):
        ev.eval_dakshina(tmp_path)
