"""Prototype: romanized/noisy line -> canonical SGGS line using Shabad OS SQLite.

Usage: python3 proto_match.py <master.sqlite> <repo_root>
"""
import random
import re
import sqlite3
import sys
import time
import unicodedata
from collections import Counter, defaultdict

db_path, repo = sys.argv[1], sys.argv[2]
sys.path.insert(0, repo)
from gurmukhi_transliterate import GurmukhiRomanizer  # noqa: E402

# ---- Gurmukhi first-letter -> coarse class (ambiguity-collapsed) ----
G2C = {}
for chars, cls in [
    ("ਅਆਇਈਉਊਏਐਓਔੳੲ", "V"), ("ਸਸ਼", "s"), ("ਹ", "h"), ("ਕਖਖ਼ਕ਼", "k"), ("ਗਘਗ਼", "g"),
    ("ਙਞਣਨ", "n"), ("ਚਛ", "c"), ("ਜਝਜ਼", "j"), ("ਟਠਤਥ", "t"), ("ਡਢਦਧ", "d"),
    ("ਪਫਫ਼", "p"), ("ਬਭ", "b"), ("ਮ", "m"), ("ਯ", "y"), ("ਰੜ", "r"), ("ਲਲ਼", "l"), ("ਵ", "v"),
]:
    for ch in chars:
        G2C[ch] = cls
R2C = {"a": "V", "e": "V", "i": "V", "o": "V", "u": "V", "s": "s", "h": "h", "k": "k", "q": "k",
       "x": "k", "g": "g", "n": "n", "c": "c", "j": "j", "z": "j", "t": "t", "d": "d", "p": "p",
       "f": "p", "b": "b", "m": "m", "y": "y", "r": "r", "l": "l", "v": "v", "w": "v"}

G_STRIP = re.compile(r"[;,.॥।੦-੯0-9]|ਰਹਾਉ")


def g_words(line):
    line = unicodedata.normalize("NFC", line).replace("ਸ਼", "ਸ਼")
    return [w for w in G_STRIP.sub(" ", line).split() if w]


def g_class(line):
    return "".join(G2C.get(w[0], "?") for w in g_words(line))


def r_norm(text):
    t = unicodedata.normalize("NFD", text.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"\|+|[0-9]+|rahaau|rahau|rahao", " ", t)
    return re.sub(r"[^a-z ]", "", t)


def r_class(text):
    return "".join(R2C.get(w[0], "?") for w in r_norm(text).split())


def lev(a, b):
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def semi(q, c):
    """Edit distance of q against best substring of c (free end gaps in c)."""
    prev = [0] * (len(c) + 1)
    for i, cq in enumerate(q, 1):
        cur = [i]
        for j, cc in enumerate(c, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (cq != cc)))
        prev = cur
    return min(prev)


def skel(t):  # consonant skeleton: collapse vowels/aspiration noise
    t = re.sub(r"(?<=[kgcjtdpb])h", "", t)
    t = re.sub(r"[aeiouy]+", "", t)
    return re.sub(r"(.)\1+", r"\1", t)


con = sqlite3.connect(db_path)
rows = con.execute(
    "select line_id, data from asset_lines where type='primary' and asset_id='SSA2'"
).fetchall()
print("SGGS lines:", len(rows))

idx_rom = GurmukhiRomanizer("sttm")
t0 = time.time()
lines = []
for lid, data in rows:
    clean = " ".join(g_words(data))
    lines.append((lid, clean, g_class(data), r_norm(idx_rom.romanize(clean))))
print(f"index build {time.time()-t0:.1f}s")

dup = Counter(l[1] for l in lines)
print("lines whose exact text occurs >1 time:", sum(1 for l in lines if dup[l[1]] > 1),
      f"({100*sum(1 for l in lines if dup[l[1]] > 1)/len(lines):.1f}%)")
cls_dup = Counter(l[2] for l in lines)
print("lines whose first-letter class string is shared with another *different* text:",
      sum(1 for l in lines if cls_dup[l[2]] > dup[l[1]]))

tri = defaultdict(set)
for i, l in enumerate(lines):
    c = l[2]
    for k in range(len(c) - 2):
        tri[c[k:k + 3]].add(i)


def search(query, k=5):
    qc = r_class(query)
    qn = r_norm(query)
    votes = Counter()
    for j in range(len(qc) - 2):
        for i in tri.get(qc[j:j + 3], ()):
            votes[i] += 1
    if len(qc) < 3:
        pool = [i for i, l in enumerate(lines) if l[2].startswith(qc)]
    else:
        pool = [i for i, _ in votes.most_common(300)]
    scored = []
    qs = skel(qn.replace(" ", ""))
    for i in pool:
        lc, lr = lines[i][2], lines[i][3]
        cs = skel(lr.replace(" ", ""))
        d_cls = lev(qc, lc) / max(len(qc), len(lc), 1)
        d_sk = lev(qs, cs) / max(len(qs), 1)
        full = 0.4 * d_cls + 0.6 * d_sk
        part = 0.4 * semi(qc, lc) / max(len(qc), 1) + 0.6 * semi(qs, cs) / max(len(qs), 1)
        # partial-line mode: prefer full match, fall back to substring match with small penalty
        scored.append((min(full, part + 0.05), i))
    scored.sort()
    return [(s, lines[i]) for s, i in scored[:k]]


def corrupt(text, rate, rng):
    out = []
    for ch in text:
        r = rng.random()
        if ch != " " and r < rate / 2:
            continue  # deletion
        if ch != " " and r < rate:
            out.append(rng.choice("abcdeghijklmnoprstuvy"))
            continue
        out.append(ch)
    return "".join(out)


rng = random.Random(7)
sample = rng.sample(range(len(lines)), 300)
q_rom = GurmukhiRomanizer("dr_sant_singh")
for label, rate, partial in [("clean, other system", 0, 1.0), ("10% char noise", 0.10, 1.0),
                             ("20% char noise", 0.20, 1.0), ("first 60% of words", 0, 0.6)]:
    top1 = top5 = 0
    t0 = time.time()
    for i in sample:
        q = q_rom.romanize(lines[i][1])
        if partial < 1:
            ws = q.split()
            q = " ".join(ws[:max(3, int(len(ws) * partial))])
        q = corrupt(q, rate, rng)
        res = search(q)
        texts = [r[1][1] for r in res]
        top1 += texts[:1] == [lines[i][1]]
        top5 += lines[i][1] in texts
    n = len(sample)
    print(f"{label:22s} top1={100*top1/n:.1f}% top5={100*top5/n:.1f}% "
          f"({(time.time()-t0)/n*1000:.0f} ms/query)")

for q in ["so purakh niranjan har purakh niranjan har agamaa agam apaaraa",
          "tati vao na lagai paarbrahm sharnai",
          "sooraj kiran mile jal ka jal hooa ram"]:
    print("\nQ:", q)
    for s, l in search(q, 3):
        print(f"  {s:.3f} {l[0]} {l[1]}")
