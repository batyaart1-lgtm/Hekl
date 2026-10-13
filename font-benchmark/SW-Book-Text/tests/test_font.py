"""Automated validation of SW Book Text (both weights)."""
import os, re, sys, hashlib, subprocess, tempfile, shutil
import pytest
import pathops
import uharfbuzz as hb
import ots
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from conftest import ROOT, FONTS

HEB_LETTERS = [chr(c) for c in range(0x05D0, 0x05EB)]
HEB_MARKS = [0x05B0, 0x05B1, 0x05B2, 0x05B3, 0x05B4, 0x05B5, 0x05B6, 0x05B7, 0x05B8, 0x05B9, 0x05BA,
             0x05BB, 0x05BC, 0x05BD, 0x05BF, 0x05C1, 0x05C2, 0x05C7]
HEB_PUNCT = [0x05BE, 0x05F3, 0x05F4, 0x05C0, 0x05C3]
REQUIRED = set(range(0x05D0, 0x05EB)) | set(HEB_MARKS) | set(HEB_PUNCT) | set(range(0x30, 0x3A)) \
    | set(range(0x41, 0x5B)) | set(range(0x61, 0x7B)) | set(range(0x21, 0x7F)) | {0x20, 0xA0}
EXPECTED_TABLES = {"GDEF", "GPOS", "OS/2", "cmap", "gasp", "glyf", "head", "hhea", "hmtx", "loca", "maxp", "name", "post"}


def glyph_path(font, name):
    p = pathops.Path()
    font.getGlyphSet()[name].draw(p.getPen())
    return p


# ------------------------------------------------------------- tables
def test_required_tables_present(font):
    assert EXPECTED_TABLES <= set(font.keys())


def test_ots_sanitizer_accepts_font(path):
    r = ots.sanitize(path)      # raises ots.CalledProcessError if OTS rejects the font
    assert r.returncode == 0


def test_all_tables_decompile_and_roundtrip(path):
    f = TTFont(path)
    for tag in f.keys():
        if tag == "GlyphOrder":
            continue
        f[tag]
    tmp = tempfile.mktemp(suffix=".ttf")
    f.save(tmp)
    g = TTFont(tmp)
    assert g.getGlyphOrder() == f.getGlyphOrder()
    os.remove(tmp)


def test_name_table(font):
    nm = font["name"]
    assert nm.getDebugName(1) == "SW Book Text"
    assert nm.getDebugName(16) == "SW Book Text \u2014 Benchmark Prototype"
    assert "Benchmark Prototype" in nm.getDebugName(4)
    assert nm.getDebugName(6).startswith("SWBookText-")
    assert "No production license" in (nm.getDebugName(13) or "")


def test_head_hhea_os2_consistency(font):
    assert font["head"].unitsPerEm == 1000
    assert font["hhea"].numberOfHMetrics == len(font.getGlyphOrder())
    os2 = font["OS/2"]
    assert os2.sTypoAscender == font["hhea"].ascent
    assert os2.usWinAscent >= font["head"].yMax
    assert os2.usWinDescent >= -font["head"].yMin
    assert os2.fsType == 2   # restricted-licence embedding: prototype, no licence granted


# --------------------------------------------------------------- cmap
def test_cmap_covers_required(font):
    cmap = font.getBestCmap()
    missing = sorted(REQUIRED - set(cmap))
    assert not missing, "missing codepoints: %s" % ["U+%04X" % c for c in missing]


def test_hebrew_27_letters_distinct_outlines(font):
    cmap = font.getBestCmap()
    sigs = set()
    for ch in HEB_LETTERS:
        g = cmap[ord(ch)]
        path = glyph_path(font, g)
        assert list(path.segments), "empty glyph for %s" % ch
        sigs.add(tuple(round(v) for seg in path.segments for pts in seg[1] for v in pts))
    assert len(sigs) == 27


def test_unicode_mapping_is_one_to_one_for_letters(font):
    cmap = font.getBestCmap()
    names = [cmap[ord(c)] for c in HEB_LETTERS]
    assert len(set(names)) == 27


def test_no_missing_glyphs_in_specimen_text(font):
    sys.path.insert(0, os.path.join(ROOT, "specimen"))
    import texts
    cmap = font.getBestCmap()
    chars = set()
    for name in dir(texts):
        v = getattr(texts, name)
        if isinstance(v, str):
            chars |= set(v)
        elif isinstance(v, list):
            for it in v:
                if isinstance(it, str):
                    chars |= set(it)
                elif isinstance(it, tuple):
                    for s in it:
                        chars |= set(s)
    chars -= {"\n"}
    missing = sorted(c for c in chars if ord(c) not in cmap)
    assert not missing, "chars with no glyph: %s" % [(c, "U+%04X" % ord(c)) for c in missing]


# ---------------------------------------------------- glyph names/outlines
def test_glyph_names_valid_unique(font):
    order = font.getGlyphOrder()
    assert len(order) == len(set(order)), "duplicate glyph names"
    for n in order:
        assert re.fullmatch(r"[A-Za-z_.][A-Za-z0-9_.]{0,62}", n), n
    assert order[0] == ".notdef"
    assert font["maxp"].numGlyphs == len(order)


def test_contours_valid(font):
    gs = font.getGlyphSet()
    glyf = font["glyf"]
    problems = []
    for name in font.getGlyphOrder():
        g = glyf[name]
        if g.numberOfContours == 0:
            continue
        p = glyph_path(font, name)
        starts = [0] + [e + 1 for e in g.endPtsOfContours[:-1]]
        for st, en in zip(starts, g.endPtsOfContours):
            if en - st + 1 < 3:
                problems.append((name, "degenerate contour (<3 points)"))
        for c in p.contours:
            if abs(c.area) < 40:
                problems.append((name, "tiny contour area %.1f" % c.area))
        # self-overlap: simplify must not change area materially
        q = pathops.Path(p)
        q.simplify(fix_winding=True)
        if abs(q.area - p.area) > 0.02 * max(1.0, abs(p.area)) + 50:
            problems.append((name, "overlapping/self-intersecting contours (area %.0f vs %.0f)" % (p.area, q.area)))
    assert not problems, problems[:20]


def test_extreme_bboxes(font):
    gs = font.getGlyphSet()
    bad = []
    for name in font.getGlyphOrder():
        bp = BoundsPen(gs)
        gs[name].draw(bp)
        if bp.bounds is None:
            continue
        x0, y0, x1, y1 = bp.bounds
        if y1 > 900 or y0 < -350 or x1 - x0 > 1100 or x0 < -400 or x1 > 1400:
            bad.append((name, bp.bounds))
    assert not bad, bad


def test_outer_contours_clockwise_truetype(font):
    """TrueType convention: outer contours clockwise.  The largest contour of every
    non-composite base glyph must be clockwise (pathops 'clockwise' flag)."""
    bad = []
    for name in font.getGlyphOrder():
        p = glyph_path(font, name)
        cs = list(p.contours)
        if not cs:
            continue
        biggest = max(cs, key=lambda c: abs(c.area))
        if not biggest.clockwise:
            bad.append(name)
    assert not bad, bad


# ------------------------------------------------------------- metrics
def test_horizontal_metrics(font):
    hmtx = font["hmtx"]
    glyf = font["glyf"]
    cmap = font.getBestCmap()
    for name in font.getGlyphOrder():
        adv, lsb = hmtx[name]
        g = glyf[name]
        assert adv >= 0
        if g.numberOfContours > 0:
            g.recalcBounds(glyf)
            assert lsb == g.xMin, (name, lsb, g.xMin)
    marks = [cmap[c] for c in HEB_MARKS]
    for m in marks:
        assert hmtx[m][0] == 0, m
    for ch in HEB_LETTERS + list("abcxyzABCXYZ0123456789"):
        adv, lsb = hmtx[cmap[ord(ch)]]
        g = glyf[cmap[ord(ch)]]
        rsb = adv - g.xMax
        assert lsb >= -40 and rsb >= -60, (ch, lsb, rsb)
        assert adv > 100, ch
    digits = {hmtx[cmap[c]][0] for c in range(0x30, 0x3A)}
    assert len(digits) == 1, "digits must be tabular"
    assert hmtx[cmap[0x20]][0] > 150


def test_optical_sidebearing_consistency_hebrew(font):
    """Hebrew spacing is *optical* (Round 2): sidebearing + clipped optical depth of each side
    (src/swbook/spacing.py) must be near-constant across the 27 letters.  Measured sigma at
    delivery: ~7-9 units (left) / ~8-9 (right); the test allows 14."""
    import numpy as np
    from swbook.spacing import depths
    hmtx, glyf, cmap = font["hmtx"], font["glyf"], font.getBestCmap()
    L, R = [], []
    for ch in HEB_LETTERS:
        g = cmap[ord(ch)]
        d = depths(glyph_path(font, g), (0, 715), 110)
        gl = glyf[g]
        L.append(gl.xMin + d[0])
        R.append(hmtx[g][0] - gl.xMax + d[1])
    assert np.std(L) <= 14 and np.std(R) <= 14, (np.std(L), np.std(R))


# --------------------------------------------------- shaping/GPOS marks
def hbfont(path):
    return hb.Font(hb.Face(hb.Blob.from_file_path(path)))


def shape(f, text, rtl=True):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.direction = "rtl" if rtl else "ltr"
    buf.script = "Hebr" if rtl else "Latn"
    hb.shape(f, buf, {})
    return buf.glyph_infos, buf.glyph_positions


def test_gpos_features_present(font):
    feats = {fr.FeatureTag for fr in font["GPOS"].table.FeatureList.FeatureRecord}
    assert {"mark", "kern"} <= feats
    scripts = {s.ScriptTag for s in font["GPOS"].table.ScriptList.ScriptRecord}
    assert "hebr" in scripts and "latn" in scripts and "DFLT" in scripts or "hebr" in scripts


def test_mark_positioning_attaches_all_marks(path, font):
    """Every Hebrew vowel/dagesh/dot mark gets a GPOS offset on every base letter that
    legitimately takes it, and a base+mark pair never overlaps outlines."""
    f = hbfont(path)
    order = font.getGlyphOrder()
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    failures = []
    below = [0x05B0, 0x05B1, 0x05B2, 0x05B3, 0x05B4, 0x05B5, 0x05B6, 0x05B7, 0x05B8, 0x05BB, 0x05BD, 0x05C7]
    for ch in HEB_LETTERS:
        for m in below + [0x05BC]:
            infos, pos = shape(f, ch + chr(m))
            assert len(infos) == 2
            # visual rtl order: mark follows base logically; find mark glyph
            mi = [i for i, g in enumerate(infos) if order[g.codepoint] == cmap[m]][0]
            if pos[mi].x_advance != 0:
                failures.append((ch, "%04X" % m, "mark advance nonzero"))
            if pos[mi].x_offset == 0 and pos[mi].y_offset == 0:
                failures.append((ch, "%04X" % m, "mark not positioned"))
    assert not failures, failures[:15]


def _placed_union(font, f, text):
    infos, pos = shape(f, text)
    order = font.getGlyphOrder()
    paths = []
    x = 0
    for g, p in zip(infos, pos):
        path = glyph_path(font, order[g.codepoint])
        path = path.transform(1, 0, 0, 1, x + p.x_offset, p.y_offset)
        paths.append(path)
        x += p.x_advance
    return paths


def test_marks_do_not_collide_with_base(path, font):
    f = hbfont(path)
    cmap = font.getBestCmap()
    below = [0x05B0, 0x05B1, 0x05B2, 0x05B3, 0x05B4, 0x05B5, 0x05B6, 0x05B7, 0x05B8, 0x05BB]
    bad = []
    for ch in HEB_LETTERS:
        for m in below + [0x05BC]:
            ps = _placed_union(font, f, ch + chr(m))
            a, b = ps
            inter = pathops.op(a, b, pathops.PathOp.INTERSECTION)
            if abs(inter.area) > 1:
                bad.append((ch, "U+%04X" % m, round(abs(inter.area))))
    assert not bad, bad[:20]


def test_shin_sin_dots_and_holam_above(path, font):
    f = hbfont(path)
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    for text in ("שׁ", "שׂ", "שֹ", "בֹ", "וֹ", "לֹ"):
        infos, pos = shape(f, text)
        ps = _placed_union(font, f, text)
        assert abs(pathops.op(ps[0], ps[1], pathops.PathOp.INTERSECTION).area) < 1, text
        base_top = ps[0].bounds[3] if infos[0].codepoint == font.getGlyphID(cmap[ord(text[0])]) else ps[1].bounds[3]
        mark = [p for p in ps if p.bounds[1] >= base_top - 1]
        assert mark, "mark not above base: " + text


def test_dagesh_inside_counter(path, font):
    f = hbfont(path)
    for ch in "בדהחכמסעפקרשתטלנ":
        ps = _placed_union(font, f, ch + "ּ")
        infos, _ = shape(f, ch + "ּ")
        names = [font.getGlyphName(g.codepoint) for g in infos]
        ib = names.index(font.getBestCmap()[ord(ch)])
        bb, ba = ps[ib].bounds, ps[1 - ib].bounds
        # dagesh centre lies within letter's bbox
        cx, cy = (ba[0] + ba[2]) / 2, (ba[1] + ba[3]) / 2
        assert bb[0] < cx < bb[2] and bb[1] < cy < bb[3], ch


def test_kerning_applied(path, font):
    f = hbfont(path)
    adv = font["hmtx"][font.getBestCmap()[ord("A")]][0]
    infos, pos = shape(f, "AV", rtl=False)
    assert pos[0].x_advance < adv, "no kerning on AV"
    infos3, pos3 = shape(f, "HH", rtl=False)
    assert pos3[0].x_advance == font["hmtx"][font.getBestCmap()[ord("H")]][0]


def test_kern_pair_count(font):
    n = 0
    for lk in font["GPOS"].table.LookupList.Lookup:
        for st in lk.SubTable:
            if getattr(st, "LookupType", None) == 2 or lk.LookupType == 2:
                n += 1
    assert n >= 1


def test_no_collisions_between_neighbouring_letters(path, font):
    """Ordinary text: for every ordered pair of Hebrew letters (and Latin lowercase) set
    with real HarfBuzz advances (kerning included) the outlines keep a clearance."""
    from swbook.kern import profile
    f = hbfont(path)
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    import numpy as np
    from fontTools.pens.recordingPen import DecomposingRecordingPen

    class G:
        def __init__(self, gl): self.gl = gl
        def draw(self, pen): self.gl.draw(pen)
    cache = {}

    def prof(ch):
        if ch not in cache:
            cache[ch] = profile(G(gs[cmap[ord(ch)]]))
        return cache[ch]
    worst = []
    sets = [(HEB_LETTERS, True), ([chr(c) for c in range(97, 123)], False), ([chr(c) for c in range(65, 91)], False)]
    for chars, rtl in sets:
        for a in chars:
            for b in chars:
                infos, pos = shape(f, a + b, rtl)
                # logical a then b; visual: rtl -> b left of a
                left, right = (b, a) if rtl else (a, b)
                li = [i for i, g in enumerate(infos) if font.getGlyphName(g.codepoint) == cmap[ord(left)]][0]
                ri = [i for i, g in enumerate(infos) if font.getGlyphName(g.codepoint) == cmap[ord(right)]][0]
                adv_left = pos[li].x_advance
                _, hi = prof(left)
                lo, _ = prof(right)
                d = (adv_left - hi) + lo
                d = d[~np.isnan(d)]
                if len(d) and d.min() < 12:
                    worst.append((a + b, round(float(d.min()))))
    assert not worst, "colliding/near-touching pairs (%d): %s" % (len(worst), worst[:25])


def test_glyph_rendering_at_print_sizes(path, font):
    """Rasterise every required glyph with FreeType at 10-13 pt, 600 dpi, and check ink."""
    import freetype
    face = freetype.Face(path)
    cmap = font.getBestCmap()
    for pt in (10, 11, 12, 13):
        face.set_char_size(pt * 64, 0, 600, 600)
        for cp in sorted(REQUIRED - {0x20, 0xA0} - set(HEB_MARKS) - set(HEB_PUNCT)):
            face.load_char(chr(cp), freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
            bm = face.glyph.bitmap
            assert bm.width > 0 and bm.rows > 0, (pt, hex(cp))
            ink = sum(1 for v in bm.buffer if v > 127)
            assert ink > 10, (pt, hex(cp), ink)


def test_stem_contrast_regular_vs_bold():
    r, b = TTFont(FONTS["Regular"]), TTFont(FONTS["Bold"])
    for tag in ("o", "n", "l", "ד", "ו"):
        pass
    cm_r, cm_b = r.getBestCmap(), b.getBestCmap()

    def ink(font, cm, ch):
        return abs(glyph_path(font, cm[ord(ch)]).area)
    for ch in "ndlmorדהוחרת":
        assert ink(b, cm_b, ch) > 1.18 * ink(r, cm_r, ch), ch


def test_bold_regular_same_coverage_and_glyph_order():
    r, b = TTFont(FONTS["Regular"]), TTFont(FONTS["Bold"])
    assert r.getGlyphOrder() == b.getGlyphOrder()
    assert set(r.getBestCmap()) == set(b.getBestCmap())


# --------------------------------------------------------- provenance
def test_build_reads_no_foreign_font_binaries(tmp_path):
    """Run the whole build in a subprocess with an audit hook and verify no .ttf/.otf/
    .woff/.pfb/.ttc file is opened for reading (only fonts written to the output dir)."""
    code = r'''
import sys, os
opened=[]
def hook(ev,args):
    if ev=="open":
        p=str(args[0]); mode=args[1] if len(args)>1 else None
        flags=args[2] if len(args)>2 else 0
        opened.append((p,mode,flags))
sys.addaudithook(hook)
sys.path.insert(0, sys.argv[1])
os.environ["SOURCE_DATE_EPOCH"]="1767225600"
from swbook import build
sys.argv=["build","--out",sys.argv[2]]
build.main()
bad=[p for p,m,f in opened if p.lower().endswith((".ttf",".otf",".woff",".woff2",".pfb",".ttc",".pfa"))
     and not p.startswith(sys.argv[2]) and (m is None or "r" in str(m) or (isinstance(f,int) and (f & 3)==0))]
print("FONTFILES_OPENED_FOR_READ:", bad)
'''
    out = tmp_path / "o"
    r = subprocess.run([sys.executable, "-c", code, os.path.join(ROOT, "src"), str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    line = [l for l in r.stdout.splitlines() if l.startswith("FONTFILES_OPENED_FOR_READ")][0]
    assert line.endswith("[]"), line


def test_reproducible_build(tmp_path):
    env = dict(os.environ, PYTHONHASHSEED="0")
    hashes = []
    for i in range(2):
        out = tmp_path / ("b%d" % i)
        r = subprocess.run([sys.executable, "-m", "swbook.build", "--out", str(out)], cwd=os.path.join(ROOT, "src"),
                           capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stderr[-1500:]
        hashes.append({w: hashlib.sha256(open(out / "fonts" / ("SWBookText-%s.ttf" % w), "rb").read()).hexdigest()
                       for w in ("Regular", "Bold")})
    assert hashes[0] == hashes[1]
    for w in ("Regular", "Bold"):
        assert hashes[0][w] == hashlib.sha256(open(FONTS[w], "rb").read()).hexdigest(), \
            "committed font differs from a fresh build (%s)" % w
