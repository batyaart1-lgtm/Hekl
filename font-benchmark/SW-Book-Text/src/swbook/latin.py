"""Latin / digits / punctuation constructions (original, parametric).

Vertical-stress serif: elliptical pen that is wide horizontally (thick
verticals, hairline horizontals) with slab-ish unbracketed serifs.
"""
import math
from .geom import *


class LCtx:
    C = 700      # cap height / lining digit height (matches Hebrew height)
    X = 470      # x-height
    A = 745      # ascender
    D = -215     # descender

    def __init__(self, a, b, wf, name):
        self.a, self.b, self.wf, self.name = a, b, wf, name
        self.hair = b * 1.25
        self.sw = a * 1.15 + 20      # half serif length
        self.bold = name == "Bold"

    # strokes
    def pen(self, p, cap=BUTT):
        return stroke(p, self.a, self.b, cap, RJOIN)

    def thin(self, p, cap=BUTT):
        return stroke(p, self.hair, self.hair, cap, RJOIN)

    def thick(self, p, cap=BUTT):
        """Heavy diagonal stroke."""
        return stroke(p, self.a * 0.98, self.b * 1.1, cap, RJOIN)

    def v(self, x, y0, y1):
        return rect(x - self.a / 2, y0, x + self.a / 2, y1)

    def h(self, x0, x1, y):
        return rect(x0, y - self.b / 2, x1, y + self.b / 2)

    def sb(self, x, y=0, half=None):
        s = half or self.sw
        return rect(x - s, y, x + s, y + self.b * 1.05)

    def st(self, x, y, half=None):
        s = half or self.sw
        return rect(x - s, y - self.b * 1.05, x + s, y)

    def stl(self, x, y):
        """top-left flag serif"""
        return poly([(x - self.a / 2 - self.sw * 0.95, y - self.b * 1.05),
                     (x + self.a / 2, y - self.b * 1.05), (x + self.a / 2, y),
                     (x - self.a / 2 - self.sw * 0.95 + 6, y)])

    def ell(self, cx, cy, rx, ry):
        return self.pen(Pth(cx + rx, cy).arc(cx, cy, rx, ry, 0, 360).close())


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


def bowl_right(c, xs, ytop, ybot, wmax, stem_side="left"):
    """D/P/B/b style bowl hanging off a stem at xs; returns path centre-line."""
    a, b = c.a, c.b
    ry = (ytop - ybot) / 2
    cy = (ytop + ybot) / 2
    rx = max(40, wmax - xs - a / 2 - ry * 0.0) * 0.55
    xc = wmax - a / 2 - rx
    p = Pth(xs, ytop).L(xc, ytop).arc(xc, cy, rx, ry, 90, -90).L(xs, ybot)
    return p


# ============================ UPPERCASE ==================================
def bowl_left(c, xs, ytop, ybot, wmin):
    """Mirror image of bowl_right (bowl to the left of a stem at xs)."""
    a = c.a
    ry = (ytop - ybot) / 2
    cy = (ytop + ybot) / 2
    rx = max(40, xs - wmin - a / 2) * 0.55
    xc = wmin + a / 2 + rx
    return Pth(xs, ytop).L(xc, ytop).arc(xc, cy, rx, ry, 90, 270).L(xs, ybot)


def U_A(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 700
    s = S(c.thick(line(w * 0.50, C, w * 0.12, 0)),
          c.thin(line(w * 0.52, C, w * 0.88, 0)),
          c.h(w * 0.20, w * 0.80, C * 0.24 + b / 2))
    s.add(c.sb(w * 0.12 - 0, 0, c.sw * 0.9)).add(c.sb(w * 0.88, 0, c.sw * 0.9))
    s.add(c.st(w * 0.5, C, c.sw * 0.5))
    s.clip(-30, 0, w + 30, C)
    return s, info(s, top=(w * 0.5, C))


def U_B(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 600
    xs = c.sw
    mid = C * 0.53
    t = bowl_right(c, xs, C - b / 2, mid + b / 2, w * 0.86)
    l = bowl_right(c, xs, mid - b / 2, b / 2, w)
    s = S(c.pen(t), c.pen(l), c.v(xs, 0, C), c.sb(xs), c.st(xs, C))
    s.add(rect(xs - c.sw, 0, xs - a / 2, b * 1.05)) if False else None
    return s, info(s)


def U_C(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 640
    cx, cy, rx, ry = w / 2, C / 2, w / 2 - a / 2, C / 2 - b / 2
    p = Pth(cx, cy)
    p = Pth(cx + rx * math.cos(math.radians(38)), cy + ry * math.sin(math.radians(38)))
    p.arc(cx, cy, rx, ry, 38, 322)
    s = S(c.pen(p), c.v(cx + rx * math.cos(math.radians(38)) - 0, C * 0.70, C * 0.88) if False else rect(0, 0, 0, 0))
    s.add(poly([(w - a * 1.0 - 12, C * 0.84), (w - 4, C * 0.84), (w - 4, C * 0.70), (w - a * 1.0 - 12, C * 0.76)]))
    return s, info(s)


def U_D(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 700
    xs = c.sw
    p = bowl_right(c, xs, C - b / 2, b / 2, w)
    s = S(c.pen(p), c.v(xs, 0, C), c.sb(xs), c.st(xs, C))
    return s, info(s)


def U_E(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 580
    xs = c.sw
    s = S(c.v(xs, 0, C), c.h(xs, w - 10, C - b / 2), c.h(xs, w - 10, b / 2),
          c.h(xs, w * 0.78, C * 0.52),
          c.sb(xs), c.st(xs, C),
          rect(w - 8 - b * 0.4, C - b * 3.2, w - 8, C), rect(w - 8 - b * 0.4, 0, w - 8, b * 3.2),
          rect(w * 0.78 - b * 0.4, C * 0.52 - b * 1.6, w * 0.78, C * 0.52 + b * 1.6))
    return s, info(s)


def U_F(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 560
    xs = c.sw
    s = S(c.v(xs, 0, C), c.h(xs, w - 10, C - b / 2), c.h(xs, w * 0.75, C * 0.50),
          c.sb(xs), c.st(xs, C),
          rect(w - 8 - b * 0.4, C - b * 3.2, w - 8, C),
          rect(w * 0.75 - b * 0.4, C * 0.50 - b * 1.6, w * 0.75, C * 0.50 + b * 1.6))
    return s, info(s)


def U_G(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 700
    cx, cy, rx, ry = w / 2, C / 2, w / 2 - a / 2, C / 2 - b / 2
    p = Pth(cx + rx * math.cos(math.radians(38)), cy + ry * math.sin(math.radians(38)))
    p.arc(cx, cy, rx, ry, 38, 360 - 18)
    s = S(c.pen(p), c.v(w - a / 2, C * 0.08, C * 0.50), c.h(w * 0.52, w, C * 0.50 + b / 2),
          c.sb(w - a / 2 - 0, 0, c.sw * 0.0 + 1) if False else rect(0, 0, 0, 0))
    s.add(poly([(w - a - 12, C * 0.84), (w - 4, C * 0.84), (w - 4, C * 0.70), (w - a - 12, C * 0.76)]))
    s.add(rect(w - a - c.sw * 0.7, 0, w + c.sw * 0.4, b * 1.0)) if False else None
    return s, info(s)


def U_H(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 740
    x1, x2 = c.sw, w - c.sw
    s = S(c.v(x1, 0, C), c.v(x2, 0, C), c.h(x1, x2, C * 0.50),
          c.sb(x1), c.sb(x2), c.st(x1, C), c.st(x2, C))
    return s, info(s)


def U_I(c):
    a, b, C = c.a, c.b, c.C
    w = c.sw * 2
    x = w / 2
    s = S(c.v(x, 0, C), c.sb(x), c.st(x, C))
    return s, info(s)


def U_J(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 380
    x = w - c.sw
    p = Pth(x, C).L(x, C * 0.22).arc(x - C * 0.17, C * 0.22, C * 0.17 - 0, C * 0.17, 0, -140)
    s = S(c.pen(p), c.st(x, C, c.sw * 1.0))
    s.clip(-20, -12, w + 60, C)
    return s, info(s)


def U_K(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 660
    xs = c.sw
    s = S(c.v(xs, 0, C), c.sb(xs), c.st(xs, C),
          c.thin(line(w - 8, C, xs + a / 2, C * 0.36)),
          c.thick(line(xs + a * 0.7, C * 0.46, w - 20, 0)),
          c.st(w - 10, C, c.sw * 0.9), c.sb(w - 20, 0, c.sw * 0.9))
    s.clip(-20, 0, w + 20, C)
    return s, info(s)


def U_L(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 540
    xs = c.sw
    s = S(c.v(xs, 0, C), c.h(xs, w, b / 2), c.sb(xs), c.st(xs, C),
          rect(w - b * 0.4, 0, w, b * 3.4))
    return s, info(s)


def U_M(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 900
    x1, x2 = c.sw, w - c.sw
    s = S(c.v(x1, 0, C), c.v(x2, 0, C), c.thick(line(x1, C, w * 0.5, 0)),
          c.thick(line(w * 0.5, 0, x2, C)),
          c.sb(x1), c.sb(x2), c.st(x1, C, c.sw * 0.8), c.st(x2, C, c.sw * 0.8))
    s.clip(0, 0, w, C)
    return s, info(s)


def U_N(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 760
    x1, x2 = c.sw, w - c.sw
    s = S(c.v(x1, 0, C), c.v(x2, 0, C), c.thick(line(x1, C, x2, 0)),
          c.sb(x1), c.sb(x2), c.st(x1, C), c.st(x2, C, c.sw * 0.8))
    s.clip(0, 0, w, C)
    return s, info(s)


def U_O(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 740
    s = S(c.ell(w / 2, C / 2, w / 2 - a / 2, C / 2 - b / 2))
    return s, info(s)


def U_P(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 580
    xs = c.sw
    p = bowl_right(c, xs, C - b / 2, C * 0.44, w)
    s = S(c.pen(p), c.v(xs, 0, C), c.sb(xs), c.st(xs, C))
    return s, info(s)


def U_Q(c):
    s, i = U_O(c)
    w = c.wf * 740
    s.add(c.thick(line(w * 0.55, C_ := c.C * 0.18, w * 0.80, -c.C * 0.14)))
    return s, info(s)


def U_R(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 650
    xs = c.sw
    p = bowl_right(c, xs, C - b / 2, C * 0.44, w * 0.92)
    s = S(c.pen(p), c.v(xs, 0, C), c.sb(xs), c.st(xs, C),
          c.thick(line(w * 0.40, C * 0.44, w - 40, 0)), c.sb(w - 40, 0, c.sw * 0.9))
    s.clip(-20, 0, w + 20, C)
    return s, info(s)


def U_S(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 540
    p = Pth(w * 0.88, C * 0.80).C(w * 0.86, C * 0.96, w * 0.66, C - b / 2, w * 0.48, C - b / 2)
    p.C(w * 0.2, C - b / 2, w * 0.10, C * 0.80, w * 0.12, C * 0.70)
    p.C(w * 0.14, C * 0.56, w * 0.40, C * 0.52, w * 0.54, C * 0.46)
    p.C(w * 0.78, C * 0.40, w * 0.92, C * 0.32, w * 0.90, C * 0.22)
    p.C(w * 0.88, C * 0.08, w * 0.70, b / 2, w * 0.46, b / 2)
    p.C(w * 0.22, b / 2, w * 0.10, C * 0.12, w * 0.08, C * 0.24)
    s = S(c.pen(p))
    s.add(rect(w * 0.88 - b * 0.5, C * 0.66, w * 0.88 + b * 0.0 + 2, C * 0.80))
    s.add(rect(w * 0.08 - 2, C * 0.18, w * 0.08 + b * 0.5, C * 0.32))
    return s, info(s)


def U_T(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 640
    x = w / 2
    s = S(c.v(x, 0, C - b / 2), c.h(0, w, C - b / 2), c.sb(x),
          rect(0, C - b * 3.4, b * 0.4, C), rect(w - b * 0.4, C - b * 3.4, w, C))
    return s, info(s)


def U_U(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 740
    x1, x2 = c.sw, w - c.sw
    r = (x2 - x1) / 2
    p = Pth(x1, C).L(x1, r * 0.9 + 0).arc((x1 + x2) / 2, r * 0.9, r, r * 0.9, 180, 360).L(x2, C)
    s = S(c.pen(p), c.st(x1, C), c.st(x2, C, c.sw * 0.8), c.v(x2, r * 0.9, C))
    s.add(rect(x1 + 0, b * 0, x1 + 0, 0))
    s.clip(0, -b * 0.4, w, C)
    return s, info(s)


def U_V(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 700
    s = S(c.thick(line(w * 0.12, C, w * 0.48, 0)), c.thin(line(w * 0.52, 0, w * 0.88, C)),
          c.st(w * 0.12, C, c.sw * 0.95), c.st(w * 0.88, C, c.sw * 0.95))
    s.clip(0, 0, w, C)
    return s, info(s)


def U_W(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 1000
    s = S(c.thick(line(w * 0.07, C, w * 0.27, 0)), c.thin(line(w * 0.27, 0, w * 0.50, C)),
          c.thick(line(w * 0.50, C, w * 0.73, 0)), c.thin(line(w * 0.73, 0, w * 0.93, C)),
          c.st(w * 0.07, C, c.sw * 0.9), c.st(w * 0.50, C, c.sw * 0.6), c.st(w * 0.93, C, c.sw * 0.9))
    s.clip(0, 0, w, C)
    return s, info(s)


def U_X(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 700
    s = S(c.thick(line(w * 0.13, C, w * 0.87, 0)), c.thin(line(w * 0.87, C, w * 0.13, 0)),
          c.st(w * 0.12, C, c.sw * 0.95), c.st(w * 0.88, C, c.sw * 0.95),
          c.sb(w * 0.12, 0, c.sw * 0.95), c.sb(w * 0.88, 0, c.sw * 0.95))
    s.clip(0, 0, w, C)
    return s, info(s)


def U_Y(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 680
    s = S(c.thick(line(w * 0.12, C, w * 0.50, C * 0.40)), c.thin(line(w * 0.88, C, w * 0.50, C * 0.40)),
          c.v(w * 0.5, 0, C * 0.42), c.sb(w * 0.5),
          c.st(w * 0.12, C, c.sw * 0.95), c.st(w * 0.88, C, c.sw * 0.95))
    s.clip(0, 0, w, C)
    return s, info(s)


def U_Z(c):
    a, b, C = c.a, c.b, c.C
    w = c.wf * 620
    s = S(c.h(0, w, C - b / 2), c.h(0, w, b / 2), c.thick(line(w * 0.88, C - b, w * 0.12, b)),
          rect(0, C - b * 3.4, b * 0.4, C), rect(w - b * 0.4, 0, w, b * 3.4))
    s.clip(0, 0, w, C)
    return s, info(s)


# ============================ lowercase ==================================
def l_stem_top(c, x, y):
    return c.stl(x, y)


def l_a(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 500
    xs = w - c.sw * 0.5
    ry = X * 0.27
    # bowl
    p = Pth(xs, X * 0.50).C(xs - 20, X * 0.50, w * 0.10, X * 0.50, w * 0.10, X * 0.20)
    p.C(w * 0.10, -b * 0.3, w * 0.30, b / 2, xs - 40, X * 0.18)
    top = Pth(w * 0.12, X * 0.78).C(w * 0.20, X - b / 2, w * 0.60, X + 6, xs, X * 0.72).L(xs, 0)
    s = S(c.pen(Pth(xs - 6, X * 0.50).C(w * 0.55, X * 0.52, w * 0.14, X * 0.50, w * 0.13, X * 0.22).C(w * 0.13, b / 2, w * 0.45, 0, xs, X * 0.12)),
          c.pen(top), c.v(xs, 0, X * 0.72), c.sb(xs + c.sw * 0.25, 0, c.sw * 0.9))
    s.add(rect(w * 0.06, X * 0.74 - 6, w * 0.06 + a * 0.95, X * 0.80))
    return s, info(s)


def l_b(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 520
    xs = c.sw
    s = S(c.v(xs, 0, c.A), c.stl(xs, c.A), c.sb(xs),
          c.pen(bowl_right(c, xs, X - b / 2, b / 2, w)))
    return s, info(s)


def l_c(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 450
    cx, cy, rx, ry = w / 2, X / 2, w / 2 - a * 0.4, X / 2 - b / 2
    p = Pth(cx + rx * math.cos(math.radians(36)), cy + ry * math.sin(math.radians(36)))
    p.arc(cx, cy, rx, ry, 36, 324)
    s = S(c.pen(p))
    s.add(poly([(w - a * 0.9 - 8, X * 0.78), (w - 4, X * 0.82), (w - 4, X * 0.58), (w - a * 0.9 - 8, X * 0.64)]))
    return s, info(s)


def l_d(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 520
    xs = w - c.sw * 0.6
    s = S(c.v(xs, 0, c.A), c.stl(xs, c.A), c.sb(xs + c.sw * 0.25, 0, c.sw * 0.9),
          c.pen(bowl_left(c, xs, X - b / 2, b / 2, 0)))
    return s, info(s)


def l_e(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 470
    cx, cy, rx, ry = w / 2, X / 2, w / 2 - a * 0.4, X / 2 - b / 2
    p = Pth(cx + rx, cy).arc(cx, cy, rx, ry, 0, 322)
    s = S(c.pen(p), c.h(cx - rx, cx + rx, cy))
    return s, info(s)


def l_f(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 340
    xs = w * 0.42
    p = Pth(xs, 0).L(xs, c.A - 120).C(xs, c.A - 20, xs + 40, c.A - b / 2, xs + 130, c.A - b / 2)
    s = S(c.pen(p), c.h(0, xs + a * 1.2, X - b / 2), c.sb(xs),
          poly([(xs + 100, c.A), (xs + 150, c.A), (xs + 150, c.A - b * 4), (xs + 110, c.A - b * 2.5)]))
    s.clip(-20, 0, w + 40, c.A)
    return s, info(s)


def l_g(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 480
    xs = w - c.sw * 0.45
    ry = X / 2 - b / 2
    cx = w * 0.5
    bowl = c.pen(Pth(cx + (xs - cx), X / 2).arc(cx, X / 2, xs - cx, ry, 0, 360).close())
    stem = c.v(xs, c.D * 0.62, X)
    tail = c.pen(Pth(xs, c.D * 0.62).C(xs, c.D + 40, xs - 90, c.D + b * 0.5, w * 0.30, c.D + b * 0.5))
    s = S(bowl, stem, tail, c.st(xs + c.sw * 0.4, X, c.sw * 1.2))
    s.add(poly([(w * 0.30 - 4, c.D + b), (w * 0.30 + 20, c.D + b), (w * 0.30 + 6, c.D + b + 50), (w * 0.30 - 22, c.D + b + 36)]))
    s.clip(-30, c.D, w + 40, X)
    return s, info(s)


def l_h(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 560
    x1, x2 = c.sw, w - c.sw
    r = (x2 - x1) / 2
    p = Pth(x1, X * 0.50).C(x1 + 30, X - b / 2, x2 - 10, X - b / 2 + 4, x2, X * 0.40).L(x2, 0)
    s = S(c.v(x1, 0, c.A), c.stl(x1, c.A), c.pen(p), c.sb(x1), c.sb(x2))
    return s, info(s)


def l_i(c):
    a, b, X = c.a, c.b, c.X
    w = c.sw * 2
    x = w / 2
    s = S(c.v(x, 0, X), c.stl(x, X), c.sb(x), c.ell(x, 600, 0, 0) if False else circle(x, 590, a * 0.62))
    return s, info(s)


def l_j(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 300
    x = w * 0.6
    p = Pth(x, X).L(x, c.D * 0.40).C(x, c.D + 20, x - 80, c.D + b, x - 150, c.D + 40)
    s = S(c.pen(p), c.stl(x, X), circle(x, 590, a * 0.62))
    s.clip(-200, c.D, 600, X + 300)
    return s, info(s)


def l_k(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 520
    xs = c.sw
    s = S(c.v(xs, 0, c.A), c.stl(xs, c.A), c.sb(xs),
          c.thin(line(w - 15, X, xs + a / 2, X * 0.30)),
          c.thick(line(xs + a * 0.6, X * 0.38, w - 20, 0)), c.st(w - 10, X, c.sw * 0.8),
          c.sb(w - 20, 0, c.sw * 0.8))
    s.clip(-20, 0, w + 20, c.A)
    return s, info(s)


def l_l(c):
    a, b, X = c.a, c.b, c.X
    w = c.sw * 2
    x = w / 2
    s = S(c.v(x, 0, c.A), c.stl(x, c.A), c.sb(x))
    return s, info(s)


def l_m(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 840
    x1, x3 = c.sw, w - c.sw
    x2 = (x1 + x3) / 2
    p1 = Pth(x1, X * 0.50).C(x1 + 20, X - b / 2, x2 - 10, X - b / 2 + 4, x2, X * 0.40).L(x2, 0)
    p2 = Pth(x2, X * 0.50).C(x2 + 20, X - b / 2, x3 - 10, X - b / 2 + 4, x3, X * 0.40).L(x3, 0)
    s = S(c.v(x1, 0, X), c.stl(x1, X), c.pen(p1), c.pen(p2), c.sb(x1), c.sb(x2), c.sb(x3))
    return s, info(s)


def l_n(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 560
    x1, x2 = c.sw, w - c.sw
    p = Pth(x1, X * 0.50).C(x1 + 30, X - b / 2, x2 - 10, X - b / 2 + 4, x2, X * 0.40).L(x2, 0)
    s = S(c.v(x1, 0, X), c.stl(x1, X), c.pen(p), c.sb(x1), c.sb(x2))
    return s, info(s)


def l_o(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 500
    s = S(c.ell(w / 2, X / 2, w / 2 - a / 2, X / 2 - b / 2))
    return s, info(s)


def l_p(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 520
    xs = c.sw
    s = S(c.v(xs, c.D, X), c.stl(xs, X), c.sb(xs, c.D),
          c.pen(bowl_right(c, xs, X - b / 2, b / 2, w)))
    return s, info(s)


def l_q(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 520
    xs = w - c.sw * 0.6
    s = S(c.v(xs, c.D, X), c.st(xs, X, c.sw * 1.1), c.sb(xs, c.D, c.sw * 0.9),
          c.pen(bowl_left(c, xs, X - b / 2, b / 2, 0)))
    return s, info(s)


def l_r(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 390
    x1 = c.sw
    p = Pth(x1, X * 0.46).C(x1 + 20, X - b / 2, w * 0.66, X - b / 2, w * 0.88, X * 0.80)
    s = S(c.v(x1, 0, X), c.stl(x1, X), c.pen(p), c.sb(x1),
          circle(w * 0.86, X * 0.77, a * 0.46))
    return s, info(s)


def l_s(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 400
    p = Pth(w * 0.86, X * 0.76).C(w * 0.80, X * 0.94, w * 0.62, X - b / 2, w * 0.45, X - b / 2)
    p.C(w * 0.2, X - b / 2, w * 0.12, X * 0.78, w * 0.14, X * 0.68)
    p.C(w * 0.18, X * 0.54, w * 0.56, X * 0.50, w * 0.76, X * 0.40)
    p.C(w * 0.90, X * 0.32, w * 0.90, X * 0.16, w * 0.80, X * 0.08)
    p.C(w * 0.66, b / 2, w * 0.30, b / 2, w * 0.10, X * 0.20)
    s = S(c.pen(p), rect(w * 0.86 - 2, X * 0.64, w * 0.86 + a * 0.4, X * 0.78))
    return s, info(s)


def l_t(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 340
    xs = w * 0.42
    p = Pth(xs, 600).L(xs, 90).C(xs, 20, xs + 50, b / 2, xs + 120, 8)
    s = S(c.pen(p), c.h(0, w * 0.88, X - b / 2),
          poly([(xs - a / 2, 600), (xs + a / 2, 520), (xs + a / 2, 600)]))
    s.add(poly([(xs - a / 2, 590), (xs + a / 2, 590), (xs + a / 2, X - b), (xs - a / 2, X - b)]))
    s.clip(-20, 0, w + 20, 600)
    return s, info(s)


def l_u(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 560
    x1, x2 = c.sw, w - c.sw
    p = Pth(x1, X).L(x1, X * 0.30).C(x1, b, x2 - 60, b / 2, x2, X * 0.30)
    s = S(c.pen(p), c.v(x2, 0, X), c.stl(x1, X), c.st(x2, X, c.sw * 0.0 + c.sw * 0.9), c.sb(x2 + c.sw * 0.25, 0, c.sw * 0.9))
    s.clip(-20, 0, w + 20, X)
    return s, info(s)


def l_v(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 520
    s = S(c.thick(line(w * 0.10, X, w * 0.47, 0)), c.thin(line(w * 0.53, 0, w * 0.90, X)),
          c.st(w * 0.10, X, c.sw * 0.9), c.st(w * 0.90, X, c.sw * 0.9))
    s.clip(0, 0, w, X)
    return s, info(s)


def l_w(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 780
    s = S(c.thick(line(w * 0.08, X, w * 0.27, 0)), c.thin(line(w * 0.27, 0, w * 0.50, X)),
          c.thick(line(w * 0.50, X, w * 0.73, 0)), c.thin(line(w * 0.73, 0, w * 0.92, X)),
          c.st(w * 0.08, X, c.sw * 0.9), c.st(w * 0.50, X, c.sw * 0.55), c.st(w * 0.92, X, c.sw * 0.9))
    s.clip(0, 0, w, X)
    return s, info(s)


def l_x(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 500
    s = S(c.thick(line(w * 0.12, X, w * 0.88, 0)), c.thin(line(w * 0.88, X, w * 0.12, 0)),
          c.st(w * 0.12, X, c.sw * 0.9), c.st(w * 0.88, X, c.sw * 0.9),
          c.sb(w * 0.12, 0, c.sw * 0.9), c.sb(w * 0.88, 0, c.sw * 0.9))
    s.clip(0, 0, w, X)
    return s, info(s)


def l_y(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 510
    p = Pth(w * 0.90, X).L(w * 0.36, c.D * 0.62).C(w * 0.30, c.D + 20, w * 0.18, c.D + 8, w * 0.10, c.D * 0.75)
    s = S(c.thick(line(w * 0.10, X, w * 0.50, X * 0.0 + 30)),
          c.thin(line(w * 0.90, X, w * 0.40, c.D * 0.55)),
          c.st(w * 0.10, X, c.sw * 0.9), c.st(w * 0.90, X, c.sw * 0.9),
          c.thin(Pth(w * 0.40, c.D * 0.55).C(w * 0.32, c.D + 30, w * 0.20, c.D + 8, w * 0.10, c.D * 0.78)))
    s.clip(-10, c.D, w + 10, X)
    return s, info(s)


def l_z(c):
    a, b, X = c.a, c.b, c.X
    w = c.wf * 450
    s = S(c.h(0, w, X - b / 2), c.h(0, w, b / 2), c.thick(line(w * 0.86, X - b, w * 0.14, b)),
          rect(0, X - b * 3.2, b * 0.4, X), rect(w - b * 0.4, 0, w, b * 3.2))
    s.clip(0, 0, w, X)
    return s, info(s)


UPPER = {chr(ord('A') + i): f for i, f in enumerate(
    [U_A, U_B, U_C, U_D, U_E, U_F, U_G, U_H, U_I, U_J, U_K, U_L, U_M,
     U_N, U_O, U_P, U_Q, U_R, U_S, U_T, U_U, U_V, U_W, U_X, U_Y, U_Z])}
LOWER = {chr(ord('a') + i): f for i, f in enumerate(
    [l_a, l_b, l_c, l_d, l_e, l_f, l_g, l_h, l_i, l_j, l_k, l_l, l_m,
     l_n, l_o, l_p, l_q, l_r, l_s, l_t, l_u, l_v, l_w, l_x, l_y, l_z])}
