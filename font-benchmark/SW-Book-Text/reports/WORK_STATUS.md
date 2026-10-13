# Work completed vs incomplete

## Complete (verified by executed commands; see `test_results.txt`)
| Deliverable | Status | Path |
|---|---|---|
| Regular TTF | done | `fonts/SWBookText-Regular.ttf` |
| Bold TTF | done | `fonts/SWBookText-Bold.ttf` |
| ≥27 original Hebrew letterforms (22 + 5 finals) | done (quality: basic, see KNOWN_DEFECTS) | `src/swbook/hebrew.py` |
| Hebrew punctuation (geresh, gershayim, maqaf, paseq, sof pasuq) | done | `src/swbook/misc.py` |
| Niqqud + dagesh + shin/sin dots, rafe, meteg (18 marks) | done, GPOS mark-to-base | `misc.py`, `build.py` |
| Digits 0–9, ASCII punctuation, extra symbols, Latin A–Z a–z | done | `latin.py`, `misc.py` |
| OpenType features | `mark`, `kern`, GDEF | `sources/*.ufo/features.fea` |
| Editable source | UFO3 + Python generators | `sources/`, `src/` |
| Reproducible build | done (hash-compared twice) | `src/swbook/build.py`, `tools/run_all.sh` |
| Coverage report (machine-readable) | done | `reports/glyph_coverage.json` |
| 6-page PDF specimen (fonts embedded) | done | `specimen/SWBookText-Specimen.pdf` |
| Tests (fonts + PDF) | 68 pytest tests pass | `tests/` |
| Provenance report | done | `reports/PROVENANCE.md`, `provenance_*.json` |
| Known defects / human-review list | done | `reports/KNOWN_DEFECTS.md` |

## Incomplete / not done
OTF (CFF) build; hinting; cantillation; presentation forms; italics; GF/Adobe FontBakery profiles; press-ready PDF;
professional-grade glyph refinement; proofreading of Scripture niqqud; legal/originality review.

## Validation results (final run; exact log in `reports/test_results.txt`)
* `pytest tests -v`: 68 passed (font tests ×2 weights + PDF tests).
* `fontbakery check-universal --skip-network` on both fonts: FAIL 0, WARN 3, PASS 149.
* `fontbakery check-opentype --skip-network`: FAIL 0, WARN 0, PASS 63.
* OTS (`python3 -m ots`): both fonts sanitised successfully.
* `pdffonts`: SWBookText-Regular and -Bold, CID TrueType, embedded, ToUnicode present; 6 pages, A4.
* Reproducibility: two fresh builds in temp dirs give identical SHA-256 for both TTFs and the PDF.

## Time and cost
Wall-clock: approx. 30 minutes of agent session (10:39 → ~11:10 UTC, 2026-10-13); tool runtime of `tools/run_all.sh`
≈ 20 s. Model/API cost: not available to the agent in this environment (no usage data exposed).

## Process notes
* Work is confined to `font-benchmark/SW-Book-Text/`; no other repository file was touched.
* Per the brief ("do not commit, push … without explicit authorization") **nothing was committed or pushed**; the
  working tree on branch `claude/practical-keller-o8kn3j` holds the uncommitted new directory.
* Packages were installed with `pip` into the container (fonttools, ufo2ft, uharfbuzz, fontbakery, …); no paid service used.

## Round 2
See `round2/ROUND2_REPORT.md`. Fonts/PDF/tests were regenerated: pytest 68 passed, FontBakery universal 0 FAIL/3 WARN, opentype 0 FAIL/0 WARN, OTS ok, builds reproducible. Not committed/pushed beyond local commits per the Round-2 instruction.
