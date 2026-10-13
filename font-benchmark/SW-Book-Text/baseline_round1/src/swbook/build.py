"""Build SW Book Text (Regular + Bold): construction scripts -> UFO -> TTF.

Usage:  python -m swbook.build [--out DIR]   (run from the src/ directory)
Deterministic: no randomness, fixed timestamps (SOURCE_DATE_EPOCH).
"""
import os
import sys
import json
import inspect
import hashlib
import argparse

import ufoLib2 as ufolib2
import ufo2ft
from fontTools.agl import UV2AGL
from pathops import Path

from .geom import Shape, xform
from . import hebrew, latin, misc
from .hebrew import HCtx
from .latin import LCtx
from .kern import optical_kerns

FAMILY = "SW Book Text — Benchmark Prototype"
UPM = 1000
EPOCH = 1767225600  # 2026-01-01T00:00:00Z, fixed for reproducibility

WEIGHTS = {
    # Hebrew pen (H = horizontal-stroke thickness, V = vertical-stem thickness,
    # wf = width factor), Latin pen (a = stem, b = hairline, wf)
    "Regular": dict(heb=(80, 50, 1.00), lat=(84, 30, 1.00), wght=400),
    "Bold": dict(heb=(108, 94, 1.08), lat=(118, 42, 1.06), wght=700),
}

HEB_SB = {  # (lsb, rsb) overrides, Regular values; Bold shrinks by 8 %
    0x05D0: (46, 46), 0x05D5: (74, 74), 0x05D6: (62, 62), 0x05D9: (76, 76),
    0x05DC: (58, 56), 0x05DD: (58, 58), 0x05E1: (54, 54), 0x05E2: (52, 52),
    0x05E9: (52, 52), 0x05E6: (56, 56), 0x05D8: (56, 56), 0x05D2: (60, 56),
}
HEB_SB_DEFAULT = (66, 66)

LAT_SB = {}
for ch in "CGOQS":
    LAT_SB[ch] = (44, 44)
for ch in "AVWXY":
    LAT_SB[ch] = (10, 10)
LAT_SB.update({"T": (18, 18), "L": (34, 14), "J": (14, 40), "I": (40, 40), "Z": (30, 30), "P": (34, 26),
               "F": (34, 22), "E": (34, 24), "K": (34, 14), "R": (34, 14), "B": (34, 34), "D": (34, 40),
               "U": (22, 36), "H": (34, 34), "M": (28, 28), "N": (28, 28)})
for ch in "oces":
    LAT_SB[ch] = (36, 34)
for ch in "vwxy":
    LAT_SB[ch] = (10, 10)
LAT_SB.update({"a": (30, 22), "f": (10, -8), "t": (10, 22), "r": (20, 4), "j": (14, 24), "g": (28, 20),
               "z": (24, 24), "i": (26, 26), "l": (26, 26), "k": (22, 12), "b": (22, 34), "d": (34, 22),
               "p": (22, 34), "q": (34, 22), "u": (22, 22)})
LAT_SB_DEFAULT_U, LAT_SB_DEFAULT_L = (34, 34), (22, 22)

NAMES_HEB = hebrew.GLYPHS
MARK_NAMES = {
    0x05B0: "sheva", 0x05B1: "hatafsegol", 0x05B2: "hatafpatah", 0x05B3: "hatafqamats",
    0x05B4: "hiriq", 0x05B5: "tsere", 0x05B6: "segol", 0x05B7: "patah", 0x05B8: "qamats",
    0x05B9: "holam", 0x05BA: "holamhaser", 0x05BB: "qubuts", 0x05BC: "dagesh", 0x05BD: "meteg",
    0x05BF: "rafe", 0x05C1: "shindot", 0x05C2: "sindot", 0x05C7: "qamatsqatan",
}
HEB_PUNCT = {0x05BE: "maqaf", 0x05F3: "geresh", 0x05F4: "gershayim", 0x05C0: "paseq", 0x05C3: "sofpasuq"}
DIGIT_NAMES = "zero one two three four five six seven eight nine".split()
PUNCT = list("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~") + [
    "–", "—", "‘", "’", "“", "”", "„", "…", "•", "«", "»",
    "·", "§", "¶", "°", "©", "±", "×", "÷", "−", "₪"]


def gname(cp):
    if cp in UV2AGL and cp < 0x2100:
        return UV2AGL[cp]
    return "uni%04X" % cp


def drop_slivers(p, min_area=400.0):
    """Remove numerically degenerate contours left behind by boolean operations."""
    q = Path()
    for c in p.contours:
        if abs(c.area) >= min_area:
            q.addPath(c)
    return q


def make_notdef(hc):
    s = Shape()
    from .geom import rect
    s.add(rect(60, 0, 540, 700)).sub(rect(60 + 50, 50, 540 - 50, 700 - 50))
    return s


def build_weight(wname, outdir):
    P = WEIGHTS[wname]
    hc = HCtx(*P["heb"], wname)
    lc = LCtx(*P["lat"], wname)
    sbscale = 1.0 if wname == "Regular" else 0.92

    ufo = ufolib2.Font()
    glyphs = []     # (name, unicodes, kind, shape/None, adv, anchors, provenance)
    prov = []
    anchors = {}

    def src(fn):
        try:
            lines, start = inspect.getsourcelines(fn)
            text = "".join(lines)
            return dict(function="%s.%s" % (fn.__module__.split('.')[-1], fn.__name__),
                        file="src/swbook/%s.py" % fn.__module__.split('.')[-1],
                        line=start, source_sha256=hashlib.sha256(text.encode()).hexdigest()[:16])
        except Exception:
            return dict(function=str(fn))

    entries = []

    def add(name, cps, kind, shape, adv=None, lsb=0, rsb=0, anc=None, fn=None, method=""):
        entries.append(dict(name=name, cps=cps, kind=kind, shape=shape, adv=adv, lsb=lsb, rsb=rsb,
                            anc=anc or {}, fn=fn, method=method))

    # .notdef, space-like
    add(".notdef", [], "base", make_notdef(hc), adv=600, lsb=0, rsb=0,
        fn=make_notdef, method="rectangle frame (polygon difference)")
    add("space", [0x20], "space", Shape(), adv=250)
    add("uni00A0", [0xA0], "space", Shape(), adv=250)
    for cp, nm in ((0x200C, "uni200C"), (0x200D, "uni200D"), (0x200E, "uni200E"), (0x200F, "uni200F")):
        add(nm, [cp], "space", Shape(), adv=0)

    # Hebrew letters
    T = hc.T
    for cp, (nm, fn) in NAMES_HEB.items():
        shape, inf = fn(hc)
        l, r = HEB_SB.get(cp, HEB_SB_DEFAULT)
        l, r = l * sbscale, r * sbscale
        xmin = inf["xmin"]
        w = inf["xmax"] - xmin
        xc = xmin + w / 2
        ytop = hc.ASC if cp == 0x05DC else T
        anc = {
            "below": inf.get("below", (xc if "below_x" not in inf else inf["below_x"], -22)),
            "belowW": inf.get("belowW", (xc if "below_x" not in inf else inf["below_x"], -22)),
            "inside": inf.get("inside", (xc, T * 0.45)),
            "hol": inf.get("hol", (xc if w < 320 else xmin + w * 0.24, ytop + 36)),
            "dotR": inf.get("dot_r", (xc if w < 320 else xmin + w * 0.72, ytop + 40)),
            "dotL": inf.get("dot_l", (xc if w < 320 else xmin + w * 0.30, ytop + 40)),
            "rafe": (xc, ytop + 26),
        }
        if "below" in inf and len(inf["below"]) == 2 and inf["below"][1] == -110:
            pass
        add(nm, [cp], "base", shape, lsb=l, rsb=r, anc={k: (v[0] - xmin + l, v[1]) for k, v in anc.items()},
            fn=fn, method="elliptical-pen strokes + chiselled polygons (hebrew.py)")

    # Hebrew punctuation
    for cp, nm in HEB_PUNCT.items():
        shape, inf = misc.heb_punct(hc, cp)
        l, r = (36, 36) if cp != 0x05C3 else (60, 40)
        if cp in (0x05F3, 0x05F4):
            l, r = (46, 30)
        add(nm, [cp], "base", shape, lsb=l, rsb=r, fn=misc.heb_punct, method="polygons/circles (misc.py)")

    # Hebrew marks
    for cp, nm in MARK_NAMES.items():
        shape, kind = misc.mk(hc, cp)
        add(nm, [cp], "mark", shape, adv=0, anc={"kind": kind}, fn=misc.mk,
            method="dots/bars from circle & rectangle primitives (misc.py)")

    # Latin
    for ch, fn in latin.UPPER.items():
        shape, inf = fn(lc)
        l, r = LAT_SB.get(ch, LAT_SB_DEFAULT_U)
        add(ch, [ord(ch)], "base", shape, lsb=l * sbscale, rsb=r * sbscale, fn=fn,
            method="elliptical-pen strokes + slab serifs (latin.py)")
    for ch, fn in latin.LOWER.items():
        shape, inf = fn(lc)
        l, r = LAT_SB.get(ch, LAT_SB_DEFAULT_L)
        add(ch, [ord(ch)], "base", shape, lsb=l * sbscale, rsb=r * sbscale, fn=fn,
            method="elliptical-pen strokes + slab serifs (latin.py)")
    # digits (tabular)
    for n in range(10):
        shape, inf = misc.digit(lc, n)
        w = inf["xmax"] - inf["xmin"]
        adv = 600 if wname == "Regular" else 640
        add(DIGIT_NAMES[n], [0x30 + n], "base", shape, adv=adv, lsb=(adv - w) / 2, fn=misc.digit,
            method="elliptical-pen strokes (misc.py)")
    # punctuation / symbols
    for ch in PUNCT:
        shape, inf = misc.punct(lc, ch)
        bb = shape.bounds()
        sb = 56
        if ch in ".,:;":
            sb = 64
        if ch in "([{":
            sb = 44
        if ch in "-–—":
            sb = 40
        if ch in "/\\_":
            sb = 20
        adv = None
        if ch in "+\u2212=<>\u00b1\u00d7\u00f7~":      # math signs share one advance width
            adv = 560 if wname == "Regular" else 590
            sb = (adv - (bb[2] - bb[0])) / 2 / sbscale
        add(gname(ord(ch)), [ord(ch)], "base", shape, adv=adv, lsb=sb * sbscale, rsb=sb * sbscale,
            fn=misc.punct, method="strokes/polygons/circles (misc.py)")

    # ---- realise glyphs in the UFO -------------------------------------
    order = []
    marks, bases = [], []
    base_anchor_rows = []
    for e in entries:
        g = ufo.newGlyph(e["name"])
        order.append(e["name"])
        g.unicodes = e["cps"]
        shape = e["shape"]
        empty = len(list(shape.path.segments)) == 0
        if e["kind"] == "mark":
            adv = 0
            if not empty:
                mp = Path(shape.path)
                mp.simplify(fix_winding=True)
                drop_slivers(mp).draw(g.getPen())
            g.width = 0
            marks.append((e["name"], e["anc"]["kind"]))
        else:
            if empty:
                g.width = int(round(e["adv"] or 0))
            else:
                b = shape.bounds()
                dx = e["lsb"] - b[0]
                p = xform(shape.path, 1, 1, dx, 0) if abs(dx) > 1e-9 else shape.path
                p = Path(p)
                p.simplify(fix_winding=True)     # uniform winding after mirrors/rotations
                p = drop_slivers(p)
                p.draw(g.getPen())
                if e["adv"] is not None:
                    g.width = int(round(e["adv"]))
                else:
                    g.width = int(round(b[2] - b[0] + e["lsb"] + e["rsb"]))
            if e["kind"] != "space" and e["name"] != ".notdef":
                bases.append(e["name"])
            if e["anc"]:
                anchors[e["name"]] = e["anc"]
        # final integer rounding of coordinates
        for c in g.contours:
            for pt in c.points:
                pt.x, pt.y = int(round(pt.x)), int(round(pt.y))
            # drop consecutive coincident points of the same kind created by rounding
            keep = []
            for pt in c.points:
                if keep and (keep[-1].x, keep[-1].y, keep[-1].type) == (pt.x, pt.y, pt.type):
                    continue
                keep.append(pt)
            while len(keep) > 3 and (keep[0].x, keep[0].y, keep[0].type) == (keep[-1].x, keep[-1].y, keep[-1].type):
                keep.pop()
            c.points[:] = keep
        prov.append(dict(glyph=e["name"], unicode=["U+%04X" % c for c in e["cps"]], weight=wname,
                         construction=e["method"] or "empty/zero-outline glyph",
                         generator=src(e["fn"]) if e["fn"] else None,
                         third_party_outlines=False))

    # ---- font info ------------------------------------------------------
    i = ufo.info
    style = wname
    i.familyName = FAMILY
    i.styleName = style
    i.styleMapFamilyName = "SW Book Text"
    i.styleMapStyleName = "regular" if wname == "Regular" else "bold"
    i.unitsPerEm = UPM
    i.ascender, i.descender = 880, -300
    i.capHeight, i.xHeight = 650, 440
    i.versionMajor, i.versionMinor = 0, 100
    i.copyright = "Benchmark prototype for SeferWorks. No license assigned; legal review required."
    i.openTypeNameLicense = ("No production license has been assigned to this benchmark prototype. "
                             "Provenance and legal review required before any use.")
    i.openTypeNameDescription = "Original Hebrew book-text benchmark prototype generated from parametric scripts."
    i.postscriptFontName = "SWBookText-" + style
    i.openTypeHeadCreated = "2026/01/01 00:00:00"
    i.openTypeOS2WeightClass = P["wght"]
    i.openTypeOS2WidthClass = 5
    i.openTypeHheaAscender, i.openTypeHheaDescender, i.openTypeHheaLineGap = 880, -300, 0
    i.openTypeOS2TypoAscender, i.openTypeOS2TypoDescender, i.openTypeOS2TypoLineGap = 880, -300, 0
    i.openTypeOS2WinAscent, i.openTypeOS2WinDescent = 1000, 400
    i.openTypeOS2Type = [1]   # restricted licence embedding: benchmark prototype, not licensed
    i.openTypeOS2Selection = [7]
    i.openTypeOS2CodePageRanges = [0, 4]  # Latin 1, Hebrew
    i.openTypeOS2UnicodeRanges = [0, 1, 11]
    i.openTypeGaspRangeRecords = [dict(rangeMaxPPEM=65535, rangeGaspBehavior=[0, 1, 2, 3])]
    i.postscriptUnderlinePosition, i.postscriptUnderlineThickness = -100, 50
    ufo.lib["public.glyphOrder"] = order

    # ---- features --------------------------------------------------------
    kerns = optical_kerns(ufo, bases)
    fea = make_fea(bases, marks, anchors, kerns)
    ufo.features.text = fea

    os.makedirs(outdir, exist_ok=True)
    ufo_path = os.path.join(outdir, "sources", "SWBookText-%s.ufo" % wname)
    if os.path.exists(ufo_path):
        import shutil
        shutil.rmtree(ufo_path)
    os.makedirs(os.path.dirname(ufo_path), exist_ok=True)
    ufo.save(ufo_path)
    return ufo_path, prov


def make_fea(bases, marks, anchors, kerns):
    L = []
    L.append("languagesystem DFLT dflt;\nlanguagesystem latn dflt;\nlanguagesystem hebr dflt;\n")
    kinds = {"below": [], "inside": [], "above": []}
    for nm, kind in marks:
        kinds[kind].append(nm)
    # mark classes
    wide = ["hatafsegol", "hatafpatah", "hatafqamats"]
    below = [m for m in kinds["below"] if m not in wide]
    L.append("markClass [%s] <anchor 0 0> @MC_below;" % " ".join(below))
    L.append("markClass [%s] <anchor 0 0> @MC_belowW;" % " ".join(wide))
    L.append("markClass [dagesh] <anchor 0 0> @MC_inside;")
    L.append("markClass [holam holamhaser] <anchor 0 0> @MC_hol;")
    L.append("markClass [shindot] <anchor 0 0> @MC_dotR;")
    L.append("markClass [sindot] <anchor 0 0> @MC_dotL;")
    L.append("markClass [rafe] <anchor 0 0> @MC_rafe;")
    L.append("")
    L.append("lookup mark_below { lookupflag 0;")
    for b, a in anchors.items():
        if "below" in a:
            L.append("  pos base %s <anchor %d %d> mark @MC_below;" % (b, *a["below"]))
    L.append("} mark_below;")
    L.append("lookup mark_belowW { lookupflag 0;")
    for b, a in anchors.items():
        if "belowW" in a:
            L.append("  pos base %s <anchor %d %d> mark @MC_belowW;" % (b, *a["belowW"]))
    L.append("} mark_belowW;")
    for look, cls, key in (("mark_inside", "MC_inside", "inside"), ("mark_hol", "MC_hol", "hol"),
                           ("mark_dotR", "MC_dotR", "dotR"), ("mark_dotL", "MC_dotL", "dotL"),
                           ("mark_rafe", "MC_rafe", "rafe")):
        L.append("lookup %s { lookupflag 0;" % look)
        for b, a in anchors.items():
            if key in a:
                L.append("  pos base %s <anchor %d %d> mark @%s;" % (b, *a[key], cls))
        L.append("} %s;" % look)
    L.append("\nfeature mark {\n  script hebr; language dflt;\n  lookup mark_below;\n  lookup mark_belowW;\n  lookup mark_inside;"
             "\n  lookup mark_hol;\n  lookup mark_dotR;\n  lookup mark_dotL;\n  lookup mark_rafe;\n} mark;")
    L.append("\nfeature mark {\n  script DFLT; language dflt;\n  lookup mark_below;\n  lookup mark_inside;"
             "\n  lookup mark_hol;\n  lookup mark_dotR;\n  lookup mark_dotL;\n  lookup mark_rafe;\n} mark;") if False else None
    # kerning
    if kerns:
        L.append("\nfeature kern {")
        for (a, b), v in kerns:
            L.append("  pos %s %s %d;" % (a, b, v))
        L.append("} kern;")
    L.append("\ntable GDEF {\n  GlyphClassDef [%s], , [%s], ;\n} GDEF;" % (
        " ".join(bases), " ".join(m for m, _ in marks)))
    return "\n".join(x for x in L if x is not None)


def compile_ttf(ufo_path, ttf_path):
    ufo = ufolib2.Font.open(ufo_path)
    font = ufo2ft.compileTTF(ufo, removeOverlaps=False, reverseDirection=True, inplace=True)
    # fixed timestamps for reproducibility
    font["head"].created = font["head"].modified = EPOCH + 2082844800
    # smart-dropout rendering instructions (unhinted font): SCANCTRL 511, SCANTYPE 4
    from fontTools.ttLib import newTable
    from fontTools.ttLib.tables import ttProgram
    prep = newTable("prep")
    prep.program = ttProgram.Program()
    prep.program.fromBytecode(bytes([0xB8, 0x01, 0xFF, 0x85, 0xB0, 0x04, 0x8D]))
    font["prep"] = prep
    font["maxp"].maxStackElements = max(getattr(font["maxp"], "maxStackElements", 0), 8)
    os.makedirs(os.path.dirname(ttf_path), exist_ok=True)
    font.save(ttf_path)
    return ttf_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", ".."))
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.environ["SOURCE_DATE_EPOCH"] = str(EPOCH)
    allprov = []
    for w in ("Regular", "Bold"):
        up, prov = build_weight(w, out)
        compile_ttf(up, os.path.join(out, "fonts", "SWBookText-%s.ttf" % w))
        allprov += prov
        print("built", w)
    os.makedirs(os.path.join(out, "reports"), exist_ok=True)
    with open(os.path.join(out, "reports", "provenance_glyphs.json"), "w", encoding="utf-8") as f:
        json.dump(allprov, f, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
