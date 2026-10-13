"""Audit/rendering library for Round 2 (rendering is always from the compiled TTF files).

Rendering model: outlines of the compiled font are flattened, drawn 4x supersampled with PIL
and box-filtered down, so output is anti-aliased greyscale at the requested dpi.  Layout uses
HarfBuzz (kerning + GPOS marks) with the same font binaries that are embedded in the PDF.
No other font is ever used (labels use PIL's built-in bitmap font).
"""
import os, sys, json
import numpy as np
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from PIL import Image, ImageDraw, ImageChops, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SS = 4  # supersampling


class _Flat(BasePen):
    def __init__(self):
        super().__init__(None)
        self.contours, self.cur = [], []

    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)

    def _qCurveToOne(self, a, c):
        p0 = self.cur[-1]
        for i in range(1, 9):
            t = i / 8; m = 1 - t
            self.cur.append((m * m * p0[0] + 2 * m * t * a[0] + t * t * c[0], m * m * p0[1] + 2 * m * t * a[1] + t * t * c[1]))

    def _curveToOne(self, a, b, c):
        p0 = self.cur[-1]
        for i in range(1, 11):
            t = i / 10; m = 1 - t
            self.cur.append((m**3 * p0[0] + 3 * m * m * t * a[0] + 3 * m * t * t * b[0] + t**3 * c[0],
                             m**3 * p0[1] + 3 * m * m * t * a[1] + 3 * m * t * t * b[1] + t**3 * c[1]))

    def _closePath(self):
        if self.cur:
            self.contours.append(self.cur)
        self.cur = []
    _endPath = _closePath


class Face:
    def __init__(self, path):
        self.path = path
        self.tt = TTFont(path)
        self.gs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.upm = self.tt["head"].unitsPerEm
        self.cmap = self.tt.getBestCmap()
        self.hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(path)))
        self._flat = {}

    def contours(self, name):
        if name not in self._flat:
            fp = _Flat()
            self.gs[name].draw(fp)
            self._flat[name] = fp.contours
        return self._flat[name]

    def shape(self, text, rtl, features=None):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.direction = "rtl" if rtl else "ltr"
        buf.script = "Hebr" if rtl else "Latn"
        buf.language = "he" if rtl else "en"
        hb.shape(self.hbfont, buf, features or {})
        return [(i.codepoint, i.cluster, p.x_advance, p.x_offset, p.y_offset)
                for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


def faces(fontdir):
    return {w: Face(os.path.join(fontdir, "SWBookText-%s.ttf" % w)) for w in ("Regular", "Bold")}


def _draw_glyph(big, face, name, ox, oy, scale):
    """ox,oy: pen position in big-image pixels (baseline y); scale: px per font unit."""
    cs = face.contours(name)
    if not cs:
        return
    xs = [x for c in cs for x, y in c]
    ys = [y for c in cs for x, y in c]
    x0, x1 = int(ox + min(xs) * scale) - 2, int(ox + max(xs) * scale) + 3
    y0, y1 = int(oy - max(ys) * scale) - 2, int(oy - min(ys) * scale) + 3
    w, h = x1 - x0, y1 - y0
    if w <= 0 or h <= 0:
        return
    m = Image.new("1", (w, h), 0)
    for c in cs:
        mm = Image.new("1", (w, h), 0)
        ImageDraw.Draw(mm).polygon([(ox + x * scale - x0, oy - y * scale - y0) for x, y in c], fill=1)
        m = ImageChops.logical_xor(m, mm)
    big.paste(0, (x0, y0), m)


def render_text(face, text, rtl, pt, dpi=300, pad=12, min_w=0, height_units=(900, -420), width_px=None, shaped=None):
    """Return an anti-aliased 'L' image of one line at pt/dpi."""
    sh = shaped or face.shape(text, rtl)
    px_per_unit = pt * dpi / 72.0 / face.upm
    tot = sum(s[2] for s in sh) * px_per_unit
    W = int(width_px or max(min_w, tot + 2 * pad))
    top = int(height_units[0] * px_per_unit) + pad
    bot = int(-height_units[1] * px_per_unit) + pad
    H = top + bot
    big = Image.new("L", (W * SS, H * SS), 255)
    sc = px_per_unit * SS
    x = (W - tot - pad) * SS if rtl else pad * SS
    base = top * SS
    for gid, cl, xa, xo, yo in sh:
        _draw_glyph(big, face, face.order[gid], x + xo * sc, base - yo * sc, sc)
        x += xa * sc
    return big.resize((W, H), Image.BOX)


def render_lines(face, lines, pt, dpi=300, width_px=None, leading=1.5, pad=12):
    """lines: [(text, rtl)]; returns stacked image."""
    ims = [render_text(face, t, r, pt, dpi, pad=pad, width_px=width_px) for t, r in lines]
    W = max(i.width for i in ims)
    lh = int(pt * dpi / 72.0 * leading)
    H = lh * len(ims) + pad
    out = Image.new("L", (W, H), 255)
    for k, im in enumerate(ims):
        # align baseline: images share the same height_units, so align tops
        out.paste(im, (0, k * lh))
    return out


def label(im, text, xy=(4, 2)):
    d = ImageDraw.Draw(im)
    d.text(xy, text, fill=90, font=ImageFont.load_default())
    return im


# ------------------------------------------------------------------ metrics
HEB = [chr(c) for c in range(0x05D0, 0x05EB)]
HEB_NAMES = ["alef", "bet", "gimel", "dalet", "he", "vav", "zayin", "het", "tet", "yod", "finalkaf", "kaf", "lamed",
             "finalmem", "mem", "finalnun", "nun", "samekh", "ayin", "finalpe", "pe", "finaltsadi", "tsadi", "qof",
             "resh", "shin", "tav"]


def glyph_raster(face, ch, px_h=64, canvas=(120, 120)):
    """Letter raster at a fixed ppem (px_h = ppem*0.65) for similarity: aligned on baseline, advance-centered."""
    name = face.cmap[ord(ch)]
    ppem = px_h / 0.65
    sc = ppem / face.upm
    adv = face.tt["hmtx"][name][0]
    W, H = canvas
    big = Image.new("L", (W * SS, H * SS), 255)
    ox = (W - adv * sc) / 2 * SS
    oy = int(H * 0.72) * SS
    _draw_glyph(big, face, name, ox, oy, sc * SS)
    return np.asarray(big.resize((W, H), Image.BOX), dtype=float) / 255.0


def metrics(face):
    out = {}
    hm = face.tt["hmtx"]
    for ch, nm in zip(HEB, HEB_NAMES):
        g = face.cmap[ord(ch)]
        adv, lsb = hm[g]
        gl = face.tt["glyf"][g]
        gl.recalcBounds(face.tt["glyf"])
        cs = face.contours(g)
        area = 0.0
        for c in cs:
            a = 0.0
            for (x0, y0), (x1, y1) in zip(c, c[1:] + c[:1]):
                a += x0 * y1 - x1 * y0
            area += a / 2.0
        ink = abs(area)
        # optical centre of ink (area centroid x) relative to advance centre
        cx = 0.0; tot = 0.0
        for c in cs:
            for (x0, y0), (x1, y1) in zip(c, c[1:] + c[:1]):
                cr = x0 * y1 - x1 * y0
                cx += (x0 + x1) * cr
                tot += cr
        cen = cx / (3 * tot) if tot else 0
        out[nm] = dict(char=ch, adv=adv, lsb=lsb, rsb=adv - gl.xMax, xMin=gl.xMin, xMax=gl.xMax, yMin=gl.yMin,
                       yMax=gl.yMax, ink_area=round(ink), density=round(ink / ((gl.xMax - gl.xMin) * (gl.yMax - gl.yMin)), 3),
                       centroid_offset=round(cen - adv / 2, 1))
    return out


def confusion(face, px_h=44, top=14):
    """Pairwise normalised distance between letter rasters at ~10 pt/300 dpi-ish size (lower = more confusable)."""
    R = {ch: glyph_raster(face, ch, px_h=px_h, canvas=(90, 90)) for ch in HEB}
    res = []
    for i, a in enumerate(HEB):
        for b in HEB[i + 1:]:
            best = 1e9
            for dx in (-2, -1, 0, 1, 2):   # tolerate tiny shifts
                d = np.abs(R[a] - np.roll(R[b], dx, axis=1)).sum() / max(1.0, ((1 - R[a]).sum() + (1 - R[b]).sum()) / 2)
                best = min(best, d)
            res.append((round(best, 3), a, b))
    res.sort()
    return res[:top]


def pair_stats(face, chars=HEB, band=(0, 650)):
    """Optical whitespace between neighbours (RTL set, kerning applied): mean clearance over the
    band, clipped at 220 units (so wide open counters do not dominate)."""
    from swbook.kern import profile  # type: ignore

    class G:
        def __init__(s, gl): s.gl = gl
        def draw(s, pen): s.gl.draw(pen)
    prof = {ch: profile(G(face.gs[face.cmap[ord(ch)]])) for ch in chars}
    from swbook.kern import YS
    sel = (YS >= band[0]) & (YS <= band[1])
    mins, means = {}, {}
    for a in chars:
        for b in chars:
            sh = face.shape(a + b, True)
            names = [face.order[s[0]] for s in sh]
            left, right = b, a
            li = names.index(face.cmap[ord(left)])
            adv = sh[li][2]
            _, hi = prof[left]
            lo, _ = prof[right]
            d = (adv - hi) + lo
            d = d[sel]
            both = ~np.isnan(d)
            if both.sum() == 0:
                continue
            dd = np.clip(d[both], -500, 220)
            mins[a + b] = float(dd.min())
            means[a + b] = float(dd.mean())
    return mins, means
