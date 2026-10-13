# Glyph-by-glyph audit — 27 Hebrew letterforms (baseline → final)

Baseline findings: `round2/BASELINE_AUDIT.md`.  Final renders inspected: `round2/images/final/glyphs_Regular.png`, `glyphs_Bold.png`,
`words_*`, `confusables_pairs_*`, `running_*`.  Per-glyph before/after images: `round2/compare_glyphs/NN_name.png` (Regular and Bold,
old|new, plus words at 40 pt and 11 pt/300 dpi).  Metric = pixel similarity of letter rasters at ~10 pt (lower = more confusable;
indicative only).  Verdicts are mine, from looking at the renders; none is a quality score.

| # | Letter | Baseline defect | Changes (see CHANGELOG) | Final state / residual defect |
|---|---|---|---|---|
| 1 | א | stepped arm joins, boot foot, heavy diagonal | rebuilt: diagonal + two curved yod-like arms with heads; weight-dependent pens | Reads as alef in words. Arms still mechanical (no flared terminals); Bold heavy and dark in running text. |
| 2 | ב | corner too close to כ | square corner (R 34), larger base overhang | Good. Base overhang a plain slab. |
| 3 | ג | foot blob + kink; then (5.R2) wrong anatomy | stem to baseline + left head + diagonal leg + base slab | Canonical structure; leg and base joint is a hard polygon; foot flare is a plain wedge. |
| 4 | ד | overhang too small | overhang 46, beak, fillet, taper | Good; distinct from ר (0.32). |
| 5 | ה | ה/ח closest pair (0.165) | leg inward, gap 135, taper, fillet | No longer in the 5 closest pairs (ה/ת 0.249 now closest). Gap is subtle at 10 pt. |
| 6 | ו | read as ז; then (5.R) head on the wrong side | head overhangs left with a beak | Reads as vav; head is a small block, not a calligraphic hook. ו/ן similarity 0.279. |
| 7 | ז | too narrow / similar to ו | width 410, symmetric head | Good; distinct from ו. Roof is a flat bar (no spur). |
| 8 | ח | ok | taper, fillets, beak | Good. ח/ת 0.278 (Bold 0.201) – the closest Bold pair. |
| 9 | ט | stub hook; tick; Bold counter closed | longer curl; Bold has shorter hook | Reads as tet; Bold counter still small; top-left terminal is a plain block. |
| 10 | י | small; then (5.R) roof+stem was not a yod | comma: thick head bar + curved tail | Reads as yod but looks light and slanted next to other letters; head not tapered like a calligraphic yod. |
| 11 | ך | ok | taper/foot | Good. |
| 12 | כ | too similar to ב | R 160 | Good (ב/כ 0.297). |
| 13 | ל | boxy hook, kink, "5"-like; then bowl/tail anatomy | head overhangs left; stem ends at bowl; bowl ends in a curved tail | Canonical anatomy; head is a heavy block; tail terminal is a flat butt, not a ball. Weakest remaining Regular letter at 10 pt after מ. |
| 14 | ם | corners heavy in Bold | R 74 | Good; plain box (no top-left head). |
| 15 | מ | cap arbitrary; then wrong anatomy | tall curved belly + head + slit + foot gap + partial base | Identity ok in words; the belly is a thick mechanical arc; Bold belly merges with the head into a dark mass. Needs redraw. |
| 16 | ן | roof as wide as ך (confusable) | now ו-like head + long stem | Good; similarity to ו 0.279 (length is the main cue). |
| 17 | נ | fine | spacing only | Reads as nun; roof+slab construction, left foot a flat slab. |
| 18 | ס | looked small | +10 overshoot | Good; plain oval (no spur). |
| 19 | ע | resembled ט; then wrong anatomy | long diagonal right arm + curved left arm + base slab | Reads as ayin but "Y-like"; close to צ in construction; Bold diagonal very heavy. |
| 20 | ף | stub tongue | tongue from head; stem to descender | Canonical structure; tongue is a flat wedge; head artefact at top-left. |
| 21 | פ | stub tongue | tongue from head, base slab | As above. |
| 22 | ץ | lumpy; then wrong anatomy | "Y" with long tail | Reads as ץ; arms heavy in Bold; looks Latin-"Y"-like. |
| 23 | צ | lumpy; then wrong anatomy | stem + head, diagonal from right head, long base | Canonical structure; the stem/diagonal/base join is hard-edged; looks "K"-like at small sizes. |
| 24 | ק | fine; then (5.R2) "connected" feedback | left leg from head; roof/right curve sweeps into the leg | Structure follows the reference; the curve junction with the leg is abrupt; reads "P"-like in words. |
| 25 | ר | ok | R 170 | Good. |
| 26 | ש | flags barely visible | bigger prong flags | Good; flags are angular wedges. |
| 27 | ת | foot blob; ח/ת confusion | plain slab foot sticking out; leg inward | Good; ת/ח 0.278. |

Regular-to-Bold consistency (final): Bold uses pens 124/108 vs Regular 98/57 and ×1.08 widths; the family is consistent in
construction, but Bold א מ ע צ ץ are visibly heavier/darker than the other bold letters and Bold counters (ט, ע, מ) are tight.
