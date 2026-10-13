"""Hebrew letter constructions (original, parametric).

Design language ("SW Book Text"): a *horizontal-stress* Hebrew serif.
Horizontals are thick (pen height H), verticals thin (pen width V).  Roofs
have a chiselled left terminal and a squared right corner; free vertical
terminals are cut flat with a small foot flare; round letters are drawn with
an elliptical pen, so contrast arises naturally and stays consistent.

Every function returns (Shape, info) where info carries the ink width and
the mark anchors.  All coordinates: y=0 baseline, y=T top of letters.
"""
from .geom import *
from pathops import Path


class HCtx:
    T = 715          # letter height
    ASC = 880        # lamed ascender
    DESC = -250      # final-letter descender

    def __init__(self, H, V, wf, name):
        self.H, self.V, self.wf, self.name = H, V, wf, name
        self.bold = name == "Bold"

    # ---- primitives --------------------------------------------------
    def pen(self, path, cap=BUTT):
        return stroke(path, self.V, self.H, cap, RJOIN)

    def roof(self, x0, x1, ytop=None, bevel=True):
        """Thick horizontal with chiselled left end, flat right end."""
        H = self.H
        yt = self.T if ytop is None else ytop
        yb = yt - H
        if bevel:
            return poly([(x0, yt), (x1, yt), (x1, yb), (x0 + H * 0.95, yb),
                         (x0, yb + H * 0.42)])
        return rect(x0, yb, x1, yt)

    def base(self, x0, x1, bevel=True):
        """Thick horizontal sitting on the baseline (mirror-bevel)."""
        H = self.H
        if bevel:
            return poly([(x0, 0), (x1, 0), (x1, H), (x0 + H * 0.95, H),
                         (x0, H * 0.58)])
        return rect(x0, 0, x1, H)

    def stem(self, xl, y0, y1, flare=True):
        """Vertical stem: slight entasis (thinner toward the foot) and, if ``flare``,
        a small concave bracket at the foot (no wedge)."""
        V, H = self.V, self.H
        ins = V * 0.06
        p = Path()
        p.moveTo(xl, y1)
        p.lineTo(xl + V, y1)
        if flare:
            fo, fh = 10.0, 46.0
            p.lineTo(xl + V - ins, y0 + fh)
            p.quadTo(xl + V - ins, y0 + 6, xl + V + fo, y0)
            p.lineTo(xl - fo, y0)
            p.quadTo(xl + ins, y0 + 6, xl + ins, y0 + fh)
        else:
            p.lineTo(xl + V - ins, y0)
            p.lineTo(xl + ins, y0)
        p.close()
        return p

    def beak(self, xr, ytop=None, h=34.0):
        """Small downward serif at the right end of a roof (family detail shared with vav/lamed)."""
        V, H = self.V, self.H
        yb = (self.T if ytop is None else ytop) - H
        return poly([(xr - V * 0.80, yb + 2), (xr, yb + 2), (xr, yb - h), (xr - V * 0.40, yb - h * 0.85)])

    def beakL(self, xl, ytop=None, h=34.0):
        """Small downward serif at the LEFT end of a head (heads overhang to the left)."""
        V, H = self.V, self.H
        yb = (self.T if ytop is None else ytop) - H
        return poly([(xl + V * 0.80, yb + 2), (xl, yb + 2), (xl, yb - h), (xl + V * 0.40, yb - h * 0.85)])

    def headL(self, xl, xr, ytop=None):
        """Flat head from xl to xr (overhangs left of the stem) with a small beak at its left end."""
        yt = self.T if ytop is None else ytop
        return S(rect(xl, yt - self.H, xr, yt), self.beakL(xl, yt))

    def fillet(self, px, py, hx, vy, r=None):
        """Fill the concave corner at (px, py): the horizontal edge runs in direction hx (+-1),
        the vertical edge in direction vy (+-1)."""
        r = r or 20.0
        k = 0.5523 * r
        p = Path()
        p.moveTo(px, py)
        p.lineTo(px + hx * r, py)
        p.cubicTo(px + hx * r - hx * k, py, px, py + vy * r - vy * k, px, py + vy * r)
        p.close()
        return p

    def stemR(self, xr, y0, y1, flare=True):
        return self.stem(xr - self.V, y0, y1, flare)

    @property
    def mark_r(self):
        return 42 if self.bold else 32

    def below_off(self, wide=False):
        r = self.mark_r
        return (5.3 if wide else 2.7) * r + 30

    def W(self, w):
        return w * self.wf


def S(*parts):
    s = Shape()
    for p in parts:
        s.add(p)
    return s


def info(s, **kw):
    b = s.bounds()
    d = dict(xmin=b[0], ymin=b[1], xmax=b[2], ymax=b[3])
    d.update(kw)
    return d


# ---------------------------------------------------------------------
def dalet(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(490)
    ov = 46
    s = S(c.roof(0, w), c.beak(w), c.stemR(w - ov, 0, T - H * 0.5), c.fillet(w - ov - V, T - H, -1, -1))
    return s, info(s, inside=(w * 0.5, T * 0.46))


def resh(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(470)
    R = 170
    yc = T - H / 2
    xc = w - V / 2
    p = Pth(H * 0.9, yc).L(xc - R, yc).C(xc - R * 0.45, yc, xc, yc - R * 0.35, xc, yc - R)
    p.L(xc, 0)
    stem_part = c.pen(p)
    # flat foot on the stem
    foot = poly([(xc - V / 2 - 24, 0), (xc + V / 2, 0), (xc + V / 2, c.H * 0.5),
                 (xc - V / 2, c.H * 0.5 + 6)])
    s = S(stem_part, foot, c.roof(0, H * 1.6))
    return s, info(s, inside=(w * 0.5, T * 0.46))


def he(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(560)
    ov = 30
    gap = 135
    s = S(c.roof(0, w), c.beak(w),
          c.stemR(w - ov, 0, T - H * 0.5), c.fillet(w - ov - V, T - H, -1, -1),
          c.stem(w * 0.15, 0, T - H - gap))
    return s, info(s, inside=(((w * 0.15 + V) + (w - 30 - V)) / 2, T * 0.30))


def het(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(570)
    s = S(c.roof(0, w), c.beak(w),
          c.stemR(w - 30, 0, T - H * 0.5), c.fillet(w - 30 - V, T - H, -1, -1),
          c.stem(w * 0.10, 0, T - H * 0.5), c.fillet(w * 0.10 + V, T - H, 1, -1))
    return s, info(s, inside=(w * 0.5, T * 0.4))


def vav(c):
    T, H, V = c.T, c.H, c.V
    tab = c.W(66)
    xs = tab + 6
    s = S(c.headL(xs - tab, xs + V), c.stem(xs, 0, T - H * 0.5))
    return s, info(s, inside=(xs - 40, T * 0.40), below_x=xs + V / 2)


def zayin(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(410)
    xs = w * 0.50 - V / 2
    s = S(c.roof(0, w), c.stem(xs, 0, T - H * 0.5), c.fillet(xs, T - H, -1, -1), c.fillet(xs + V, T - H, 1, -1))
    return s, info(s, inside=(xs - 62, T * 0.38))


def yod(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(210)
    head = c.roof(0, w * 0.92, T)
    tail = c.pen(Pth(w * 0.66, T - H * 0.5).C(w * 0.66, T * 0.66, w * 0.44, T * 0.56, w * 0.30, T * 0.40))
    s = S(head, tail)
    return s, info(s, inside=(w * 0.17, T * 0.70))


def tet(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(560)
    xl = V / 2
    xr = w - V / 2
    yt = T - H / 2
    p = Pth(xl, T - 0.5).L(xl, 0.34 * T + 20)
    p.arc(w * 0.5, 0.36 * T + 4, w * 0.5 - V / 2, 0.36 * T - H / 2 + 14, 180, 360)
    p.L(xr, yt - 60)
    p.arc(xr - 90, yt - 60, 90, 60, 0, 90)
    s1 = c.pen(p)
    # inner hook: the roof runs left and curls down into the bowl; in Bold it is shorter so the counter stays open
    k = 0.62 if c.bold else 1.0
    q = Pth(xr - 90, yt).L(w * (0.56 if c.bold else 0.50), yt).C(w * 0.40, yt, w * 0.34, yt - 40 * k, w * 0.34, yt - 170 * k)
    s = S(s1, c.pen(q))
    if not c.bold:
        s.add(rect(0, T - H * 0.6, V * 1.6, T))
    return s, info(s, inside=(w * 0.52, T * 0.26))


def kaf(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(480)
    R = 160
    xr = w - V / 2
    yt = T - H / 2
    yb = H / 2
    p = Pth(0, yt).L(xr - R, yt).arc(xr - R, yt - R, R, R, 90, 0).L(xr, yb + R)
    p.arc(xr - R, yb + R, R, R, 0, -90).L(0, yb)
    s = S(c.pen(p), c.roof(0, H * 1.4), c.base(0, H * 1.4))
    return s, info(s, inside=(w * 0.46, T * 0.5))


def kaf_final(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(430)
    R = 130
    xr = w - V / 2
    yt = T - H / 2
    p = Pth(0, yt).L(xr - R, yt).arc(xr - R, yt - R, R, R, 90, 0).L(xr, c.DESC)
    s = S(c.pen(p), c.roof(0, H * 1.4),
          poly([(xr - V / 2 - 26, c.DESC), (xr + V / 2, c.DESC),
                (xr + V / 2, c.DESC + H * 0.5), (xr - V / 2, c.DESC + H * 0.55)]))
    return s, info(s, inside=(w * 0.46, T * 0.5), below=(xr - V / 2 - c.below_off(), -110), belowW=(xr - V / 2 - c.below_off(True), -110))


def lamed(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(480)
    A = c.ASC
    xs = w * 0.26
    yc = T * 0.60 - H / 2
    stem = c.stem(xs, T * 0.50, A - H * 0.5, flare=False)
    head = c.headL(xs - c.W(64), xs + V, A)
    bowl = Pth(xs + V / 2, yc).C(xs + 120, yc, w - V / 2, yc, w - V / 2, yc - 110)
    bowl.L(w - V / 2, T * 0.30).C(w - V / 2, T * 0.10, w * 0.62, H * 0.15, w * 0.34, H * 0.5)
    s = S(stem, head, c.pen(bowl))
    return s, info(s, inside=(w * 0.60, T * 0.26), above=(xs, A + 20))


def mem(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(590)
    R = 120
    xr = w - V / 2
    yt, yb = T - H / 2, H / 2
    right = Pth(w * 0.34, yt).L(xr - R * 0.8, yt).arc(xr - R * 0.8, yt - R * 0.8, R * 0.8, R * 0.8, 90, 0).L(xr, yb + R)
    right.arc(xr - R, yb + R, R, R, 0, -90).L(w * 0.24, yb)
    # left belly: a heavier curved stroke (diagonal parts of the pen are thick); narrow slit to the roof, small gap at the foot
    left = Pth(w * 0.17, 0.86 * T).C(w * 0.02, 0.72 * T, w * 0.00, 0.34 * T, w * 0.12, 6)
    head = c.roof(w * 0.05, w * 0.325, T * 0.985)
    s = S(c.pen(right), stroke(left, V * 1.55, H * 0.90), head, c.roof(w * 0.34, w * 0.50))
    return s, info(s, inside=(w * 0.60, T * 0.44))


def mem_final(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(540)
    R = 74
    xl, xr = V / 2, w - V / 2
    yt, yb = T - H / 2, H / 2
    p = Pth(xl, yb + R).L(xl, yt - R).arc(xl + R, yt - R, R, R, 180, 90).L(xr - R, yt)
    p.arc(xr - R, yt - R, R, R, 90, 0).L(xr, yb + R).arc(xr - R, yb + R, R, R, 0, -90).L(xl + R, yb)
    p.arc(xl + R, yb + R, R, R, -90, -180).close()
    s = S(c.pen(p))
    return s, info(s, inside=(w * 0.5, T * 0.5))


def nun(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(400)
    xr = w - V / 2
    yt = T - H / 2
    R = 100
    p = Pth(w * 0.46, yt).L(xr - R * 0.7, yt).arc(xr - R * 0.7, yt - R * 0.7, R * 0.7, R * 0.7, 90, 0)
    p.L(xr, H / 2 + R * 0.8).arc(xr - R * 0.8, H / 2 + R * 0.8, R * 0.8, R * 0.8, 0, -90).L(0, H / 2)
    s = S(c.pen(p), c.roof(w * 0.34, w * 0.6), c.base(0, H * 1.2))
    return s, info(s, inside=(w * 0.55, T * 0.45))


def nun_final(c):
    T, H, V = c.T, c.H, c.V
    tab = c.W(66)
    xs = tab + 6
    s = S(c.headL(xs - tab, xs + V), c.stem(xs, c.DESC, T - H * 0.5))
    return s, info(s, inside=(xs - 40, T * 0.40), below=(xs - c.below_off(), -110),
                   belowW=(xs - c.below_off(True), -110))


def samekh(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(520)
    OS = 10   # optical overshoot of round letters
    p = Pth(w - V / 2, T / 2).arc(w / 2, T / 2, w / 2 - V / 2, T / 2 + OS - H / 2, 0, 360).close()
    s = S(c.pen(p))
    return s, info(s, inside=(w * 0.5, T * 0.5))


def ayin(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(560)
    diag = stroke(line(w - V * 0.7, T - H * 0.5, w * 0.13, H * 0.5), V * 1.45, H * 0.62)
    arm = Pth(w * 0.15, T - H / 2).C(w * 0.15, 0.62 * T, w * 0.26, 0.50 * T, w * 0.33, 0.40 * T)
    arm.C(w * 0.35, 0.36 * T, w * 0.36, 0.33 * T, w * 0.38, 0.28 * T)
    s = S(c.pen(arm), diag, c.roof(w * 0.66, w, T), c.beak(w), c.roof(0, w * 0.34, T), c.base(w * 0.05, w * 0.50))
    s.clip(-5, -5, w + 5, T)
    return s, info(s, inside=(w * 0.72, T * 0.30))


def pe(c, final=False):
    T, H, V = c.T, c.H, c.V
    w = c.W(530)
    R = 130
    xr = w - V / 2
    yt, yb = T - H / 2, H / 2
    p = Pth(w * 0.20, yt).L(xr - R, yt).arc(xr - R, yt - R, R, R, 90, 0)
    if final:
        p.L(xr, c.DESC)
    else:
        p.L(xr, yb + R).arc(xr - R, yb + R, R, R, 0, -90).L(w * 0.10, yb)
    head = c.roof(0, w * 0.30, T)
    # left side: curved stem from the head that turns inward into the tongue
    tongue = Pth(w * 0.14, T - H).C(w * 0.03, 0.80 * T, w * 0.03, 0.52 * T, w * 0.18, 0.46 * T).L(w * 0.52, 0.44 * T)
    parts = [c.pen(p), head, c.pen(tongue)]
    if not final:
        parts.append(c.base(0, w * 0.32))
    else:
        parts.append(poly([(xr - V / 2 - 26, c.DESC), (xr + V / 2, c.DESC),
                           (xr + V / 2, c.DESC + H * 0.5), (xr - V / 2, c.DESC + H * 0.55)]))
    s = S(*parts)
    kw = dict(inside=(w * 0.66, T * 0.26))
    if final:
        kw['below'] = (xr - V / 2 - c.below_off(), -110)
        kw['belowW'] = (xr - V / 2 - c.below_off(True), -110)
    return s, info(s, **kw)


def pe_final(c):
    return pe(c, True)


def tsadi(c, final=False):
    T, H, V = c.T, c.H, c.V
    w = c.W(540)
    thick = (V * 1.45, H * 0.60)
    if not final:
        xl = w * 0.14
        s = S(c.base(w * 0.10, w),
              c.stem(xl, H * 0.5, T * 0.84, flare=False),
              c.headL(0, xl + V, T * 0.94),
              stroke(line(w * 0.80, T - H * 0.6, w * 0.24, H * 0.8), *thick),
              c.roof(w * 0.66, w, T), c.beak(w))
        s.clip(-5, -5, w + 5, T)
        return s, info(s, inside=(w * 0.70, T * 0.30))
    jx, jy = w * 0.52, T * 0.36
    s = S(c.headL(0, w * 0.30, T * 0.94),
          stroke(line(w * 0.16, T * 0.80, jx, jy), V * 1.25, H * 0.55),
          c.roof(w * 0.66, w, T), c.beak(w),
          stroke(line(w * 0.80, T - H * 0.6, jx, jy), *thick),
          c.stem(jx - V / 2, c.DESC, jy + 40))
    s.clip(-5, c.DESC - 5, w + 5, T)
    return s, info(s, inside=(jx - V - 54, T * 0.22), below=(jx - V / 2 - c.below_off(), -110),
                   belowW=(jx - V / 2 - c.below_off(True), -110))


def tsadi_final(c):
    return tsadi(c, True)


def qof(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(540)
    R = 130
    xl = w * 0.10
    xr = w - V / 2
    yt = T - H / 2
    top = Pth(xl + V / 2, yt).L(xr - R, yt).arc(xr - R, yt - R, R, R, 90, 0).L(xr, 0.50 * T)
    top.C(xr, 0.36 * T, w * 0.52, 0.31 * T, xl + V, 0.30 * T)
    s = S(c.pen(top), c.stem(xl, c.DESC, T - H * 0.5), c.beakL(xl - c.W(30)), rect(xl - c.W(30), T - H, xl + V, T))
    return s, info(s, inside=(w * 0.60, T * 0.58), below=(xl - c.below_off(), -110), belowW=(xl - c.below_off(True), -110))


def shin(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(640)
    xl, xr = V / 2, w - V / 2
    yb = H / 2
    R = 110
    # outer bowl: left arm descends, round bottom, right arm ascends
    p = Pth(xl, T - H * 0.3).L(xl, 0.38 * T).C(xl, 0.10 * T, w * 0.18, yb, w * 0.40, yb)
    p.L(w * 0.66, yb).C(xr - 5, yb, xr, 0.2 * T, xr, 0.42 * T).L(xr, T - H * 0.3)
    mid = Pth(w * 0.50, yb + 20).L(w * 0.50, T - H * 0.3)
    s = S(c.pen(p), c.pen(mid))
    # little roofs at each prong top (chiselled flags)
    for xc in (xl, w * 0.50, xr):
        s.add(poly([(xc - V * 1.9, T), (xc + V / 2, T), (xc + V / 2, T - H * 0.9),
                    (xc - V / 2, T - H * 0.9), (xc - V * 1.9, T - H * 0.40)]))
    return s, info(s, inside=(w * 0.26, T * 0.50), dot_r=(w * 0.80, T + 48),
                   dot_l=(xl + 10, T + 48), hol=(w * 0.50, T + 48))


def tav(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(590)
    ov = 30
    xl = w * 0.17
    s = S(c.roof(0, w), c.beak(w), c.stemR(w - ov, 0, T - H * 0.5), c.fillet(w - ov - V, T - H, -1, -1),
          c.stem(xl, 0, T - H * 0.5, flare=False), c.fillet(xl + V, T - H, 1, -1), c.base(0, xl + V))
    return s, info(s, inside=(w * 0.5, T * 0.42))


def alef(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(600)
    a_d, a_a = 46 + 0.50 * V, 40 + 0.42 * V
    diag = stroke(line(w * 0.22, T, w * 0.78, 0), a_d, H * 0.80)
    ur = Pth(w * 0.58, 0.46 * T).C(w * 0.70, 0.53 * T, w * 0.83, 0.58 * T, w * 0.83, 0.76 * T).L(w * 0.83, T - H * 0.5)
    ll = Pth(w * 0.42, 0.54 * T).C(w * 0.30, 0.47 * T, w * 0.17, 0.42 * T, w * 0.17, 0.24 * T).L(w * 0.17, H * 0.5)
    s = S(diag, stroke(ur, a_a, H * 0.70), stroke(ll, a_a, H * 0.70), c.roof(w * 0.68, w, T), c.base(0, w * 0.34))
    s.clip(-5, 0, w + 5, T)
    return s, info(s, inside=(w * 0.17, T * 0.78))


def bet(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(560)
    R = 34
    xr = w - 64 - V / 2
    yt = T - H / 2
    yb = H / 2
    p = Pth(0, yt).L(xr - R, yt).arc(xr - R, yt - R, R, R, 90, 0).L(xr, yb)
    s = S(c.pen(p), c.roof(0, H * 1.4), c.base(0, w),
          poly([(w - 22, 0), (w, 0), (w, H * 0.8), (w - 22, H)]))
    return s, info(s, inside=(w * 0.42, T * 0.5))


def gimel(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(520)
    xs = w * 0.70
    stem = c.stem(xs, 0, T - H * 0.5)
    head = c.headL(xs - c.W(72), xs + V)
    leg = stroke(line(xs + V * 0.2, 0.50 * T, w * 0.20, H * 0.6), V * 1.35, H * 0.58)
    s = S(stem, head, leg, c.base(w * 0.04, w * 0.40), c.fillet(xs, T - H, -1, -1))
    s.clip(-5, 0, w + 5, T)
    return s, info(s, inside=(w * 0.38, T * 0.60))


GLYPHS = {
    0x05D0: ("alef", alef), 0x05D1: ("bet", bet), 0x05D2: ("gimel", gimel),
    0x05D3: ("dalet", dalet), 0x05D4: ("he", he), 0x05D5: ("vav", vav),
    0x05D6: ("zayin", zayin), 0x05D7: ("het", het), 0x05D8: ("tet", tet),
    0x05D9: ("yod", yod), 0x05DA: ("finalkaf", kaf_final), 0x05DB: ("kaf", kaf),
    0x05DC: ("lamed", lamed), 0x05DD: ("finalmem", mem_final), 0x05DE: ("mem", mem),
    0x05DF: ("finalnun", nun_final), 0x05E0: ("nun", nun), 0x05E1: ("samekh", samekh),
    0x05E2: ("ayin", ayin), 0x05E3: ("finalpe", pe_final), 0x05E4: ("pe", pe),
    0x05E5: ("finaltsadi", tsadi_final), 0x05E6: ("tsadi", tsadi), 0x05E7: ("qof", qof),
    0x05E8: ("resh", resh), 0x05E9: ("shin", shin), 0x05EA: ("tav", tav),
}
