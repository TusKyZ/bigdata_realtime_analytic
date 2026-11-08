"""Check 1, extended: same sentence split and normalisation as check1_evidence.py,
but for every sentence it reports WHICH version holds it, compares that with the
version the item's as_of_date points to (L1 before 20 Oct 2025, L2 from then on),
and for anything not found shows the closest passage and the word differences.

    python3 -I check1_diagnose.py            (run in the folder with the .txt/.json files)
"""
import difflib
import json
import re

SWITCH = "2025-10-20"  # consolidated text L2 applies from this as_of_date


def norm(s):
    s = s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).lower().strip()


src = {v: norm(open(f, encoding="utf-8").read()) for v, f in
       [("L1", "cbam_2023_original.txt"), ("L2", "cbam_2025-10-20.txt")]}
LABEL = r"(?:Article|ANNEX|Annex|Recital)\s+[\w().,\- &]{0,45}?:\s*"


def best_window(s, text):
    """Closest passage in text to sentence s, found via shared 20-char shingles."""
    best = (0.0, "")
    seen = set()
    for i in range(0, max(1, len(s) - 20), 5):
        sh = s[i:i + 20]
        pos = text.find(sh)
        hits = 0
        while pos != -1 and hits < 20:
            start = max(0, pos - i - 15)
            if start not in seen:
                seen.add(start)
                win = text[start:start + len(s) + 30]
                r = difflib.SequenceMatcher(None, s, win, autojunk=False).ratio()
                if r > best[0]:
                    best = (r, win)
            pos = text.find(sh, pos + 1)
            hits += 1
    return best


def word_diff(a, b):
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a.split(), b.split(), autojunk=False).get_opcodes():
        if op != "equal":
            out.append(f"{op}: evidence {' '.join(a.split()[i1:i2])!r} -> law {' '.join(b.split()[j1:j2])!r}")
    return out


items = json.load(open("High_Prompt2.json", encoding="utf-8"))
tot = {"checked": 0, "short_skipped": 0}
for it in items:
    want = "L2" if it["as_of_date"] >= SWITCH else "L1"
    text = re.sub(LABEL, " ", it["evidence_en"])
    rows = []
    for piece in re.split(r"\.\.\.|…|\|", text):
        for sent in re.split(r"(?<=[.;])\s+", piece):
            s = norm(sent)
            if not s:
                continue
            if len(s) <= 40:
                tot["short_skipped"] += 1
                continue
            tot["checked"] += 1
            where = [v for v in ("L1", "L2") if s in src[v]]
            rows.append((s, sent, where))
    n_ok = sum(1 for r in rows if want in r[2])
    print(f"\n{it['question_id']}  as_of {it['as_of_date']}  expects {want}:  "
          f"{n_ok}/{len(rows)} sentences found in {want}")
    for s, sent, where in rows:
        if want in where:
            continue
        tag = f"only in {where[0]}" if where else "NOT FOUND in either"
        print(f"  [{tag}] {sent.strip()[:110]}")
        if not where:
            for v in ("L1", "L2"):
                r, win = best_window(s, src[v])
                if r > 0.6:
                    print(f"      closest in {v} ({r:.0%} similar):")
                    for d in word_diff(s, win)[:6]:
                        print(f"        {d[:150]}")
print(f"\nsentences checked (>40 chars): {tot['checked']}, short pieces skipped: {tot['short_skipped']}")
