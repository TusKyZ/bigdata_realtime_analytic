"""Print one provision from a plain-text export, joined onto readable lines.

    python3 -I show.py <file> "Article 17" ["Article 25a" ...]
    python3 -I show.py <file> "ANNEX II"

A provision runs from its heading line to the next Article/ANNEX/CHAPTER heading.
"""
import re
import sys

HEAD = re.compile(r"^(Article \d+[a-z]?|ANNEX [IVX]+|CHAPTER [IVX]+)$")

path, wanted = sys.argv[1], sys.argv[2:]
lines = open(path, encoding="utf-8").read().split("\n")
for w in wanted:
    idx = [i for i, ln in enumerate(lines) if ln == w]
    if not idx:
        print(f"##### {w}: NOT PRESENT in {path}\n")
        continue
    # the article body is the LAST exact heading match (earlier ones can be a table of contents)
    i = idx[-1]
    j = i + 1
    while j < len(lines) and not HEAD.match(lines[j]):
        j += 1
    body = lines[i:j]
    # join paragraph numbers / point letters with the text that follows them
    out, buf = [], ""
    for ln in body:
        if re.fullmatch(r"(\d+[a-z]?\.|\([a-z]+\)|\([ivx]+\)|—|–|-)", ln):
            buf += ln + " "
        else:
            out.append(buf + ln)
            buf = ""
    print(f"##### {w}  ({path}, lines {i + 1}-{j})")
    print("\n".join(out))
    print()
