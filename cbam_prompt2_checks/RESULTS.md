# Prompt 2 High: check results

Run on 8 Nov 2026 against `High_Prompt2.json` (10 items, sha256 `a991ab0a…c6ed0`) and the law texts fetched from EUR-Lex the same day. Follows the check pack of 7 Nov 2026.

## Bottom line

- **Check 1 (evidence word for word): no real mismatches.** The pack's script prints 4 lines, and all 4 are formatting false alarms. A stricter version-aware run matched **64 of 64 evidence sentences** (over 40 characters) to the law. Each one is in the version its as_of date calls for, except QA-009's two recitals (three sentences), which exist only in L1 (expected).
- **Every "Check" fact on QA-001 to QA-004 holds**, and QA-005 still holds.
- **The pack's main findings stand.** QA-009 and QA-010 should be relabelled false_premise. QA-006 applies Art 27 before 1 Jan 2026. PAIR-2 leaks a 2026-only rule. QA-004 has no version tag. QA-009's recitals exist only in L1.
- **Where this run corrects or extends the pack:**
  1. **QA-007:** the pinpoint fix isn't needed. The "serious infringement" sentence is in Art 25a(4) itself (third subparagraph).
  2. **QA-007:** gold_article cites "Article 2(3)", which in the consolidated text is now the military-goods exemption. Drop it.
  3. **QA-010:** adding UCC Art 4 (L6) grounds Switzerland but **not the UK**. Even the latest consolidated UCC still lists the UK in Art 4(1). Ground the UK fact with the Withdrawal Agreement, Art 126.
  4. **QA-006:** for the 2024 twin, "ยกเว้นไฟฟ้าและไฮโดรเจน" is a leak and also a false premise. L1 has no such exception.
  5. **Minor:** QA-004's gold_article cites Art 35(2), which the answer doesn't use. In QA-009, "polymers" appear only in the review clause, and Annex I does have one chapter-27 code (electricity). None of the 2023/956 corrigenda apply to the English text.

## Check 1: the pack's script, run unchanged (`check1_evidence.py`)

```
CBAM-QA-003 | not found:  Greenhouse gas: Carbon dioxide and nitrous oxide.
CBAM-QA-003 | not found:  Greenhouse gas: Carbon dioxide and perfluorocarbons.
CBAM-QA-006 | not found:  By way of derogation from paragraphs 1 and 2, this Regulation shall not apply to: (a) goo
CBAM-QA-010 | not found: THIRD COUNTRIES AND TERRITORIES OUTSIDE THE SCOPE OF THIS REGULATION: This Regulation shal
```

| Line | Cause | Real problem? |
|---|---|---|
| QA-003 (×2) | "Greenhouse gas:" is the Annex I column header, written into the quote. The cell text is in the 3102 row (CO2 and nitrous oxide) and the 7610 row (CO2 and perfluorocarbons), in both versions. | No |
| QA-006 | L1 has a footnote marker "(22)" after "Council Regulation (EC) No 1186/2009". The evidence leaves it out; every word is otherwise identical. | No |
| QA-010 | The evidence adds ":" after the Annex III heading and "." after "Switzerland". The words are identical. | No |

## Check 1, version-aware (`check1_diagnose.py`)

The same sentence split and normalisation, but each sentence is matched against the version the as_of date points to: L1 before 20 Oct 2025, L2 from that date.

| Item | as_of | Version | Found | Note |
|---|---|---|---|---|
| QA-001 | 2026-06-01 | L2 | 9/9 | |
| QA-002 | 2026-06-01 | L2 | 4/4 | |
| QA-003 | 2026-06-01 | L2 | 10/12 | the 2 are the "Greenhouse gas:" header labels |
| QA-004 | 2024-06-15 | L1 | 4/4 | |
| QA-005 | 2026-06-15 | L2 | 8/8 | |
| QA-006 | 2024-05-01 | L1 | 4/5 | the footnote marker above |
| QA-007 | 2026-02-01 | L2 | 9/9 | |
| QA-008 | 2026-06-01 | L2 | 3/3 | |
| QA-009 | 2026-06-01 | L2 | 2/5 | the 3 are sentences of Recitals 34 and 35, found in L1 only (check 6) |
| QA-010 | 2026-06-01 | L2 | 4/5 | the heading-colon line above |

64 sentences were checked. 18 short pieces (40 characters or fewer, such as "CN code: 2804 10 00 – Hydrogen") are skipped by design; the annex rows they come from were checked by hand below.

## Item by item

**QA-001: Check → confirmed.** L2 Art 9(1), (2) and (3) match the evidence verbatim: rebates are taken into account, the certifier is independent of the declarant and of the third country, and records are kept until the end of the fourth year. L2 also has a new Art 9(4) (default carbon prices, "As from 2027…"), which confirms the pack's context note.

**QA-002: Check → confirmed.** L2 Art 17(7) says "30 September". L1 said "31 May", so the file's notes are right. The Art 31 free-allocation adjustment in Art 17(5) exists only in L2.

**QA-003: Check → confirmed.** In Annex I, 3102 carries CO2 and nitrous oxide, and 7610 carries CO2 and perfluorocarbons. Annex II contains 7610 but not 3102, in both versions. Art 3(22) and Art 7(1) have the same numbering and wording.

**QA-004: Check → confirmed.** L1 Art 32 limits obligations to reporting. Art 35(1) gives the one-month deadline. Art 36(2)(a) to (b) match the evidence. Still to do: add the "(Original 2023-05-10)" tag. Minor: gold_article cites Art 35(2) (contents of the report), which the answer doesn't use.

**QA-005: still verified.** All 8 evidence sentences are in L2. Art 20(1) applies only from 1 Feb 2027, which the gold answer says.

**QA-006: Fix → confirmed.**
- L1 Art 2(3)(a) to (b) are verbatim.
- Reg 1186/2009 Art 23(2) defines the threshold as "a total of EUR 150 per consignment".
- L1 Art 27(2)(b) is verbatim.
- L1 Art 36(2)(b) makes "Articles 21 to 27" apply only from 1 Jan 2026, so Art 27 was not yet applicable on 1 May 2024.
- Question leak: L1 Art 2(3)(a) covers all Annex I goods and has no electricity or hydrogen exception. That exception exists only in L2 Art 2a(4). For this twin the phrase is therefore a false premise as well as a hint.

**QA-007: Fix, partly withdrawn.**
- Question leak: as for QA-006.
- Pinpoint: **no change needed.** L2 Art 25a(4) has three subparagraphs: (1) the authority disregards non-genuine practices; (2) what counts as non-genuine; (3) "For the purposes of Article 17(2), point (a), and Article 26(2a) … serious infringement". "Art 25a(4)" already covers both claims. Optional: the evidence quotes only subparagraph 1, so add subparagraph 3 if you want the "serious infringement" claim backed by evidence.
- **New:** gold_article cites "Article 2(3)". Reg 2025/2083 Art 1(1)(a) replaced that paragraph, and in L2 it now reads only "…shall not apply to goods to be moved or used in the context of military activities…". It supports nothing in the answer. Drop it, or cite the amending provision instead. The pack's suggested IDs already leave it out.

**QA-008: Keep → confirmed.** Art 1(1), Art 3(29) and Art 9(1) are verbatim in L2.

**QA-009: Relabel → confirmed.**
- Art 2(1) is verbatim.
- Annex I chemicals are only "2804 10 00 – Hydrogen", in both versions. Annex I has no chapter-29 or chapter-39 codes. Its only chapter-27 code is 2716 00 00 (electricity); there are no refinery products (2710 to 2713).
- **The pinpoint Art 30(2)(a)(iii) is confirmed** in both versions (the pack couldn't confirm the point letters).
- Recitals (34) (organic chemicals) and (35) (refinery products) are numbered correctly and exist in L1 only.
- Minor: "polymers" appears only in the review clause Art 30(2)(a)(iii). The "technical limitations" reason is given for organic chemicals and refinery products, not polymers, so the last sentence of the gold answer slightly over-attributes.

**QA-010: Relabel → confirmed, with one correction.**
- Art 1(1), Art 2(1), Art 3(6) and Art 3(7) are verbatim in L2.
- Annex III point 1 exempts goods *originating* in Switzerland. Delete that clause from the gold answer, as the pack says.
- **Correction:** UCC Art 4(1), in the original *and* the latest consolidated version (12 Dec 2022), still lists "the territory of the United Kingdom of Great Britain and Northern Ireland and of the Channel Islands and the Isle of Man". So L6 grounds Switzerland (not listed; Büsingen is carved out) but not the UK. The UK's exit comes from the Withdrawal Agreement (OJ L 29, 31.1.2020, p. 7): Art 126 ends the transition period on 31 Dec 2020, and Art 127(1) applied Union law until then. Add that, or treat the UK fact as general knowledge. Don't add L6 alone, because a RAG system reading it literally could conclude the UK is inside. The pack's Northern Ireland caveat was not checked here.

## File-wide checks

| # | Check | Result |
|---|---|---|
| 1 | Evidence word for word | **Passed.** Only the 4 formatting false alarms above. |
| 2 | Cited article applies on as_of | **1 issue:** QA-006, where Art 27 applies from 1 Jan 2026. QA-005's Art 20(1) (from 1 Feb 2027) is stated correctly in the gold answer. The pack's "When each provision applies" table matches L2 Art 36(2)(a) to (d). |
| 3 | Twin questions identical | **Passed.** QA-004 = QA-005 and QA-006 = QA-007, character for character. |
| 4 | No single-version rule in shared questions | **Found:** "ยกเว้นไฟฟ้าและไฮโดรเจน" in PAIR-2 (L2 Art 2a(4) only). Nothing found in PAIR-1. |
| 5 | gold_article names its version | **Found:** QA-004 only. |
| 6 | Corpus holds what evidence quotes | L2 has no recitals, so QA-009's Recitals 34 and 35 exist only in L1. Whether your chunker kept them can't be checked without your corpus. |
| 7 | CN codes are in Annex I | **Passed.** 7610, 3102, 7304 and 7606 are all in Annex I (both versions). 7610, 7304 and 7606 are also in Annex II; 3102 is not. |
| 8, 9 | gold_nuggets, machine-readable IDs | Editorial to-dos, not checks; not run. |

Documents: the pack's two EUR-Lex "Read (EN)" links for L1 and L2 work. The data.europa.eu ELI links were not tested, because this session can't reach that host. L4 enters into force on "the third day following" publication on 17.10.2025, which is 20 Oct 2025. The corrigenda to 2023/956 listed on EUR-Lex (R(01) to R(04)) correct only the DE, EL, NL, IT, SV and FI texts. None exists in English, so the English OJ text is final.

## Suggested edits to `High_Prompt2.json`

| Item | Field | Change |
|---|---|---|
| QA-004 | gold_article | Add "(Original 2023-05-10)". Optionally "Article 35(1)" instead of "35(1)-(2)". |
| QA-006 | gold_answer_th | Say that Art 27 applies only from 1 Jan 2026, or drop the circumvention half of the question for this twin. |
| QA-006, QA-007 | question_th | Remove "ยกเว้นไฟฟ้าและไฮโดรเจน" from both twins so they stay identical. |
| QA-007 | gold_article | Remove "Article 2(3)," (or cite Reg 2025/2083 Art 1(1)(a)). Optionally add Art 25a(4) third subparagraph to evidence_en. |
| QA-009 | category, gold_article | false_premise; Art 2(1) and Annex I (supporting: Art 30(2)(a)(iii); Recitals 34 and 35, which exist only in the original text). |
| QA-010 | category, gold_article, gold_answer_th | false_premise; Art 2(1), 3(6), 3(7). Delete the Annex III clause. Ground the UK with Withdrawal Agreement Art 126, not UCC Art 4; consider "Great Britain". |
| QA-009 | gold_answer_th (optional) | Give the "technical limitations" reason for organic chemicals (Rec. 34) and refinery products (Rec. 35); polymers are only up for review (Art 30(2)(a)(iii)). |

## Files and how to rerun

| File | What it is |
|---|---|
| `check1_evidence.py` | The pack's check-1 script, unchanged |
| `check1_diagnose.py` | Check 1 by version, with closest passage and word diff for anything not found |
| `checks_2_to_7.py` | File-wide checks 2 to 7 |
| `show.py` | Prints any provision, e.g. `python3 show.py cbam_2025-10-20.txt "Article 25a"` |
| `fetch_corpus.py` | Downloads from EUR-Lex and writes the plain-text exports |
| `cbam_2023_original.txt` | L1, CELEX 32023R0956 |
| `cbam_2025-10-20.txt` | L2, CELEX 02023R0956-20251020 |
| `reg_2025_2083.txt`, `reg_1186_2009.txt`, `ucc_952_2013_*.txt` | L4, L5, L6 (original and consolidated 2022-12-12) |

Put your `High_Prompt2.json` in this folder first. It is git-ignored, so it never gets pushed to this public repo.

```
python3 fetch_corpus.py --dl <download folder> --out .    # needs access to eur-lex.europa.eu
python3 check1_evidence.py
python3 check1_diagnose.py
python3 checks_2_to_7.py
```

How the text exports were made: block elements (paragraphs, table cells, list items) become line breaks, and inline elements are joined. The consolidated text's amendment markers (▼M1, ▼B, ►M1 … ◄) are removed, and footnote reference numbers are kept. If your corpus was exported differently (for example with markers kept), rerun check 1 on your own exports.
