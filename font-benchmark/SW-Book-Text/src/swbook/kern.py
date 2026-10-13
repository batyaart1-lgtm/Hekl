"""Deterministic optical kerning generated from outline profiles.

For each ordered pair (L, R) the minimum horizontal clearance between L's
right profile and R's left profile over the y-range both occupy is measured
on a 20-unit scanline grid.  The kern value moves that clearance 55 % of the
way toward a target (tighter where the pair is loose, looser where it is
tight), clamped to [-70, +25] and quantised to 5 units.  Only |value| >= 10
is emitted.  This is script-generated, not hand-tuned: human review of the
kerning is listed as an open item in the reports.
"""
import numpy as np
from fontTools.pens.basePen import BasePen

HEB = [chr(c) for c in range(0x05D0, 0x05EB)]


class _Flat(BasePen):
    def __init__(self):
        super().__init__(None)
        self.segs, self.cur, self.start = [], None, None

    def _moveTo(self, p): self.cur = self.start = p
    def _lineTo(self, p):
        self.segs.append((self.cur, p)); self.cur = p
    def _curveToOne(self, a, b, c):
        p0 = self.cur
        for i in range(1, 11):
            t = i / 10; m = 1 - t
            q = (m**3*p0[0]+3*m*m*t*a[0]+3*m*t*t*b[0]+t**3*c[0], m**3*p0[1]+3*m*m*t*a[1]+3*m*t*t*b[1]+t**3*c[1])
            self._lineTo(q)
    def _qCurveToOne(self, a, c):
        p0 = self.cur
        for i in range(1, 9):
            t = i / 8; m = 1 - t
            self._lineTo((m*m*p0[0]+2*m*t*a[0]+t*t*c[0], m*m*p0[1]+2*m*t*a[1]+t*t*c[1]))
    def _closePath(self):
        if self.cur != self.start:
            self.segs.append((self.cur, self.start))
    _endPath = _closePath


YS = np.arange(-200, 780, 20.0) + 10


def profile(glyph):
    pen = _Flat()
    glyph.draw(pen)
    lo = np.full(len(YS), np.nan)
    hi = np.full(len(YS), np.nan)
    for (x0, y0), (x1, y1) in pen.segs:
        if y0 == y1:
            continue
        ya, yb = sorted((y0, y1))
        for i, y in enumerate(YS):
            if ya <= y < yb:
                x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                lo[i] = x if np.isnan(lo[i]) else min(lo[i], x)
                hi[i] = x if np.isnan(hi[i]) else max(hi[i], x)
    return lo, hi


def _pairs(ufo, names, target, ymin, ymax, scale):
    prof = {n: profile(ufo[n]) for n in names}
    out = []
    sel = (YS >= ymin) & (YS <= ymax)
    for a in names:
        for b in names:
            la, ha = prof[a]
            lb, hb = prof[b]
            d = (ufo[a].width - ha) + lb
            d = d[sel]
            d = d[~np.isnan(d)]
            if len(d) == 0:
                continue
            dmin = float(d.min())
            k = (target - dmin) * 0.55
            k = max(-70, min(25, k))
            k = int(round(k / 5.0) * 5)
            if abs(k) >= 10:
                out.append(((a, b), k))
    return out


def optical_kerns(ufo, bases):
    names = {ufo[n].unicodes[0]: n for n in bases if ufo[n].unicodes}
    heb = [names[c] for c in range(0x05D0, 0x05EB) if c in names]
    low = [names[c] for c in range(ord('a'), ord('z') + 1) if c in names]
    upp = [names[c] for c in range(ord('A'), ord('Z') + 1) if c in names]
    weight_scale = 1.0
    res = []
    res += _pairs(ufo, heb, 100, 0, 715, 1)
    res += _pairs(ufo, low, 66, 0, 720, 1)
    res += _pairs(ufo, upp, 70, 0, 700, 1)
    res += _pairs(ufo, upp + low, 70, 0, 650, 1) if False else []
    # upper->lower (e.g. "Te", "Wa")
    res += [p for p in _pairs(ufo, upp + low, 68, 0, 440, 1) if p[0][0] in upp and p[0][1] in low]
    return res
