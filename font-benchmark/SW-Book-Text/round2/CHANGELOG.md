# Round 2 change log (every decision, with the evidence image inspected)

Method: build to `round2/work/` → `tools/cmp.py` (OLD = last accepted fonts, NEW = trial fonts, enlarged cells + words at 40 pt and
11 pt/300 dpi, Regular and Bold) → I looked at the image → accept or revert.  Frozen material: `specimen/texts.py`, page geometry,
sizes and layout code are byte-identical to Round 1 (`git diff 2f25372 HEAD -- specimen` shows only the PDF binary changed) and
`tools/audit_text.py` (word lists, pairs, running text) was not edited.  All renders come from the compiled TTFs.
"Evidence" paths are relative to `round2/images/`.

## Pass 1 — fundamental construction and recognizability
| # | Glyph | Defect (baseline audit) | Modification | Evidence | Decision |
|---|---|---|---|---|---|
| 1.1 | ו / ז | ו read as ז at 10 pt ("והשורות" looked like "זהשורות"): one-sided 70-unit tab vs. 330-unit symmetric roof | vav head slimmed to a 40-unit tab with a small beak; zayin widened to 410 and kept symmetric | `p1/a_vav_zayin_tav_gimel_alef.png` (words rows) | accepted — **later superseded** (see 5.R: head belongs on the left) |
| 1.2 | ת | left foot a wedge/blob, not distinct from ח | removed stem flare, plain slab foot | same image | accepted; foot length changed again in 5.4 |
| 1.3 | ג | foot blob, kink at the leg joint | straight parallelogram leg + clean base slab | same image | accepted — **superseded** in 5.R (wrong anatomy) |
| 1.4 | א | stepped arm joins, boot-like foot | rebuilt as diagonal + two stroked arms | same image | **partly rejected**: Bold became an "X"-like mass |
| 1.5 | א | (1.4 fix) arms too heavy / aligned with the diagonal → read as Latin X | pen widths made weight-dependent (`46+0.5V`); arms as yod-like slant+vertical | `p1/c_alef_weight.png` (rejected: still X-like), `p1/c_alef_weight2.png` (accepted) | second attempt accepted |
| 1.6 | ל | kink at stem/bowl junction, boxy hook, "5"-like | stem shortened below the bowl, beak on hook, foot chisel integrated | `p1/b_lamed_tet_ayin_tsadi.png` | accepted — superseded in 5.R |
| 1.7 | ט | inner hook a stub; spurious top-left tick | hook lengthened into a curl; flat stem top | same | accepted |
| 1.8 | ע | resembled ט (both "cups") | left arm made a straight diagonal | same | accepted — superseded in 5.R |
| 1.9 | צ ץ | lumpy arm/base junction | single diagonal replaces crossing curves | same | accepted (images show cleaner) — superseded in 5.R |
| 1.10 | ב כ ד ר ה פ | similarity ב/כ 0.20, ד/ר 0.24, ה/ח 0.165 | ב corner R 70→34, כ R 120→160, ד overhang 30→46, ר R 130→170, ה leg moved inward + gap 135, פ tongue lengthened | `p1/d_confusables.png` | accepted; similarity ה/ח no longer in the closest-pair list |

## Pass 2 — proportions, curves, consistency
| 2.1 | stems | wedge-flare feet look like blobs; no entasis | `stem()`: slight taper + concave bracket foot; `fillet()` at roof/stem inner corners (ד ה ח ת ז) | `p2_a_stems.png` | accepted |
| 2.2 | weight | strokes too uniform | Regular pen 80/50 → 84/44 | `p2_b_weight.png` (11 pt running) | accepted, **later replaced** (5.7) |
| 2.3 | ס ט ע | round letters look small next to flat ones | +10 unit overshoot (ס both ends; ט, ע bottoms) | `p2_c_round_shin_yod.png` | accepted |
| 2.4 | ש | flags barely visible | prong flags enlarged (1.1V → 1.9V) | same | accepted |
| 2.5 | י | too small | stem lengthened to 0.36T | same | accepted — superseded in 5.R |
| 2.6 | צ ץ מ ם | arm/base clutter; mem cap flag arbitrary; ם corners heavy | thinner diagonal, shorter tail; flag removed; R 60→74 | `p2_d_tsadi_mem.png` | accepted |

## Pass 3 — spacing, kerning, word rhythm
| 3.1 | all Hebrew | rule-based sidebearings, uneven colour/gaps | optical sidebearings (`src/swbook/spacing.py`): sb moves against measured side depth | `p3_a_spacing.png`; σ of mean clearance 20.0 → 10.9 (Regular) | accepted (σ is a proxy; I also looked at the running text) |
| 3.2 | Latin | looser than Hebrew | same optical method for Latin | `latin_pass3_try.png` vs `latin_pass3_start.png` — no visible change | **reverted** (identical TTF bytes to the accepted font verified) |
| 3.3 | ד ה ח ת | no family serif detail | small beak at roof right end | `p3_b_beak.png` | accepted (visible only enlarged; neutral at 11 pt) |

## Pass 4 — Bold and mark positioning
| 4.1 | marks | dots 56 units: barely visible at 9 pt | mark radius 28→32 (Bold 38→42), `below_off` scales with it | `p4_a_marks.png`; tests: no mark/base overlaps | accepted |
| 4.2 | Bold ט | counter closed up by the hook, heavy tab | hook shorter in Bold, no tab | `p4_b_bold_tet.png` | accepted |

## Pass 5 — full-page typography and regression correction
| 5.1 | § | looked like "S" in citations | two stacked small S shapes | `p5_a_section.png` | accepted (still small) |
| 5.2 | א | colour spot in running text (heavier than neighbours) | diagonal/arm pens lighter | `p5_b_alef.png` | accepted |
| 5.3 | f + ascenders | test caught near-touching `fb fh fl` after height change | f rsb −8 → 14 | `latin_final.png`; tests pass | accepted |
| 5.4 | ת | ח/ת similarity 0.235 (Bold 0.155) | left leg moved inward, foot sticks out | `p5_c_tav.png`; ת/ח 0.345 / 0.235 | accepted |
| 5.5 | Hebrew height | **reference review (user-supplied serif page): letters too short/airy at the same point size** | letter height 650→715, lamed 800→880, descender −230→−250; Latin cap/x/asc 650/440/700 → 700/470/745 | `p5_d_height.png` (10 pt) | accepted |
| 5.6 | spacing | still airy vs. the reference | base sidebearing 64→50, word space 250→215, kern target 112→100, optical α .55→.75 | `p5_e_spacing.png`, `p5_f_alpha75.png` | accepted (σ clearance 14.2; no pair < 20 units) |
| 5.7 | weight | **text too light/wiry vs. reference** | Hebrew Regular pen 84/44 → 98/57, Bold 108/94 → 124/108; Latin 92/32 and 126/44 | `p5_g_weight.png` | accepted |
| 5.R | ו ן י ל מ פ ף ע א צ ץ | **user: "broken"; reference alphabet shows canonical anatomy** — heads overhang LEFT (ו ן ל ע צ), ל bowl ends in a curled tail, מ has a tall curved belly + slit + foot gap, פ tongue curls in from the top-left head, ע diagonal right arm + curved left arm, י comma, צ stem+diagonal+base, ץ "Y" with long tail | all rebuilt (`hebrew.py`) | `p6_a.png`, `p6_b.png`, `p6_c.png` (first attempt: מ read as "כ(" → belly thickened, slit narrowed), `p6try/glyphs_Regular.png` | accepted after one rejected מ/ע iteration |
| 5.R2 | ג ק | **user: "ג is off", "ק is connected"** | ג = stem to baseline + left head + diagonal leg + base; ק = left leg from a top-left head, roof/right curve sweeps back into the leg | `p7_a.png`, `p7_alphabet_line.png` | accepted |
| 5.8 | tests | mark/base collisions after redesigns (ה ג ע צ ץ י ן dagesh/hataf anchors); sidebearing test obsolete | anchors moved to free regions; `below` offset sign fixed for ן; the sidebearing test now checks *optical* consistency (σ ≤ 14; measured 7–9) | `reports/test_results.txt` | accepted |

Rejected / superseded work is kept in this log on purpose: items 1.4 (X-like alef), 3.2 (Latin optical spacing) and the first מ/ע attempts.
