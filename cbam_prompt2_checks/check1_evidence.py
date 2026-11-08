import json, re

def norm(s):
    s = s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).lower().strip()

# Plain-text exports of the two versions your corpus is built from
src = {v: norm(open(f, encoding="utf-8").read()) for v, f in
       [("original", "cbam_2023_original.txt"), ("consolidated", "cbam_2025-10-20.txt")]}
LABEL = r"(?:Article|ANNEX|Annex|Recital)\s+[\w().,\- &]{0,45}?:\s*"   # strips "Article 9(1):" labels

for it in json.load(open("High_Prompt2.json", encoding="utf-8")):
    text = re.sub(LABEL, " ", it["evidence_en"])
    for piece in re.split(r"\.\.\.|…|\|", text):          # split on ... and |
        for sent in re.split(r"(?<=[.;])\s+", piece):
            s = norm(sent)
            if len(s) > 40 and not any(s in v for v in src.values()):
                print(it["question_id"], "| not found:", sent[:90])
