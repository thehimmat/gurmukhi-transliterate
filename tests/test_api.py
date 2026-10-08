"""Smoke tests verifying API handlers import and function signatures are correct.

These catch missing library exports or wrong function signatures before a
deployment silently breaks the live site (e.g. forgetting to commit the
library alongside the API handlers).
"""

import sys
import os
import importlib.util

import pytest

pytestmark = pytest.mark.story('US-006')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def _load_api(name):
    path = os.path.join(PROJECT_ROOT, 'api', f'{name}.py')
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestAPIImports:
    """Every handler must import cleanly — catches missing library exports."""

    def test_transliterate_imports(self):
        mod = _load_api('transliterate')
        assert hasattr(mod, 'handler')

    def test_legacy_imports(self):
        mod = _load_api('legacy')
        assert hasattr(mod, 'handler')

    def test_other_imports(self):
        mod = _load_api('other')
        assert hasattr(mod, 'handler')

    def test_compare_imports(self):
        mod = _load_api('compare')
        assert hasattr(mod, 'handler')

    def test_identify_imports(self):
        mod = _load_api('identify')
        assert hasattr(mod, 'handler')


class TestAPISignatures:
    """Core functions must accept the expected parameters — catches signature drift."""

    def test_iso_accepts_delete_schwa(self):
        from gurmukhi_transliterate import GurmukhiISO15919
        iso = GurmukhiISO15919()
        assert isinstance(iso.to_phonetic('ਸਤਿ', delete_schwa=False), str)
        assert isinstance(iso.to_phonetic('ਸਤਿ', delete_schwa=True), str)

    def test_practical_accepts_delete_schwa(self):
        from gurmukhi_transliterate import GurmukhiPractical
        practical = GurmukhiPractical()
        assert isinstance(practical.to_practical('ਸਤਿ', delete_schwa=False), str)
        assert isinstance(practical.to_practical('ਸਤਿ', delete_schwa=True), str)

    def test_comparison_table(self):
        from gurmukhi_transliterate import comparison_table
        result = comparison_table('ਸਿੰਘ')
        assert isinstance(result, dict)
        assert 'iso15919' in result
        assert 'practical' in result

    def test_identify_system(self):
        from gurmukhi_transliterate import identify_system
        result = identify_system('waheguru')
        assert isinstance(result, list)
        assert all({'system', 'label', 'confidence'} <= r.keys() for r in result)

    def test_romanizer(self):
        from gurmukhi_transliterate import GurmukhiRomanizer
        result = GurmukhiRomanizer('dr_sant_singh').romanize('ਸਿੰਘ')
        assert isinstance(result, str)


def _call(handler_cls, path):
    """Drive a BaseHTTPRequestHandler subclass without a socket."""
    import io
    import json
    h = handler_cls.__new__(handler_cls)
    h.path = path
    h.wfile = io.BytesIO()
    h.status = None
    h.send_response = lambda code: setattr(h, 'status', code)
    h.send_header = lambda *a: None
    h.end_headers = lambda: None
    h.do_GET()
    return h.status, json.loads(h.wfile.getvalue())


class TestLegacyEndpoint:
    """/api/legacy exposes warnings and per-line detection, in both servers."""

    def _handlers(self):
        import server
        return [_load_api('legacy').handler, server.Handler]

    def test_report_fields(self):
        from urllib.parse import quote
        for h in self._handlers():
            status, data = _call(h, '/api/legacy?text=' + quote('kèk\ngur pRswid'))
            assert status == 200
            assert data['unicode'] == 'ਕèਕ\nਗੁਰ ਪ੍ਰਸਾਦਿ'
            assert [l['label'] for l in data['lines']] == ['latin', 'anmollipi']
            assert data['warnings'][0]['kind'] == 'unmapped'
