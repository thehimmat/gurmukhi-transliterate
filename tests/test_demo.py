"""The browser demo: one page (index.html), wired to the API locally and on Vercel (#2, #3).

Three layers, cheapest first:
- wiring: every endpoint the page fetches exists as api/<name>.py and as a
  Vercel rewrite;
- server: server.py serves that page and those handlers;
- browser: a headless Chromium drives each panel and checks the output appears
  (skipped when Playwright or a browser isn't installed; see README).
"""

import json
import os
import re
import threading
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / 'index.html').read_text(encoding='utf-8')
FETCHED = sorted(set(re.findall(r"fetch\(\s*[`'\"]/api/([a-z_]+)", PAGE)))


class TestWiring:
    def test_page_fetches_the_api(self):
        assert {'transliterate', 'other', 'compare', 'identify', 'legacy', 'systems'} <= set(FETCHED)

    @pytest.mark.parametrize('name', FETCHED)
    def test_each_endpoint_has_a_handler(self, name):
        source = (ROOT / 'api' / f'{name}.py').read_text(encoding='utf-8')
        assert 'class handler' in source

    def test_each_handler_has_a_vercel_rewrite(self):
        rewrites = {r['source'] for r in json.loads((ROOT / 'vercel.json').read_text())['rewrites']}
        handlers = {p.stem for p in (ROOT / 'api').glob('*.py')}
        assert {f'/api/{h}' for h in handlers} <= rewrites

    def test_server_has_no_page_of_its_own(self):
        # server.py serves index.html; a second copy of the page is how they drifted
        assert '<html' not in (ROOT / 'server.py').read_text(encoding='utf-8').lower()


@pytest.fixture(scope='module')
def base_url():
    import importlib.util
    spec = importlib.util.spec_from_file_location('demo_server', ROOT / 'server.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    server = module.serve(0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f'http://127.0.0.1:{server.server_address[1]}'
    server.shutdown()


def get(base_url, path, **params):
    url = f'{base_url}{path}' + ('?' + urllib.parse.urlencode(params) if params else '')
    with urllib.request.urlopen(url) as r:
        return r.read().decode('utf-8')


class TestServer:
    def test_serves_index_html(self, base_url):
        assert get(base_url, '/') == PAGE

    def test_systems(self, base_url):
        from gurmukhi_transliterate import SYSTEM_ORDER
        ids = [s['id'] for s in json.loads(get(base_url, '/api/systems'))]
        assert ids == ['iso15919', 'practical', *SYSTEM_ORDER]

    @pytest.mark.parametrize('path, params, key', [
        ('/api/transliterate', {'text': 'ਸਤਿ'}, 'iso'),
        ('/api/other', {'text': 'ਸਤਿ', 'system': 'shabados'}, 'result'),
        ('/api/compare', {'text': 'ਸਤਿ'}, 'banidb_ipa'),
        ('/api/legacy', {'text': 'uzvh', 'font': 'Asees'}, 'converted_with'),
    ])
    def test_endpoints(self, base_url, path, params, key):
        assert key in json.loads(get(base_url, path, **params))

    def test_identify(self, base_url):
        data = json.loads(get(base_url, '/api/identify', text='The quick brown fox', include_english='1'))
        assert data[0]['system'] == 'english'

    def test_unknown_path(self, base_url):
        with pytest.raises(urllib.error.HTTPError) as e:
            get(base_url, '/api/nope')
        assert e.value.code == 404


# --- browser -----------------------------------------------------------------

def _launch(p):
    try:
        return p.chromium.launch()
    except Exception:
        # Playwright's bundled browser may not be downloaded; use a system one
        exe = os.environ.get('CHROMIUM') or '/opt/pw-browsers/chromium'
        if Path(exe).exists():
            return p.chromium.launch(executable_path=exe)
        raise


@pytest.fixture(scope='module')
def page(base_url):
    sync_api = pytest.importorskip('playwright.sync_api')
    with sync_api.sync_playwright() as p:
        try:
            browser = _launch(p)
        except Exception as e:  # pragma: no cover - depends on the machine
            pytest.skip(f'no browser for Playwright: {e}')
        page = browser.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(base_url + '/')
        page.errors = errors
        yield page
        browser.close()


class TestBrowser:
    def test_no_script_errors(self, page):
        page.wait_for_selector('#other-checkboxes label', state='attached')
        assert page.errors == []

    def test_transliterate(self, page):
        page.fill('#input', 'ਸਤਿ ਨਾਮੁ')
        page.wait_for_function("document.getElementById('iso').textContent !== '—'")
        assert page.text_content('#iso') == 'sati nāmu'
        assert page.text_content('#practical') != '—'

    def test_every_system_is_offered(self, page):
        from gurmukhi_transliterate import SYSTEM_ORDER
        page.wait_for_selector('#other-checkboxes label', state='attached')
        values = page.eval_on_selector_all('#other-checkboxes input', 'els => els.map(e => e.value)')
        assert values == list(SYSTEM_ORDER)

    def test_other_system(self, page):
        page.fill('#input', 'ਸਤਿ ਨਾਮੁ')
        page.click('#other-header')
        page.click('#other-checkboxes label:has(input[value="shabados"])')
        page.wait_for_function("document.getElementById('other-shabados').textContent !== '—'")
        assert page.text_content('#other-shabados') == 'sat naam'

    def test_compare(self, page):
        page.fill('#input', 'ਸਤਿ ਨਾਮੁ')
        page.click('#compare-btn')
        page.wait_for_selector('#compare-modal.open')
        assert page.locator('#compare-body tr').count() == 14
        page.click('#modal-close')

    def test_identify(self, page):
        page.fill('#identify-input', 'kiv sachiaaraa hoieeaai kiv kooRai tuTai paal')
        page.click('#identify-btn')
        page.wait_for_selector('#identify-results .id-row')
        assert 'SikhiToTheMax' in page.text_content('#identify-results .id-label')

    def test_legacy(self, page):
        page.fill('#legacy-input', "fsj py;h; eoh eoskoz. gqG{ pke fJw ej' fpukoz.")
        page.wait_for_function("document.getElementById('legacy-output').textContent !== '—'")
        assert page.text_content('#legacy-output') == 'ਤਿਹ ਬਖਸੀਸ ਕਰੀ ਕਰਤਾਰੰ। ਪ੍ਰਭੂ ਬਾਕ ਇਮ ਕਹੋ ਬਿਚਾਰੰ।'
        assert 'asees' in page.text_content('#legacy-notes')
