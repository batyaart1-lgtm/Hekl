# Round 2 — baseline audit (Round-1 prototype, commit 2f25372)

Frozen copies: `baseline_round1/` (fonts, UFO sources, generator source, specimen PDF, manifest SHA-256).
Renders inspected: `round2/images/baseline/` — enlarged glyph sheets (`glyphs_Regular|Bold.png`), per-letter word strips
(`words_*`), confusables/pairs (`confusables_pairs_*`), running text at 10–13 pt/300 dpi (`running_*`), specimen pages (`page-*.png`).
Measurements: `round2/images/baseline/summary.json`.

Objective diagnostics (indicative only, **not a quality score**): pixel-similarity of letter rasters at ~10 pt/300 dpi
(lower = more confusable): baseline Regular closest pairs ה/ח 0.165, ב/כ 0.202, ח/ת 0.215, ד/ר 0.241, ץ/צ 0.293;
Bold: ה/ח 0.130, ח/ת 0.156, ב/כ 0.161, ד/ר 0.189, ו/ז 0.189. Optical clearance between neighbours: mean 196 units,
σ = 21 (Regular), 22 (Bold); no pair collides (< 20 units).
Visual finding from the running-text strips: **ו is read as ז in 10 pt text** ("והשורות" looks like "זהשורות") — the numeric metric did not
flag this for Regular, the eye did. This is exactly the kind of judgement the numbers cannot replace.

## Glyph-by-glyph defects (Regular; Bold checked separately where noted)

| # | Letter | Specific defects observed | Likely geometric cause |
|---|---|---|---|
| 1 | א alef | Upper-right arm meets the diagonal with a stepped, jagged corner; lower-left arm ends in a notched "boot" (stem + base slab with a visible step); diagonal is lighter than the two arms' visual weight | arms are separate strokes unioned at hard angles; foot = stem + `base()` slab at different x |
| 2 | ב bet | Acceptable. Top-right corner radius (70) too close to kaf's (120) → ב/כ similarity 0.20; bottom-right spur wedge nearly invisible | corner radii nearly equal, tiny spur |
| 3 | ג gimel | Foot is a dark blob where leg, base slab and chisel meet; leg joins the right stem with a kink at ≈0.44T; leg heavier than stem | leg stroked with (1.15V, 0.8H) pen, base slab overlaps |
| 4 | ד dalet | Fine. Right overhang only 30 units → at 10 pt it differs from resh by corner only (similarity 0.24) | overhang too small |
| 5 | ה he | Distinguishable from ח only by the 120-unit gap (similarity 0.165 – the closest pair); left leg bottom flare is heavy | gap is small relative to H |
| 6 | ו vav | **Head is a one-sided flag (stem + 70-unit tab) and reads as ז at small sizes**; vav (adv 302) and zayin (454) differ mostly by width | tab too wide, zayin roof not distinct enough |
| 7 | ז zayin | Symmetric roof is correct but only 330 wide; stem right of centre; sits too close to vav in shape | width/roof proportion |
| 8 | ח het | OK. Strong rhythm with ת; left leg and right leg identical flares | – |
| 9 | ט tet | Inner hook is a stub (≈120 units) that does not read as the curl of ט; spurious tick at top-left of the left stem looks like dirt; Bold counter too small | hook path too short; `left_cap` polygon |
| 10 | י yod | Reads well; slightly small (stem stops at 0.46T) | – |
| 11 | ך final kaf | Good. Descender flare fine | – |
| 12 | כ kaf | Fine; top-left and bottom-left chisels fine | – |
| 13 | ל lamed | Ascender hook is a boxy rectangle; visible kink where stem meets bowl on the left; bottom-left "foot" bar looks detached → shape reads like numeral 5 | stem + `pen` bowl + `base()` slab unioned without blending |
| 14 | ם final mem | Fine (closed box); slightly heavy at corners in Bold | – |
| 15 | מ mem | Distinct from ם thanks to open top-left, but cap flag looks arbitrary; right roof junction ok | – |
| 16 | ן final nun | Fine | – |
| 17 | נ nun | Fine; short roof vs kaf distinct | – |
| 18 | ס samekh | Fine; no overshoot (round letters look slightly small next to flat ones) | no optical overshoot |
| 19 | ע ayin | U-shape plus slanted left arm resembles ט (tet): both look like a cup at 10 pt; left arm top has a chisel cap but no horn | left arm too short/steep, shared bowl |
| 20 | ף final pe | Tongue is a small stub; otherwise fine | tongue path short |
| 21 | פ pe | as above | – |
| 22 | ץ final tsadi | Junction of arm and base is lumpy/notched; arm crosses the left bowl; descender attaches below a kink | two curves cross at a shallow angle |
| 23 | צ tsadi | same as 22; base tail ends in a flat slab | same |
| 24 | ק qof | Fine; right arm foot has a small wedge; similar to ך at small size (0.33) but acceptable | – |
| 25 | ר resh | Fine; corner radius 130 | – |
| 26 | ש shin | Good; prong flags barely visible | – |
| 27 | ת tav | Left foot is a wedge/blob (stem flare + base slab overlap) and not distinct from ח at 10 pt | `base()` + `stem()` flare overlap |

Regular-to-Bold consistency: Bold uses H 108/V 94 (Regular 80/50): vertical stems nearly double, horizontals ×1.35, so Bold loses the
horizontal-stress contrast (acceptable for a bold, but Bold ט/ס/ע counters are tight and Bold mem/final mem corners are heavy).

## Context findings (running text, words, pairs)
* ו/ז confusion (above). ל looks spiky ("5-like") in running text. Round letters (ס ט ע) look lighter than flat letters (ח ת ה) → uneven colour.
* Word spaces (250 units) look slightly wide against tight letter spacing in 10 pt lines; comma/period fine.
* No collisions; open-sided letters (ל, ר, ד after ל) leave gaps that look like holes: spacing is rule-based.
* Glyph-outline vs spacing: ו/ז, ל, ת, ג, צ are **outline** defects; colour unevenness and gaps are **spacing** defects (Pass 3).
