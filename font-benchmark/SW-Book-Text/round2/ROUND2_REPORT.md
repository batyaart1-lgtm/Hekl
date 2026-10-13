# SW Book Text — Round 2 report (iterative glyph refinement)

## What was done
Baseline frozen → audited → five passes of focused changes, each rendered and inspected → full-page comparison.
Per-pass logs: `round2/CHANGELOG.md`.  Glyph audit: `round2/GLYPH_AUDIT.md`.  Baseline audit: `round2/BASELINE_AUDIT.md`.

## Deliverables (paths relative to `font-benchmark/SW-Book-Text/`)
1. Revised fonts: `fonts/SWBookText-Regular.ttf`, `fonts/SWBookText-Bold.ttf` (172 glyphs each).
2. Sources and builds: `src/swbook/*` (generators), `sources/*.ufo` (regenerated UFOs), `tools/run_all.sh`; new: `src/swbook/spacing.py`.
3. Glyph-by-glyph audit: `round2/GLYPH_AUDIT.md`.
4. Before/after images for every Hebrew letter (all 27 were modified): `round2/compare_glyphs/01_alef.png … 27_tav.png`.
5. Before/after PDFs: `round2/specimen_before.pdf` (Round-1 fonts) and `round2/specimen_after.pdf`; page composites `round2/compare_pages/pageN_before_after.png`.
   The frozen specimen sources are unchanged (git shows only the PDF binary differing); both PDFs embed only SW Book Text (`pdffonts`), so no fallback font is involved.
6. Per-pass defect/correction logs: `round2/CHANGELOG.md`.
7. Technical validation: `reports/test_results.txt` (final run: pytest 68 passed; FontBakery `check-universal` 0 FAIL / 3 WARN / 149 PASS;
   `check-opentype` 0 FAIL / 0 WARN / 63 PASS; OTS accepts both fonts; two fresh builds give identical SHA-256 for fonts and PDF).
8. Unresolved defects: below and `round2/GLYPH_AUDIT.md`.
9. Snapshots for each stage: `round2/images/{baseline,pass1,pass3,final}/` (summary.json holds metrics); baseline files: `baseline_round1/` (+ `MANIFEST.sha256`, commit id).

## Measured differences, baseline → final (indicative proxies, not quality scores)
* Closest letter pairs by raster similarity, Regular: ה/ח 0.165, ב/כ 0.202, ח/ת 0.215, ד/ר 0.241 → ה/ת 0.249, ח/ת 0.278, ו/ן 0.279, ב/כ 0.297, ד/ר 0.324.
  Bold: ה/ח 0.130, ח/ת 0.156 → ח/ת 0.201, ה/ת 0.222.  Every confusable pair got further apart; no pair is now below 0.20.
* σ of mean optical clearance between neighbours: 21.0 → 13.1 (Regular), 21.7 → 15.6 (Bold); no pair collides (< 20 units).
* Ink density of the 27 letters: 0.279 → 0.323 (Regular), 0.405 → 0.450 (Bold); letter height 650 → 715 units; mean advance 609 → 592.
These numbers were useful guides (e.g. they exposed nothing about ו/ז, which I found only by looking at 10 pt text) and are **not** evidence of quality.

## Iteration counts and time
* Five passes were run, each with several focused corrections.  About 30 trial builds were rendered and inspected (exact count was not logged);
  rejected or reverted: alef v1 (X-like), Latin optical spacing (no visible gain), first מ and ע redraws.
* Wall-clock for Round 2: baseline freeze at 11:15 UTC, last full validation ≈ 11:50 UTC (~37 min of agent time, plus ~5 min writing this documentation).
* API/model cost: not available in this environment.

## Reference material and originality (important)
Mid-round the user supplied two PDFs of Hebrew pages as examples of professional typography.  I **looked at their renders** (and enlarged
letter crops, kept only in the session scratch directory, not in the repository) to correct letter anatomy, proportions, weight and spacing.
No outline, bitmap or measurement was imported into the build (build still reads no font file: `test_build_reads_no_foreign_font_binaries` passes),
and every outline in the font is still generated from my own centre-lines and polygons.  But the *structure* of letters such as ו ל מ פ ע צ ץ ק was
revised after seeing that reference, so this is **no longer a clean-room design** and the originality statement in `reports/PROVENANCE.md` is weakened
accordingly.  The user also mentioned a font called "Livorna" which is not installed here and which I never saw.  Legal/originality review must take this into account.

## Unresolved typography defects (honest list)
* The letters now follow canonical anatomy, but their drawing is still mechanical: elliptical-pen arcs, straight chiselled terminals, no flared or ball terminals,
  no stroke modulation inside curves, simplified "heads" (blocks instead of calligraphic hooks).  Side by side with the reference page the font looks
  like a geometric imitation of a book serif.
* Weakest letters (see GLYPH_AUDIT): מ (belly), ל (head, tail), צ/ץ (hard joins, "K"/"Y" look), ע (Y-like), י (light comma), ק/ג (abrupt joins), פ/ף (flat tongue).
* Bold is a parametric thickening; Bold א מ ע צ ץ are visibly heavy and some bold counters are tight.
* Latin companion is untouched in design: quirky `a g s t u`, uneven widths, rough `@ & % $`, small `§`.
* Spacing is rule-based (optical depth formula + algorithmic kerning); there is no designer-tuned kerning, no digit/punctuation kerning, no Hebrew-Latin boundary tuning.
* Marks: dagesh anchors for ע צ ץ י ו ן are compromises; two marks of the same class on one base and cantillation are unsupported; mark sizes were tuned only by eye on the specimen.
* Specimen engine limits unchanged (UAX#9 subset, greedy justification gives wide gaps in short mixed lines on page 5), and Scripture niqqud is unproofed.
* No hinting; OTF not built; Google/Adobe FontBakery profiles not run.

## Candid assessment
Round 2 made the font **clearly better than Round 1**: letters are now the standard Hebrew letters (several were wrong before), running text is darker,
denser and more even, confusable letters are better separated, and marks are visible.  It is **not suitable for professional book printing as it stands**.
At 10–11 pt body size, pages read as Hebrew text with a consistent texture, but at display sizes and in careful proofing the letter drawing,
terminals, Bold and Latin would be rejected by a typographer, and spacing/kerning/hinting are unfinished.  It is a reasonable *starting skeleton*
(reproducible build, working GPOS marks, tests, tooling) for a type designer to redraw glyph by glyph, not a finished typeface.
