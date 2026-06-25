"""Dev server for gurmukhi-transliterate — REST API + demo UI."""

import sys
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, ".")
from gurmukhi_transliterate import (
    GurmukhiISO15919, GurmukhiPractical, GurmukhiLegacy,
    GurmukhiRomanizer, SYSTEMS, SYSTEM_ORDER,
    comparison_table, identify_system,
)

iso = GurmukhiISO15919()
practical = GurmukhiPractical()
legacy = GurmukhiLegacy()

# Build JS-safe system list for the UI
_SYSTEM_JS = json.dumps([
    {"id": sid, "label": SYSTEMS[sid].label}
    for sid in SYSTEM_ORDER
])

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gurmukhi Transliterate</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0f0f0f;
      color: #e8e8e8;
      min-height: 100vh;
      padding: 2rem;
    }
    h1 {
      font-size: 1.4rem;
      font-weight: 600;
      margin-bottom: 1.5rem;
      color: #fff;
    }
    .input-area { margin-bottom: 1.5rem; }
    label {
      display: block;
      font-size: 0.8rem;
      font-weight: 500;
      color: #888;
      margin-bottom: 0.4rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    textarea {
      width: 100%;
      max-width: 640px;
      padding: 0.75rem 1rem;
      font-size: 1.5rem;
      font-family: inherit;
      background: #1a1a1a;
      border: 1px solid #2e2e2e;
      border-radius: 8px;
      color: #fff;
      resize: vertical;
      min-height: 80px;
      outline: none;
      transition: border-color 0.15s;
    }
    textarea:focus { border-color: #555; }
    textarea::placeholder { color: #444; }
    .results {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 1rem;
      max-width: 840px;
    }
    .card {
      background: #1a1a1a;
      border: 1px solid #2e2e2e;
      border-radius: 8px;
      padding: 1rem 1.2rem;
    }
    .card-label {
      font-size: 0.72rem;
      font-weight: 600;
      color: #666;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      margin-bottom: 0.5rem;
    }
    .card-value {
      font-size: 1.2rem;
      color: #e8e8e8;
      min-height: 1.6rem;
      word-break: break-word;
    }
    .card-value.empty { color: #444; font-style: italic; font-size: 0.9rem; }
    .section-title {
      font-size: 0.8rem;
      font-weight: 500;
      color: #888;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin: 1.5rem 0 0.75rem;
    }
    .legacy-section { max-width: 840px; margin-top: 1.5rem; }
    .legacy-row {
      display: flex; gap: 1rem; align-items: flex-start;
      flex-wrap: wrap; margin-bottom: 0.75rem;
    }
    .legacy-row textarea {
      flex: 1; min-width: 200px; max-width: 360px; font-size: 1rem;
    }
    .legacy-arrow { font-size: 1.2rem; color: #444; padding-top: 0.5rem; }
    .legacy-result {
      flex: 1; min-width: 200px;
      background: #1a1a1a; border: 1px solid #2e2e2e;
      border-radius: 8px; padding: 0.75rem 1rem; font-size: 1.5rem;
    }

    /* Schwa deletion checkbox */
    .checkbox-row {
      display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.5rem;
    }
    .checkbox-row input[type=checkbox] {
      width: 15px; height: 15px; cursor: pointer;
      accent-color: #6dbf6d;
    }
    .checkbox-row label {
      font-size: 0.8rem; font-weight: 500; color: #888;
      text-transform: uppercase; letter-spacing: 0.05em;
      cursor: pointer; user-select: none; margin: 0;
    }

    /* Other systems */
    .other-header {
      display: flex; align-items: center; gap: 0.75rem;
      max-width: 840px; margin: 1.5rem 0 0.75rem; cursor: pointer;
    }
    .other-header .section-title { margin: 0; }
    .chevron {
      font-size: 0.65rem; color: #555; transition: transform 0.2s;
      user-select: none;
    }
    .chevron.open { transform: rotate(90deg); }

    .other-checkboxes {
      display: flex; flex-wrap: wrap; gap: 0.5rem;
      max-width: 840px; margin-bottom: 0.75rem;
    }
    .sys-check {
      display: flex; align-items: center; gap: 0.35rem;
      background: #1a1a1a; border: 1px solid #2e2e2e;
      border-radius: 6px; padding: 0.35rem 0.7rem;
      cursor: pointer; user-select: none;
      font-size: 0.78rem; color: #888;
      transition: border-color 0.15s, color 0.15s;
    }
    .sys-check:hover { border-color: #444; color: #bbb; }
    .sys-check.active { border-color: #4a7a4a; color: #8ecf8e; }
    .sys-check input { display: none; }

    .other-results {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 1rem; max-width: 840px;
    }

    /* Compare table */
    .compare-btn {
      margin-top: 0.75rem;
      background: #1a1a1a; border: 1px solid #2e2e2e;
      color: #888; font-size: 0.78rem; font-family: inherit;
      padding: 0.35rem 0.9rem; border-radius: 6px;
      cursor: pointer; transition: border-color 0.15s, color 0.15s;
    }
    .compare-btn:hover { border-color: #555; color: #ccc; }

    .modal-overlay {
      display: none; position: fixed; inset: 0;
      background: rgba(0,0,0,0.7); z-index: 100;
      align-items: flex-start; justify-content: center;
      padding: 2rem;
    }
    .modal-overlay.open { display: flex; }
    .modal {
      background: #111; border: 1px solid #2e2e2e;
      border-radius: 10px; width: 100%; max-width: 720px;
      max-height: 85vh; overflow-y: auto; padding: 1.5rem;
    }
    .modal-header {
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 1rem;
    }
    .modal-header h2 { font-size: 1rem; font-weight: 600; color: #fff; }
    .modal-close {
      background: none; border: none; color: #666; font-size: 1.2rem;
      cursor: pointer; padding: 0.2rem 0.5rem; line-height: 1;
    }
    .modal-close:hover { color: #bbb; }
    .compare-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    .compare-table th {
      text-align: left; padding: 0.5rem 0.75rem;
      border-bottom: 1px solid #222; color: #666;
      font-size: 0.72rem; font-weight: 600; letter-spacing: 0.05em;
      text-transform: uppercase;
    }
    .compare-table td {
      padding: 0.6rem 0.75rem; border-bottom: 1px solid #1c1c1c;
      color: #ccc; vertical-align: top;
    }
    .compare-table tr:last-child td { border-bottom: none; }
    .compare-table .sys-name { color: #666; font-size: 0.75rem; }
    .compare-table .rom-val { font-size: 1rem; }

    /* Identify */
    .identify-section { max-width: 640px; margin-top: 2rem; }
    .identify-row { display: flex; gap: 0.6rem; align-items: center; }
    .identify-row input[type=text] {
      flex: 1; padding: 0.65rem 0.9rem; font-size: 1rem;
      font-family: inherit; background: #1a1a1a;
      border: 1px solid #2e2e2e; border-radius: 8px;
      color: #fff; outline: none; transition: border-color 0.15s;
    }
    .identify-row input[type=text]:focus { border-color: #555; }
    .identify-row input[type=text]::placeholder { color: #444; }
    .identify-btn {
      background: #1a1a1a; border: 1px solid #2e2e2e;
      color: #888; font-size: 0.8rem; font-family: inherit;
      padding: 0.65rem 1rem; border-radius: 8px;
      cursor: pointer; white-space: nowrap;
      transition: border-color 0.15s, color 0.15s;
    }
    .identify-btn:hover { border-color: #555; color: #ccc; }
    .identify-results { margin-top: 0.75rem; }
    .id-row {
      display: flex; align-items: center; gap: 0.75rem;
      padding: 0.5rem 0; border-bottom: 1px solid #1a1a1a;
    }
    .id-row:last-child { border-bottom: none; }
    .id-bar-wrap { flex: 1; height: 4px; background: #1a1a1a; border-radius: 2px; }
    .id-bar { height: 4px; background: #4a7a4a; border-radius: 2px; transition: width 0.3s; }
    .id-label { font-size: 0.8rem; color: #888; min-width: 180px; }
    .id-score { font-size: 0.75rem; color: #555; min-width: 40px; text-align: right; }
  </style>
</head>
<body>
  <h1>Gurmukhi Transliterate</h1>

  <div class="input-area">
    <label>Gurmukhi input</label>
    <textarea id="input" placeholder="ਸਤਿ ਨਾਮੁ ਕਰਤਾ ਪੁਰਖੁ" autofocus></textarea>
  </div>

  <div class="checkbox-row">
    <input type="checkbox" id="schwa-toggle">
    <label for="schwa-toggle">Schwa deletion</label>
  </div>

  <div class="results">
    <div class="card">
      <div class="card-label">ISO 15919</div>
      <div class="card-value empty" id="iso">—</div>
    </div>
    <div class="card">
      <div class="card-label">Practical</div>
      <div class="card-value empty" id="practical">—</div>
    </div>
  </div>

  <!-- Other systems -->
  <div class="other-header" id="other-header">
    <span class="section-title">Other systems</span>
    <span class="chevron" id="chevron">&#9658;</span>
  </div>
  <div id="other-panel" style="display:none">
    <div class="other-checkboxes" id="other-checkboxes"></div>
    <div class="other-results" id="other-results"></div>
    <button class="compare-btn" id="compare-btn">Compare all systems</button>
  </div>

  <!-- Legacy conversion -->
  <div class="section-title">Legacy → Unicode</div>
  <div class="legacy-section">
    <div class="legacy-row">
      <textarea id="legacy-input" placeholder="AnmolLipi / legacy font text"></textarea>
      <span class="legacy-arrow">→</span>
      <div class="legacy-result" id="legacy-output" style="color:#444;font-style:italic;font-size:0.9rem">—</div>
    </div>
  </div>

  <!-- Identify section -->
  <div class="section-title">Identify system</div>
  <div class="identify-section">
    <div class="identify-row">
      <input type="text" id="identify-input" placeholder="waheguru / vaahiguroo / ʋaːɦɪɡʊruː …">
      <button class="identify-btn" id="identify-btn">Which system is this?</button>
    </div>
    <div class="identify-results" id="identify-results"></div>
  </div>

  <!-- Compare modal -->
  <div class="modal-overlay" id="compare-modal">
    <div class="modal">
      <div class="modal-header">
        <h2>All systems comparison</h2>
        <button class="modal-close" id="modal-close">&#x2715;</button>
      </div>
      <table class="compare-table" id="compare-table">
        <thead>
          <tr><th>System</th><th>Romanization</th></tr>
        </thead>
        <tbody id="compare-body"></tbody>
      </table>
    </div>
  </div>

  <script>
    const SYSTEMS = __SYSTEMS_JSON__;
    const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };

    const schwaToggle = document.getElementById('schwa-toggle');
    const inputEl = document.getElementById('input');
    const isoEl = document.getElementById('iso');
    const practicalEl = document.getElementById('practical');

    // --- Other systems panel ---
    const otherCheckboxes = document.getElementById('other-checkboxes');
    const otherResults = document.getElementById('other-results');
    const otherPanel = document.getElementById('other-panel');
    const chevron = document.getElementById('chevron');
    let panelOpen = false;

    document.getElementById('other-header').addEventListener('click', () => {
      panelOpen = !panelOpen;
      otherPanel.style.display = panelOpen ? '' : 'none';
      chevron.classList.toggle('open', panelOpen);
    });

    const activeSystems = new Set();
    const otherCards = {};

    SYSTEMS.forEach(sys => {
      const chip = document.createElement('label');
      chip.className = 'sys-check';
      chip.innerHTML = `<input type="checkbox" value="${sys.id}"><span>${sys.label}</span>`;
      chip.addEventListener('click', e => {
        const cb = chip.querySelector('input');
        // toggle fires before checked changes when using label click
        const willCheck = !cb.checked;
        if (willCheck) {
          activeSystems.add(sys.id);
          chip.classList.add('active');
          if (!otherCards[sys.id]) {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `<div class="card-label">${sys.label}</div>
                              <div class="card-value empty" id="other-${sys.id}">—</div>`;
            otherResults.appendChild(card);
            otherCards[sys.id] = document.getElementById('other-' + sys.id);
          }
          otherCards[sys.id].parentElement.style.display = '';
        } else {
          activeSystems.delete(sys.id);
          chip.classList.remove('active');
          if (otherCards[sys.id]) {
            otherCards[sys.id].parentElement.style.display = 'none';
          }
        }
        updateOther(inputEl.value);
      });
      otherCheckboxes.appendChild(chip);
    });

    async function fetchOther(text, systemId) {
      const schwa = schwaToggle.checked ? '&schwa=1' : '';
      const res = await fetch(`/api/other?text=${encodeURIComponent(text)}&system=${systemId}${schwa}`);
      return res.json();
    }

    const updateOther = debounce(async (text) => {
      for (const sid of activeSystems) {
        const el = otherCards[sid];
        if (!el) continue;
        if (!text.trim()) {
          el.textContent = '—'; el.className = 'card-value empty'; continue;
        }
        const data = await fetchOther(text, sid);
        el.textContent = data.result || '—';
        el.className = data.result ? 'card-value' : 'card-value empty';
      }
    }, 80);

    // --- Main transliterate ---
    async function transliterate(text) {
      const schwa = schwaToggle.checked ? '&schwa=1' : '';
      const res = await fetch('/api/transliterate?text=' + encodeURIComponent(text) + schwa);
      return res.json();
    }

    const updatePhonetic = debounce(async (text) => {
      if (!text.trim()) {
        isoEl.textContent = '—'; isoEl.className = 'card-value empty';
        practicalEl.textContent = '—'; practicalEl.className = 'card-value empty';
        updateOther('');
        return;
      }
      const data = await transliterate(text);
      isoEl.textContent = data.iso || '—';
      isoEl.className = data.iso ? 'card-value' : 'card-value empty';
      practicalEl.textContent = data.practical || '—';
      practicalEl.className = data.practical ? 'card-value' : 'card-value empty';
      updateOther(text);
    }, 80);

    inputEl.addEventListener('input', e => updatePhonetic(e.target.value));
    schwaToggle.addEventListener('change', () => updatePhonetic(inputEl.value));

    // --- Compare modal ---
    const compareBtn = document.getElementById('compare-btn');
    const compareModal = document.getElementById('compare-modal');
    const compareBody = document.getElementById('compare-body');
    document.getElementById('modal-close').addEventListener('click', () => compareModal.classList.remove('open'));
    compareModal.addEventListener('click', e => { if (e.target === compareModal) compareModal.classList.remove('open'); });

    compareBtn.addEventListener('click', async () => {
      const text = inputEl.value.trim();
      if (!text) return;
      const schwa = schwaToggle.checked ? '&schwa=1' : '';
      const res = await fetch('/api/compare?text=' + encodeURIComponent(text) + schwa);
      const data = await res.json();
      const labels = { iso15919: 'ISO 15919', practical: 'Practical' };
      SYSTEMS.forEach(s => { labels[s.id] = s.label; });
      compareBody.innerHTML = Object.entries(data)
        .map(([sid, val]) =>
          `<tr>
            <td class="sys-name">${labels[sid] || sid}</td>
            <td class="rom-val">${val}</td>
          </tr>`
        ).join('');
      compareModal.classList.add('open');
    });

    // --- Legacy ---
    async function convertLegacy(text) {
      const res = await fetch('/api/legacy?text=' + encodeURIComponent(text));
      return res.json();
    }
    const legacyInputEl = document.getElementById('legacy-input');
    const legacyOutputEl = document.getElementById('legacy-output');
    const updateLegacy = debounce(async (text) => {
      if (!text.trim()) {
        legacyOutputEl.textContent = '—';
        legacyOutputEl.style.cssText = 'color:#444;font-style:italic;font-size:0.9rem';
        return;
      }
      const data = await convertLegacy(text);
      legacyOutputEl.textContent = data.unicode || '—';
      legacyOutputEl.style.cssText = '';
    }, 80);
    legacyInputEl.addEventListener('input', e => updateLegacy(e.target.value));

    // --- Identify ---
    const identifyInput = document.getElementById('identify-input');
    const identifyBtn = document.getElementById('identify-btn');
    const identifyResults = document.getElementById('identify-results');

    identifyBtn.addEventListener('click', async () => {
      const text = identifyInput.value.trim();
      if (!text) return;
      const res = await fetch('/api/identify?text=' + encodeURIComponent(text));
      const data = await res.json();
      identifyResults.innerHTML = data.map(r =>
        `<div class="id-row">
          <span class="id-label">${r.label}</span>
          <div class="id-bar-wrap">
            <div class="id-bar" style="width:${Math.round(r.confidence * 100)}%"></div>
          </div>
          <span class="id-score">${Math.round(r.confidence * 100)}%</span>
        </div>`
      ).join('');
    });

    identifyInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') identifyBtn.click();
    });
  </script>
</body>
</html>
"""

# Embed the system list JSON into the HTML
HTML = HTML.replace('__SYSTEMS_JSON__', _SYSTEM_JS)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # suppress default access log

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/":
            body = HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)

        elif path == "/api/transliterate":
            text = params.get("text", [""])[0]
            delete_schwa = bool(params.get("schwa", [""])[0])
            self.send_json({
                "iso": iso.to_phonetic(text, delete_schwa=delete_schwa),
                "practical": practical.to_practical(text, delete_schwa=delete_schwa),
            })

        elif path == "/api/other":
            text = params.get("text", [""])[0]
            system = params.get("system", [""])[0]
            delete_schwa = bool(params.get("schwa", [""])[0])
            if not system or system not in SYSTEMS:
                self.send_json({"error": f"unknown system '{system}'"}, 400)
                return
            result = GurmukhiRomanizer(system).romanize(text, delete_schwa=delete_schwa)
            self.send_json({"system": system, "result": result})

        elif path == "/api/compare":
            text = params.get("text", [""])[0]
            delete_schwa = bool(params.get("schwa", [""])[0])
            self.send_json(comparison_table(text, delete_schwa=delete_schwa))

        elif path == "/api/identify":
            text = params.get("text", [""])[0]
            results = identify_system(text)
            self.send_json(results)

        elif path == "/api/legacy":
            text = params.get("text", [""])[0]
            self.send_json({"unicode": legacy.to_unicode(text)})

        else:
            self.send_json({"error": "not found"}, 404)


if __name__ == "__main__":
    port = 3005
    server = HTTPServer(("", port), Handler)
    print(f"Running at http://localhost:{port}")
    server.serve_forever()
