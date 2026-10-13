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


class HCtx:
    T = 650          # letter height
    ASC = 800        # lamed ascender
    DESC = -230      # final-letter descender

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
        V, H = self.V, self.H
        if flare:
            f = V * 0.55 + 6
            return poly([(xl, y1), (xl + V, y1), (xl + V, y0 + H * 0.42),
                         (xl + V + f * 0.0, y0), (xl - f, y0),
                         (xl, y0 + H * 0.55)])
        return rect(xl, y0, xl + V, y1)

    def stemR(self, xr, y0, y1, flare=True):
        return self.stem(xr - self.V, y0, y1, flare)

    def below_off(self, wide=False):
        r = 38 if self.bold else 28
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
    w = c.W(480)
    ov = 30
    s = S(c.roof(0, w), c.stemR(w - ov, 0, T - H * 0.5))
    return s, info(s, inside=(w * 0.5, T * 0.46))


def resh(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(470)
    R = 130
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
    gap = 120
    s = S(c.roof(0, w),
          c.stemR(w - ov, 0, T - H * 0.5),
          c.stem(w * 0.10, 0, T - H - gap))
    return s, info(s, inside=(w * 0.38, T * 0.34))


def het(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(570)
    s = S(c.roof(0, w),
          c.stemR(w - 30, 0, T - H * 0.5),
          c.stem(w * 0.10, 0, T - H * 0.5))
    return s, info(s, inside=(w * 0.5, T * 0.4))


def vav(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(250)
    xs = w * 0.52 - V / 2
    head = poly([(xs - V * 0.6, T), (xs + V + c.W(70), T),
                 (xs + V + c.W(70), T - H), (xs + V, T - H),
                 (xs + V, T - H), (xs - V * 0.6, T - H)])
    head = c.roof(xs - V * 0.6, xs + V + c.W(70))
    s = S(head, c.stem(xs, 0, T - H * 0.5))
    return s, info(s, inside=(xs - 48, T * 0.40), below_x=xs + V / 2)


def zayin(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(330)
    xs = w * 0.56 - V / 2
    s = S(c.roof(0, w), c.stem(xs, 0, T - H * 0.5))
    return s, info(s, inside=(xs - 52, T * 0.38))


def yod(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(190)
    s = S(c.roof(0, w, T), c.stem(w * 0.16, T * 0.46, T - H * 0.5, flare=True))
    return s, info(s, inside=(w * 0.16 + V + 62, T * 0.58))


def tet(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(560)
    xl = V / 2
    xr = w - V / 2
    yb = H / 2
    yt = T - H / 2
    p = Pth(xl + V * 0.2, T - H * 0.2).L(xl, yt - 30).L(xl, 0.34 * T + 20)
    p.arc(w * 0.5, 0.36 * T + 4, w * 0.5 - V / 2, 0.36 * T - H / 2 + 4, 180, 360)
    p.L(xr, yt - 60)
    p.arc(xr - 90, yt - 60, 90, 60, 0, 90)
    s1 = c.pen(p)
    # inner hook from the top roof curling down into the bowl
    q = Pth(xr - 90, yt).L(w * 0.42, yt).C(w * 0.33, yt, w * 0.30, yt - 40, w * 0.30, yt - 120)
    hook = c.pen(q)
    left_cap = poly([(0, T), (V * 2.2, T), (V * 2.2, T - H), (0, T - H * 0.45)])
    s = S(s1, hook, left_cap)
    return s, info(s, inside=(w * 0.52, T * 0.30))


def kaf(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(480)
    R = 120
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
    w = c.W(470)
    A = c.ASC
    xs = w * 0.30
    yt = A - H / 2
    # ascender with a hook/roof to the right
    asc = Pth(xs, T * 0.42).L(xs, A - 150).C(xs, yt - 40, xs + 20, yt, xs + 70, yt)
    asc.L(w * 0.62, yt)
    roof = c.pen(asc)
    cut = c.roof(xs - V / 2 - 6, w * 0.62, A)
    # lower body: a bowl hanging from the stem, opening to the left
    p = Pth(xs, T * 0.46).C(xs + 60, T * 0.50, w - V / 2 - 30, T * 0.50, w - V / 2, T * 0.34)
    p.C(w - V / 2, T * 0.14, w * 0.80, H / 2, w * 0.58, H / 2).L(w * 0.12, H / 2)
    body = c.pen(p)
    s = S(roof, c.stem(xs - V / 2, T * 0.42, A - 150), body,
          c.base(0, H * 1.0))
    return s, info(s, inside=(w * 0.60, T * 0.28), above=(xs, A + 20))


def mem(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(580)
    R = 100
    xl, xr = V / 2, w - V / 2
    yt, yb = T - H / 2, H / 2
    # right body: roof + right stem curving into a full-width base
    right = Pth(w * 0.50, yt).L(xr - R * 0.7, yt).arc(xr - R * 0.7, yt - R * 0.7, R * 0.7, R * 0.7, 90, 0).L(xr, yb + R)
    right.arc(xr - R, yb + R, R, R, 0, -90).L(w * 0.30, yb)
    # left body: shorter left stem (open at the top) hooking into the base
    left = Pth(xl, T * 0.54).L(xl, yb + R).arc(xl + R, yb + R, R, R, 180, 270).L(w * 0.5, yb)
    s = S(c.pen(right), c.pen(left), c.roof(w * 0.44, w * 0.6))
    # chiselled cap on the open left stem
    s.add(poly([(0, T * 0.54), (V * 1.7, T * 0.54), (V * 1.7, T * 0.54 - H * 0.75), (0, T * 0.54 - H * 0.30)]))
    return s, info(s, inside=(w * 0.62, T * 0.46))


def mem_final(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(540)
    R = 60
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
    w = c.W(350)
    xr = w - V / 2
    yt = T - H / 2
    R = 100
    p = Pth(0, yt).L(xr - R * 0.7, yt).arc(xr - R * 0.7, yt - R * 0.7, R * 0.7, R * 0.7, 90, 0).L(xr, c.DESC)
    s = S(c.pen(p), c.roof(0, H * 1.2),
          poly([(xr - V / 2 - 26, c.DESC), (xr + V / 2, c.DESC),
                (xr + V / 2, c.DESC + H * 0.5), (xr - V / 2, c.DESC + H * 0.55)]))
    return s, info(s, inside=(w * 0.42, T * 0.5), below=(xr - V / 2 - c.below_off(), -110), belowW=(xr - V / 2 - c.below_off(True), -110))


def samekh(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(520)
    p = Pth(w - V / 2, T / 2).arc(w / 2, T / 2, w / 2 - V / 2, T / 2 - H / 2, 0, 360).close()
    s = S(c.pen(p))
    return s, info(s, inside=(w * 0.5, T * 0.5))


def ayin(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(540)
    xr = w - V / 2
    yb = H / 2
    # right arm + bottom bowl
    p = Pth(xr, T - H * 0.2).L(xr, 0.42 * T).C(xr, 0.16 * T, w * 0.78, yb, w * 0.52, yb)
    p.C(w * 0.34, yb, w * 0.26, 0.12 * T, w * 0.22, 0.30 * T)
    # left arm rising to the top-left
    q = Pth(w * 0.22, 0.30 * T).C(w * 0.16, 0.50 * T, V / 2 + 14, 0.62 * T, V / 2 + 10, T - H * 0.2)
    s = S(c.pen(p), c.pen(q), c.roof(0, H * 1.8))
    s.clip(-5, -5, w + 5, T + 5)
    s.add(poly([(xr - V / 2 - 0, T), (xr + V / 2, T), (xr + V / 2, T - H), (xr - V / 2, T - H)]))
    return s, info(s, inside=(w * 0.5, T * 0.5))


def pe(c, final=False):
    T, H, V = c.T, c.H, c.V
    w = c.W(520)
    R = 120
    xr = w - V / 2
    xl = V / 2
    yt, yb = T - H / 2, H / 2
    p = Pth(xl + R, yt).L(xr - R, yt).arc(xr - R, yt - R, R, R, 90, 0)
    if final:
        p.L(xr, c.DESC)
    else:
        p.L(xr, yb + R).arc(xr - R, yb + R, R, R, 0, -90).L(xl + R, yb)
        p.arc(xl + R, yb + R, R, R, -90, -150)
    # left top: rounded corner turning down then inward tongue
    q = Pth(xl + R, yt).arc(xl + R, yt - R, R, R, 90, 180).L(xl, 0.5 * T)
    tongue = Pth(xl + R + 20, yt - H * 0.1).C(xl + R + 20, yt - 20, w * 0.38, yt - 30, w * 0.38, yt - 140)
    parts = [c.pen(p), c.pen(q), c.pen(tongue)]
    if final:
        parts.append(poly([(xr - V / 2 - 26, c.DESC), (xr + V / 2, c.DESC),
                           (xr + V / 2, c.DESC + H * 0.5), (xr - V / 2, c.DESC + H * 0.55)]))
    s = S(*parts)
    kw = dict(inside=(w * 0.5, T * 0.40))
    if final:
        kw['below'] = (xr - V / 2 - c.below_off(), -110)
        kw['belowW'] = (xr - V / 2 - c.below_off(True), -110)
    return s, info(s, **kw)


def pe_final(c):
    return pe(c, True)


def tsadi(c, final=False):
    T, H, V = c.T, c.H, c.V
    w = c.W(520)
    xr = w - V / 2
    yb = H / 2
    R = 100
    # right arm: from top right down, bowl to left
    arm = Pth(xr, T - H * 0.2).L(xr, 0.52 * T).C(xr, 0.26 * T, w * 0.66, 0.14 * T, w * 0.46, yb + 8)
    # left stem with yod-like head
    left = Pth(w * 0.12, T * 0.70).L(w * 0.12, 0.30 * T).C(w * 0.12, 0.08 * T, w * 0.26, yb, w * 0.46, yb)
    if final:
        left.L(w * 0.66, yb)
        tail = Pth(xr, 0.40 * T).L(xr, c.DESC)
        tail = c.pen(tail)
        fl = poly([(xr - V / 2 - 26, c.DESC), (xr + V / 2, c.DESC),
                   (xr + V / 2, c.DESC + H * 0.5), (xr - V / 2, c.DESC + H * 0.55)])
        parts = [tail, fl]
    else:
        left.L(w * 0.86, yb)
        parts = []
    head = c.roof(0, w * 0.34, T - 0)  # yod-like head at upper left
    s = S(c.pen(arm), c.pen(left), head, c.roof(w - H * 1.4, w, T), *parts)
    s.clip(-5, c.DESC - 5, w + 5, T + 5)
    kw = dict(inside=(w * 0.5, T * 0.5))
    if final:
        kw['below'] = (xr - V / 2 - c.below_off(), -110)
        kw['belowW'] = (xr - V / 2 - c.below_off(True), -110)
    return s, info(s, **kw)


def tsadi_final(c):
    return tsadi(c, True)


def qof(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(520)
    xr = w - V / 2
    yt = T - H / 2
    R = 120
    p = Pth(0, yt).L(xr - R, yt).arc(xr - R, yt - R, R, R, 90, 0).L(xr, 0.28 * T)
    leg = c.stem(w * 0.20, c.DESC, T - H * 0.5)
    s = S(c.pen(p), c.roof(0, H * 1.4), leg,
          poly([(xr - V / 2 - 6, 0.28 * T), (xr + V / 2, 0.28 * T), (xr + V / 2, 0.28 * T + H * 0.6),
                (xr - V / 2, 0.28 * T + H * 0.6)]))
    return s, info(s, inside=(w * 0.62, T * 0.50), below=(w * 0.2 - c.below_off(), -110), belowW=(w * 0.2 - c.below_off(True), -110))


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
        s.add(poly([(xc - V * 1.1, T), (xc + V / 2, T), (xc + V / 2, T - H * 0.9),
                    (xc - V / 2, T - H * 0.9), (xc - V * 1.1, T - H * 0.35)]))
    return s, info(s, inside=(w * 0.26, T * 0.50), dot_r=(w * 0.80, T + 48),
                   dot_l=(xl + 10, T + 48), hol=(w * 0.50, T + 48))


def tav(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(590)
    ov = 30
    xl = w * 0.10
    s = S(c.roof(0, w), c.stemR(w - ov, 0, T - H * 0.5), c.stem(xl, H, T - H * 0.5),
          c.base(0, xl + V + 10))
    return s, info(s, inside=(w * 0.5, T * 0.42))


def alef(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(600)
    # main diagonal (thin pen, so it stays light like a joined hairline-stem)
    dpen = (V * 1.25, H * 0.68)
    diag = stroke(line(w * 0.22, T - 40, w * 0.78, 40), *dpen)
    # upper-right arm: stem rising from the diagonal ending in a small roof
    ur = Pth(w * 0.66, 0.50 * T).L(w * 0.86, 0.80 * T).L(w * 0.86 - 4, T - H * 0.6)
    ul_roof = c.roof(w - H * 1.5, w, T)
    # lower-left arm
    ll = Pth(w * 0.32, 0.46 * T).L(w * 0.12, 0.22 * T).L(w * 0.12, H * 0.5)
    ll_base = c.base(0, H * 1.5)
    s = S(diag, stroke(ur, V * 1.1, H * 0.75), ul_roof, stroke(ll, V * 1.1, H * 0.75), ll_base)
    s.clip(-5, -5, w + 5, T + 5)
    return s, info(s, inside=(w * 0.17, T * 0.74))


def bet(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(560)
    R = 70
    xr = w - 60 - V / 2
    yt = T - H / 2
    yb = H / 2
    p = Pth(0, yt).L(xr - R, yt).arc(xr - R, yt - R, R, R, 90, 0).L(xr, yb)
    s = S(c.pen(p), c.roof(0, H * 1.4), c.base(0, w),
          poly([(w - 22, 0), (w, 0), (w, H * 0.8), (w - 22, H)]))
    return s, info(s, inside=(w * 0.42, T * 0.5))


def gimel(c):
    T, H, V = c.T, c.H, c.V
    w = c.W(500)
    xr = w * 0.78
    yt = T - H / 2
    R = 90
    st = Pth(w * 0.26, yt).L(xr - R * 0.7, yt).arc(xr - R * 0.7, yt - R * 0.7, R * 0.7, R * 0.7, 90, 0).L(xr, 0.42 * T)
    leg = stroke(Pth(xr, 0.44 * T).L(w * 0.30, H / 2), V * 1.15, H * 0.8)
    s = S(c.pen(st), c.roof(w * 0.16, w * 0.46), leg, c.base(0, w * 0.58))
    s.clip(-5, -5, w + 5, T + 5)
    return s, info(s, inside=(w * 0.5, T * 0.5))


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
