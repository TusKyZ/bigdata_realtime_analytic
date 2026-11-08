"""File-wide checks 2-7 from the check pack, run against High_Prompt2.json and the
plain-text exports of L1 (original) and L2 (consolidated 2025-10-20).

    python3 -I checks_2_to_7.py      (run in the folder with the .txt/.json files)

2  every cited provision applies on the item's as_of_date (Art 36(2) of the version in force)
3  twin questions are identical
4  shared questions contain no rule that exists in only one version
5  every gold_article names its version
6  evidence quoting recitals: are they in the consolidated text?
7  every CN code used is in Annex I (and whether it is in Annex II)
"""
import json
import re

SWITCH = "2025-10-20"
items = json.load(open("High_Prompt2.json", encoding="utf-8"))
TXT = {"L1": open("cbam_2023_original.txt", encoding="utf-8").read(),
       "L2": open("cbam_2025-10-20.txt", encoding="utf-8").read()}


def version(it):
    return "L2" if it["as_of_date"] >= SWITCH else "L1"


# ---- Art 36(2), transcribed from each export (printed below so it can be eyeballed) ----
def applies_from(ver, art, para):
    if art in {"5", "10", "14", "16", "17"}:
        return "2024-12-31"                                   # (a) in both versions
    if art == "2" and para == "2":
        return "2026-01-01"
    if ver == "L1":                                           # L1 (b)
        if art == "20" and para in {"1", "3", "4", "5"}:
            return "2026-01-01"
        if art in {"4", "6", "7", "8", "9", "15", "19", "21", "22", "23", "24", "25", "26", "27", "31"}:
            return "2026-01-01"
        return "2023-10-01"
    if art == "20" and para in {"1", "3", "4", "5"}:          # L2 (d)
        return "2027-02-01"
    if art == "22" and para == "2":                           # L2 (c)
        return "2027-01-01"
    if art == "22" and para in {"1", "3"}:
        return "2026-01-01"
    if art in {"2a", "4", "6", "7", "8", "9", "10a", "15", "19", "21",
               "23", "24", "25", "25a", "26", "27", "31"}:    # L2 (b); 25a sits inside "23 to 27"
        return "2026-01-01"
    return "2023-10-01"


def cited_provisions(it):
    """(article, paragraph) pairs from gold_article, or from evidence labels when gold is None."""
    if it["gold_article"].strip() != "None":
        s = re.sub(r"^Regulation \(EU\) 2023/956( \([^)]*\))?,", "", it["gold_article"])
        s = re.sub(r"\(point [^)]*\)", "", s)
        s = re.sub(r"Annex [IVX]+", "", s)
        src = "gold_article"
    else:  # only the "Article N(x):" labels, not in-text references such as "Article 256 of Regulation ..."
        s = " ".join(re.findall(r"Article (\d+[a-z]?(?:\(\w+\))*):", it["evidence_en"]))
        src = "evidence labels"
    # skip "-(2)" continuations of a range such as "2a(1)-(2)"
    pairs = re.findall(r"(?<![\w(\-/])(\d+[a-z]?)(?:\((\w+)\))?", s)
    seen, out = set(), []
    for a, p in pairs:
        if (a, p) not in seen:
            seen.add((a, p))
            out.append((a, p))
    return out, src


print("=" * 100)
print("Art 36(2) as exported (the basis of check 2):")
for v in ("L1", "L2"):
    i = TXT[v].index("It shall apply from 1 October 2023")
    print(f"  {v}: " + " ".join(TXT[v][i:i + 520].split("\n")[:12])[:520])

print("\n" + "=" * 100)
print("CHECK 2  cited provisions vs as_of_date")
for it in items:
    v = version(it)
    provs, src = cited_provisions(it)
    late = [(a, p, applies_from(v, a, p)) for a, p in provs if applies_from(v, a, p) > it["as_of_date"]]
    shown = ", ".join(f"Art {a}" + (f"({p})" if p else "") for a, p in provs)
    status = "OK" if not late else "LATER: " + "; ".join(
        f"Art {a}" + (f"({p})" if p else "") + f" applies from {d}" for a, p, d in late)
    print(f"  {it['question_id']}  as_of {it['as_of_date']} [{v}]  from {src}: {shown}\n      -> {status}")

print("\n" + "=" * 100)
print("CHECK 3  twin questions identical")
pairs = {}
for it in items:
    if it["pair_id"] != "none":
        pairs.setdefault(it["pair_id"][:-1], []).append(it)
for k, (a, b) in sorted(pairs.items()):
    same = a["question_th"] == b["question_th"]
    print(f"  {k}: {a['question_id']} vs {b['question_id']}  identical={same}  "
          f"(as_of {a['as_of_date']} vs {b['as_of_date']})")

print("\n" + "=" * 100)
print("CHECK 4  shared questions: phrases tied to only one version")
MARKERS = [  # Thai phrase in a question -> English wording that carries the rule, per version
    ("ไฟฟ้าและไฮโดรเจน", "electricity or hydrogen"),
    ("50 ตัน", "50 tonnes of net mass"),
    ("น้ำหนักสุทธิ", "net mass"),
    ("150 ยูโร", "negligible value"),
    ("มูลค่าเล็กน้อย", "negligible value"),
]
for k, (a, b) in sorted(pairs.items()):
    for th, en in MARKERS:
        if th in a["question_th"]:
            inL1, inL2 = en in TXT["L1"], en in TXT["L2"]
            only = "both versions" if inL1 and inL2 else ("L1 only" if inL1 else ("L2 only" if inL2 else "neither"))
            flag = "LEAK" if only in ("L1 only", "L2 only") else "ok"
            print(f"  {k}: question has '{th}'  ~ '{en}' -> {only}  [{flag}]")

print("\n" + "=" * 100)
print("CHECK 5  gold_article names its version")
for it in items:
    g = it["gold_article"]
    if g.strip() == "None":
        print(f"  {it['question_id']}: gold_article None (unanswerable)")
        continue
    tag = re.search(r"\((Original|Consolidated) \d{4}-\d{2}-\d{2}\)", g)
    print(f"  {it['question_id']}: {'OK  ' + tag.group(0) if tag else 'MISSING version tag'}")

print("\n" + "=" * 100)
print("CHECK 6  recitals quoted in evidence")
for it in items:
    for num, body in re.findall(r"Recital \((\d+)\):\s*(.+?)(?= Recital \(| Article \d| Annex |$)", it["evidence_en"]):
        first = body.split(". ")[0][:80]
        print(f"  {it['question_id']}: Recital ({num}) '{first}...'  in L1={first in TXT['L1']}  in L2={first in TXT['L2']}")

print("\n" + "=" * 100)
print("CHECK 7  CN codes used in questions vs Annex I / Annex II of the item's version")


def annex(v, name, nxt):
    L = TXT[v].split("\n")
    i = max(k for k, x in enumerate(L) if x == name)
    j = min(k for k, x in enumerate(L) if k > i and x == nxt)
    return {re.match(r"^(?:ex )?(\d{4})", x).group(1) for x in L[i:j] if re.match(r"^(?:ex )?\d{4}", x)}, \
        {x[:2] for x in L[i:j] if re.fullmatch(r"\d{2} –.*|\d{2} –", x)}


for it in items:
    codes = re.findall(r"CN (\d{4})", it["question_th"])
    if not codes:
        continue
    v = version(it)
    a1, _ = annex(v, "ANNEX I", "ANNEX II")
    a2, a2_chapters = annex(v, "ANNEX II", "ANNEX III")
    for c in codes:
        in2 = c in a2 or c[:2] in a2_chapters
        print(f"  {it['question_id']} [{v}] CN {c}: Annex I={c in a1}  Annex II={in2}")
