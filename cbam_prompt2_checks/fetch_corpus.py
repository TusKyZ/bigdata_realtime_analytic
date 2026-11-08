"""Download the legal texts behind the CBAM check pack from EUR-Lex and
export them as plain text, one file per document.

    python3 -I fetch_corpus.py --dl <download dir> --out <output dir>

Writes the two files the check-1 script expects:
    cbam_2023_original.txt   L1  Regulation (EU) 2023/956, OJ text of 10 May 2023
    cbam_2025-10-20.txt      L2  same Regulation, consolidated version of 20 Oct 2025
plus the supporting acts L4, L5, L6 (amending Reg 2025/2083, Reg 1186/2009,
Union Customs Code 952/2013 original and latest consolidated).

Export rules (so evidence can be compared word for word):
  * block elements (p, div, table cells, list items, ...) become line breaks,
    inline elements (span, a, sub, sup, ...) are joined without extra spaces;
  * consolidated-text amendment markers are removed: the "modref" lines
    (e.g. "▼M1", "▼B", "▼C1"), the header "arrow" cells, and inline
    "►M1 ... ◄" brackets. The legal wording itself is untouched.
"""
import argparse
import os
import re
import sys
import time
import urllib.request
import warnings

from bs4 import BeautifulSoup, Comment, Doctype, NavigableString, ProcessingInstruction, Tag
from bs4 import XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)  # EUR-Lex serves XHTML

BASE = "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:"

DOCS = [
    # key, CELEX, output file
    ("L1", "32023R0956", "cbam_2023_original.txt"),
    ("L2", "02023R0956-20251020", "cbam_2025-10-20.txt"),
    ("L4", "32025R2083", "reg_2025_2083.txt"),
    ("L5", "32009R1186", "reg_1186_2009.txt"),
    ("L6", "32013R0952", "ucc_952_2013_original.txt"),
]

BLOCK = {
    "p", "div", "td", "th", "tr", "table", "li", "ul", "ol", "dl", "dt", "dd",
    "h1", "h2", "h3", "h4", "h5", "h6", "br", "hr", "tbody", "thead", "tfoot",
    "caption", "section", "article", "header", "footer", "blockquote", "pre",
    "body", "html", "col", "colgroup",
}

UA = "Mozilla/5.0 (X11; Linux x86_64) cbam-eval-check"


def fetch(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 10_000:
        return open(path, encoding="utf-8").read()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                html = r.read().decode("utf-8")
            break
        except Exception as e:  # network hiccup: back off and retry
            if attempt == 3:
                raise
            print(f"  retry {url}: {e}", file=sys.stderr)
            time.sleep(2 ** (attempt + 1))
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return html


def html_to_text(html):
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "head", "noscript"]):
        t.decompose()
    # consolidated-text furniture: "▼M1" lines and the header arrow cells
    for t in soup.select(".modref, .arrow"):
        t.decompose()

    out = []

    def walk(node):
        for ch in node.children:
            if isinstance(ch, (Comment, Doctype, ProcessingInstruction)):
                continue
            if isinstance(ch, NavigableString):
                out.append(str(ch))
            elif isinstance(ch, Tag):
                block = ch.name in BLOCK
                if block:
                    out.append("\n")
                walk(ch)
                if block:
                    out.append("\n")

    walk(soup)
    text = "".join(out).replace("\xa0", " ")
    # inline amendment brackets: "►M1 text ◄", "►C1 text ◄"
    text = re.sub(r"►\s*(?:M|C|A)?\d*\s*", "", text)
    text = re.sub(r"▼\s*(?:M\d+|C\d+|A\d+|B)\b", "", text)
    text = text.replace("◄", "")
    lines = (re.sub(r"[ \t\r\f\v]+", " ", ln).strip() for ln in text.split("\n"))
    return "\n".join(ln for ln in lines if ln) + "\n"


def latest_consolidated(celex, dl):
    """Find the newest consolidated version of an act from its EUR-Lex 'ALL' page."""
    page = fetch(f"https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:{celex}",
                 os.path.join(dl, f"ALL_{celex}.html"))
    base = "0" + celex[1:]
    dates = sorted(set(re.findall(re.escape(base) + r"-(\d{8})", page)))
    return f"{base}-{dates[-1]}" if dates else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dl", required=True, help="folder for the raw HTML downloads")
    ap.add_argument("--out", required=True, help="folder for the plain-text exports")
    a = ap.parse_args()
    os.makedirs(a.dl, exist_ok=True)
    os.makedirs(a.out, exist_ok=True)

    docs = list(DOCS)
    ucc = latest_consolidated("32013R0952", a.dl)
    if ucc:
        docs.append(("L6c", ucc, f"ucc_952_2013_consolidated_{ucc.split('-')[1]}.txt"))

    for key, celex, name in docs:
        html = fetch(BASE + celex, os.path.join(a.dl, f"{celex}.html"))
        text = html_to_text(html)
        with open(os.path.join(a.out, name), "w", encoding="utf-8") as f:
            f.write(text)
        print(f"{key:4} {celex:22} -> {name:42} {len(text):>8} chars")


if __name__ == "__main__":
    main()
