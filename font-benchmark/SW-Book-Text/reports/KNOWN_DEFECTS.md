> **Round-1 list.** Round 2 superseded parts of it (letter anatomy, weights, spacing, marks). Current status: `round2/ROUND2_REPORT.md` and `round2/GLYPH_AUDIT.md`.

# Known defects, limitations and items needing human visual review

Honest status: this is a **working but unpolished prototype**, not a professional-quality typeface. Passing the
automated tests proves technical validity, not design quality.

## Design defects (visible)
1. **Letterform refinement is basic.** Curves are elliptical-pen strokes with round-ish joins; there is no optical
   correction, no stroke modulation inside letters, no ink traps, and terminals are generic chiselled/flat cuts. The
   result reads as a clean geometric-calligraphic serif, not as a finished book face.
2. **Weak glyphs** (need redrawing by a type designer): tsadi/final tsadi (junction of arm and base is clumsy), lamed
   (hook proportions), tet (inner hook), gimel (leg), alef (arms too light vs. diagonal), pe/final pe (tongue small),
   mem (distinguished from final mem mainly by the open top-left; real mem construction differs).
3. **Similar pairs at 10 pt:** he/het, dalet/resh, vav/final nun, samekh/final mem rely on small details; he/het
   differ by a 120-unit gap which is subtle at 10 pt.
4. **Latin** is a basic text serif: `a`, `g`, `s`, `t`, `u` and capitals `S`, `J`, `G` need refinement; § is a plain S
   (single contour); `@`, `&`, `%`, `$` are rough constructions; bold Latin counters are tight in `a e s`.
5. **Bold** is produced by pen/width parameters of the same skeletons — not individually optically adjusted;
   Bold Hebrew `tet`, `samekh`, `ayin` counters are small.
6. **Spacing/kerning** are rule-based (sidebearing table + `kern.py` optical pairs). No hand-tuned class kerning;
   Hebrew–Latin boundary spacing and digit/punctuation kerning not tuned. Human review needed on page 2 (10–13 pt).
7. Hebrew punctuation (geresh, gershayim, maqaf) are simple polygons; maqaf height/length not tuned against niqqud.
8. Mark stacking: only single mark per class per base is positioned (e.g. holam + shin dot works; two below-marks on
   one base, cantillation marks (U+0591–05AF), and mark-to-mark are **not** implemented. Holam haser/vav conventions
   (vav+holam as one glyph) not implemented — holam sits above the vav stem.
9. Not implemented: Hebrew cantillation, presentation forms U+FB1D–FB4F, `ccmp` composition, ligatures, other
   Hebrew-block symbols (U+05C4–05C6, U+05F0–05F2), Latin accents, ligatures, small caps, figures variants,
   italics, TrueType hinting (ttfautohint not available; unhinted + smart-dropout `prep` + gasp).
10. OTF/CFF output not produced (TTF only).

## Technical limitations of the tooling
* FontBakery `check-universal`: 0 FAIL, 3 WARN (contour_count for `at`, `section`; overlapping_path_segments on
  Regular). `check-opentype`: 0 FAIL/WARN. Google Fonts/Adobe profiles and network checks were **not** run.
* Specimen PDF is produced by a custom PDF writer (full font embedding, ToUnicode, no tagging/PDF-UA, not PDF/X).
  Extracted text order for Hebrew is visual, not logical (per-glyph positioning). Bidi is a UAX#9 subset
  (no explicit embeddings/isolates, no number-separator subtleties). Greedy line breaking, no hyphenation (n/a for
  Hebrew), no widow/orphan control; page 3 columns balanced by text length only.
* Scripture niqqud in the specimen was typed from memory and must be proofread.
* No colour/ICC, bleed or crop marks: not a press-ready PDF.

## Human visual review required (print and screen)
- [ ] Specimen p.1: all 27 forms, weight rhythm Regular vs Bold, digit/punctuation shapes.
- [ ] p.2: colour (evenness) of text at 10/11/12/13 pt printed, he/het, dalet/resh discrimination, word spaces (250 units).
- [ ] p.3: two-column justified rivers, bold run-in openings, heading hierarchy, gutter.
- [ ] p.4: every vowel/dagesh/dot position; collision of sheva/hataf with neighbouring letters; shin+holam+dagesh stack;
      marks under final letters (ךְ ךָ ףּ); small-size mark clarity at 9 pt.
- [ ] p.5: mixed-direction ordering of parentheses, numbers, citations, URLs/paths; Latin/Hebrew size and colour match.
- [ ] p.6: Regular/Bold contrast and width change; whether Bold counters close up.
- [ ] Glyph-level: tsadi, lamed, tet, gimel, mem, alef, qof, final pe (see item 2); Latin `a g s t u S G J @ & % $ §`.
- [ ] Kerning/spacing in running text; hinting/rendering on Windows GDI (unhinted font).
- [ ] Originality/similarity review and legal review (see PROVENANCE.md).
