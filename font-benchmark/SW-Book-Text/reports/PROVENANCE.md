# Originality and provenance report

**Scope of claim.** Process evidence only. No legal opinion; no claim that the font is legally
independent or copyright-protected. Needs legal review before any licensing or catalog use.

## How every glyph was built
* Machine-readable per-glyph record: `reports/provenance_glyphs.json` — for each of the 172 glyphs × 2
  weights: Unicode value, construction method, generating function (file, line, SHA-256 prefix of the
  function source) and `third_party_outlines: false`.
* Summary and tool versions: `reports/provenance_summary.json` (also lists SHA-256 of each source module).
* Construction primitives (all in `src/swbook/geom.py`): rectangles/polygons with hand-typed
  coordinates, ellipses, Bézier centre-lines written by hand in `hebrew.py` / `latin.py` / `misc.py`,
  stroked with an elliptical-pen model (Skia stroker via `skia-pathops`), unioned with boolean ops.
* Hebrew letters (27) — `src/swbook/hebrew.py`, one function per letter. Latin — `latin.py`. Digits,
  punctuation, symbols and Hebrew points/dagesh — `misc.py`. Kerning — `kern.py` (computed from our own outlines).
* Letterform *structure* (e.g. a Hebrew dalet is a roof plus a right stem) is the common skeleton of the script and
  of any Hebrew typeface; shapes were drawn from general typographic knowledge, not from tracing any font.

## What was NOT done
No outline was imported, traced, extracted, transformed or derived from David CLM, Frank Ruehl CLM,
Culmus, proprietary fonts, or any other font binary. No existing font is used as a starting point.
Automated evidence: `tests/test_font.py::test_build_reads_no_foreign_font_binaries` runs the entire build under a
Python audit hook and fails if any `.ttf/.otf/.woff/.pfb/.ttc` file is opened for reading.
Limitation: this proves the build reads no font files; it cannot prove the author's memory of existing designs
did not influence shapes. A human originality/similarity review is still required.

## Tools, libraries, dependencies (versions in `provenance_summary.json`, `requirements.txt`)
Python 3.13; fontTools (compile/GPOS/tests), ufoLib2 + ufo2ft (UFO, TTF compile, feature compilation),
skia-pathops (stroking, boolean ops), uharfbuzz (shaping for specimen/tests), FontBakery, opentype-sanitizer (OTS),
freetype-py (render tests), pypdf, pypdfium2, numpy, Pillow (developer previews), pytest; poppler-utils
(`pdffonts`, `pdftotext`, `pdftoppm`) as external tools.

## Third-party assets
None. Specimen text is original prose written for this benchmark, plus public-domain Hebrew Scripture excerpts
(Genesis 1:1–5, Psalm 23:1–3) typed from memory; **the niqqud of these excerpts was not checked against a printed
edition** and needs proofreading before publication.

## Licence status
`OS/2.fsType = 2` (restricted-licence embedding) and name table ID 13 state that no production licence is assigned.
The font is not added to any production catalog.

## Round 2 addendum (reference material)
During Round 2 the user supplied two PDF pages of Hebrew text as examples of professional typography (and named a font, "Livorna", that was not available and was never viewed). Their renders and enlarged letter crops were looked at to correct letter anatomy, proportions, weight and spacing; the crops stayed in the session scratch directory and are not in the repository. No outline, bitmap or measurement from them was imported into the build, and the build still opens no font file (automated test). Nevertheless the letter structure of several glyphs (ו ל מ פ ף ע צ ץ ק ג ן י) was revised after seeing that reference, so the clean-room statement above no longer holds for Round 2 and a human originality/legal review is required.
