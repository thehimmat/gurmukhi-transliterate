"""Gate: every user story is backed by tagged acceptance tests (#11).

Tests are tagged with ``@pytest.mark.story('US-001', ...)`` on a class or
function, or with ``pytestmark = pytest.mark.story(...)`` for a whole module.
The tags are the source of truth; each story's ``linked_tests`` frontmatter and
``user-stories/INDEX.md`` must agree with them. Run one story's tests with
``pytest --story US-007``.
"""

import ast
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
STORIES = ROOT / 'user-stories'
TESTS = ROOT / 'tests'

FIELDS = {'id', 'title', 'status', 'created', 'updated', 'linked_issues',
          'linked_tests', 'supersedes', 'superseded_by'}
STATUSES = {'proposed', 'in-progress', 'delivered', 'superseded'}


def frontmatter(path):
    text = path.read_text(encoding='utf-8')
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    assert m, f'{path.name}: no frontmatter'
    meta = {}
    for line in m.group(1).splitlines():
        key, _, value = line.partition(':')
        value = value.strip()
        if value.startswith('['):
            value = [v.strip() for v in value[1:-1].split(',') if v.strip()]
        meta[key.strip()] = value
    return meta


def stories():
    return {p.name: frontmatter(p) for p in sorted(STORIES.glob('US-*.md'))}


def tagged():
    """{story id: {test file}} from the story markers in tests/."""
    found = {}
    for path in sorted(TESTS.glob('test_*.py')):
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, ast.Call) and ast.unparse(node.func) == 'pytest.mark.story':
                for arg in node.args:
                    found.setdefault(arg.value, set()).add(f'tests/{path.name}')
    return found


def index_rows():
    rows = {}
    for line in (STORIES / 'INDEX.md').read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if cells and re.fullmatch(r'US-\d{3}', cells[0]):
            rows[cells[0]] = cells
    return rows


@pytest.mark.parametrize('name, meta', stories().items())
def test_story_is_well_formed(name, meta):
    assert set(meta) == FIELDS, name
    assert name.startswith(meta['id'] + '-'), name
    assert meta['status'] in STATUSES, name


def test_markers_name_real_stories():
    ids = {meta['id'] for meta in stories().values()}
    assert set(tagged()) <= ids, set(tagged()) - ids


def test_delivered_stories_have_tests():
    found = tagged()
    untested = [m['id'] for m in stories().values()
                if m['status'] == 'delivered' and not found.get(m['id'])]
    assert not untested


def test_linked_tests_match_markers():
    found = tagged()
    for meta in stories().values():
        assert sorted(meta['linked_tests']) == sorted(found.get(meta['id'], ())), meta['id']


def test_linked_tests_exist():
    for meta in stories().values():
        for path in meta['linked_tests']:
            assert (ROOT / path).is_file(), f"{meta['id']}: {path}"


def test_index_matches_stories():
    rows = index_rows()
    metas = {m['id']: m for m in stories().values()}
    assert set(rows) == set(metas)
    for sid, meta in metas.items():
        _, title, status, *_ = rows[sid]
        assert (title, status) == (meta['title'], meta['status']), sid


def test_story_option_selects_tagged_tests(pytester):
    pytester.makeconftest((TESTS / 'conftest.py').read_text(encoding='utf-8'))
    pytester.makeini('[pytest]\naddopts = --strict-markers\n')
    pytester.makepyfile('''
        import pytest

        pytestmark = pytest.mark.story('US-001')

        def test_one():
            pass

        @pytest.mark.story('US-002')
        class TestTwo:
            def test_two(self):
                pass

        def test_three():
            pass
    ''')
    pytester.runpytest('--story', 'US-002').assert_outcomes(passed=1, deselected=2)
    pytester.runpytest('--story', 'US-001').assert_outcomes(passed=3)
    pytester.runpytest().assert_outcomes(passed=3)
