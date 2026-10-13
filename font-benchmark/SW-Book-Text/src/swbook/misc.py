"""Digits, punctuation, symbols and Hebrew combining marks (original)."""
import math
from .geom import *
from .latin import LCtx, S, info, bowl_right


def rot180(shape):
    b = shape.bounds()
    t = Shape()
    t.path = xform(shape.path, -1, -1, b[0] + b[2], b[1] + b[3])
    return t


def _dot(c, x, y, r=None):
    return circle(x, y, r or c.a * 0.62)


# ============================== digits ==================================
def digit(c, n):
    a, b, C = c.a, c.b, c.C
    w = 520 * c.wf
    P = c.pen
    if n == 0:
        s = S(c.ell(w / 2, C / 2, w / 2 - a / 2, C / 2 - b / 2))
    elif n == 1:
        x = w * 0.54
        s = S(c.v(x, 0, C), c.sb(x, 0, c.sw * 1.1),
              c.thick(line(x - a / 2 + 4, C - b * 0.5, w * 0.16, C * 0.80)))
        s.clip(0, 0, w, C)
    elif n == 2:
        p = Pth(w * 0.10, C * 0.76).C(w * 0.14, C * 0.96, w * 0.34, C - b / 2, w * 0.5, C - b / 2)
        p.C(w * 0.78, C - b / 2, w * 0.88, C * 0.82, w * 0.86, C * 0.68)
        p.C(w * 0.84, C * 0.52, w * 0.4, C * 0.26, w * 0.1, b * 1.1)
        s = S(P(p), c.h(w * 0.06, w * 0.94, b / 2), rect(w * 0.88, 0, w * 0.94, b * 3.0))
    elif n == 3:
        p = Pth(w * 0.12, C * 0.80).C(w * 0.18, C * 0.97, w * 0.38, C - b / 2, w * 0.50, C - b / 2)
        p.C(w * 0.76, C - b / 2, w * 0.82, C * 0.80, w * 0.80, C * 0.74)
        p.C(w * 0.76, C * 0.60, w * 0.5, C * 0.55, w * 0.36, C * 0.55)
        q = Pth(w * 0.36, C * 0.55).C(w * 0.64, C * 0.55, w * 0.86, C * 0.46, w * 0.86, C * 0.28)
        q.C(w * 0.86, C * 0.08, w * 0.66, b / 2, w * 0.46, b / 2)
        q.C(w * 0.26, b / 2, w * 0.12, C * 0.10, w * 0.08, C * 0.20)
        s = S(P(p), P(q))
    elif n == 4:
        x = w * 0.68
        s = S(c.v(x, 0, C), c.thick(line(x, C, w * 0.04, C * 0.30)), c.h(w * 0.02, w * 0.96, C * 0.30),
              c.sb(x, 0, c.sw * 1.0))
        s.clip(0, 0, w, C)
    elif n == 5:
        p = Pth(w * 0.26, C * 0.54).C(w * 0.34, C * 0.60, w * 0.5, C * 0.62, w * 0.62, C * 0.60)
        p.C(w * 0.86, C * 0.56, w * 0.88, C * 0.34, w * 0.86, C * 0.26)
        p.C(w * 0.84, C * 0.08, w * 0.66, b / 2, w * 0.44, b / 2)
        p.C(w * 0.24, b / 2, w * 0.12, C * 0.10, w * 0.08, C * 0.20)
        s = S(P(p), c.v(w * 0.26, C * 0.52, C - b), c.h(w * 0.26, w * 0.86, C - b / 2),
              rect(w * 0.86 - b * 0.4, C - b * 3, w * 0.86, C))
    elif n in (6, 9):
        p = Pth(w * 0.84, C * 0.86).C(w * 0.74, C - b / 2, w * 0.5, C - b / 2, w * 0.38, C * 0.90)
        p.C(w * 0.14, C * 0.70, w * 0.12, C * 0.40, w * 0.12, C * 0.30)
        s = S(P(p), c.ell(w / 2, C * 0.31, w * 0.40 - a / 2, C * 0.31 - b / 2))
        if n == 9:
            s = rot180(S(P(p), c.ell(w / 2, C * 0.31, w * 0.40 - a / 2, C * 0.31 - b / 2)))
    elif n == 7:
        s = S(c.h(w * 0.06, w * 0.92, C - b / 2), c.thick(line(w * 0.88, C - b, w * 0.30, 0)),
              rect(w * 0.06, C - b * 3.2, w * 0.06 + b * 0.4, C))
        s.clip(0, 0, w, C)
    elif n == 8:
        s = S(c.ell(w / 2, C * 0.75, w * 0.31 - a / 2 + 4, C * 0.25 - b / 2),
              c.ell(w / 2, C * 0.28, w * 0.40 - a / 2, C * 0.28 - b / 2))
    return s, info(s)


# ============================ punctuation ===============================
def _stroked(c, p, cap=BUTT):
    return c.pen(p, cap)


def punct(c, ch):
    a, b, C, X = c.a, c.b, c.C, c.X
    w = None
    r = a * 0.62
    hb = b * 1.4
    if ch == ' ':
        return Shape(), dict(adv=250)
    if ch == ' ':
        return Shape(), dict(adv=250)
    if ch == '.':
        s = S(circle(r + 6, r + 4, r + 6))
    elif ch == ',':
        s = S(circle(r + 6, r + 4, r + 6), c.pen(Pth(r + 10, 10).C(r + 14, -40, r - 4, -90, r - 40, -120)))
    elif ch == ':':
        s = S(circle(r + 6, r + 4, r + 6), circle(r + 6, X - r - 6, r + 6))
    elif ch == ';':
        s = S(circle(r + 6, X - r - 6, r + 6), circle(r + 6, r + 4, r + 6),
              c.pen(Pth(r + 10, 10).C(r + 14, -40, r - 4, -90, r - 40, -120)))
    elif ch == '!':
        s = S(poly([(0, C), (a * 1.25, C), (a * 0.85, C * 0.28), (a * 0.4, C * 0.28)]),
              circle(a * 0.625, r + 4, r + 6))
    elif ch == '?':
        p = Pth(60, C * 0.78).C(70, C - 10, 200, C - b / 2, 250, C - b / 2)
        p.C(400, C - b / 2, 440, C * 0.74, 380, C * 0.58).C(330, C * 0.48, 250, C * 0.44, 250, C * 0.28)
        s = S(c.pen(p), circle(250, r + 4, r + 6))
    elif ch == '"':
        s = S(poly([(0, C), (a * 1.2, C), (a * 0.8, C * 0.66), (a * 0.4, C * 0.66)]),
              poly([(a * 2.0, C), (a * 3.2, C), (a * 2.8, C * 0.66), (a * 2.4, C * 0.66)]))
    elif ch == "'":
        s = S(poly([(0, C), (a * 1.2, C), (a * 0.8, C * 0.66), (a * 0.4, C * 0.66)]))
    elif ch == '`':
        s = S(c.pen(Pth(0, C).L(a * 1.4, C * 0.78)))
    elif ch in '([{':
        h = {'(': 0, '[': 1, '{': 2}[ch]
        top, bot = C + 60, -170
        if ch == '(':
            p = Pth(230, top).C(60, top - 160, 60, bot + 160, 230, bot)
            s = S(c.pen(p))
        elif ch == '[':
            s = S(c.v(a / 2 + 40, bot, top), c.h(a / 2 + 40, 250, top - b / 2), c.h(a / 2 + 40, 250, bot + b / 2))
        else:
            mid = (top + bot) / 2
            p = Pth(240, top).C(150, top, 150, top - 60, 150, top - 120).L(150, mid + 40).C(150, mid + 10, 100, mid, 60, mid)
            q = Pth(60, mid).C(100, mid, 150, mid - 10, 150, mid - 40).L(150, bot + 120).C(150, bot + 60, 150, bot, 240, bot)
            s = S(c.pen(p), c.pen(q))
    elif ch in ')]}':
        base, i = punct(c, {')': '(', ']': '[', '}': '{'}[ch])
        b0 = base.bounds()
        xr = b0[0] + b0[2]
        s = Shape()
        s.path = xform(base.path, -1, 1, xr, 0)
    elif ch == '/':
        s = S(c.thin(line(0, -90, 330, C + 40)))
        s.clip(-10, -90, 400, C + 40)
    elif ch == '\\':
        s = S(c.thin(line(0, C + 40, 330, -90)))
    elif ch == '-':
        s = S(rect(0, X * 0.42, 260, X * 0.42 + hb * 1.2))
    elif ch == '–':
        s = S(rect(0, X * 0.42, 520, X * 0.42 + hb * 1.2))
    elif ch == '—':
        s = S(rect(0, X * 0.42, 960, X * 0.42 + hb * 1.2))
    elif ch == '+':
        s = S(c.v(240, 70, 500), c.h(30, 450, 285))
    elif ch == '−':
        s = S(c.h(30, 450, 285))
    elif ch == '±':
        s = S(c.v(240, 170, 560), c.h(30, 450, 365), c.h(30, 450, 40))
    elif ch == '×':
        s = S(c.thin(line(50, 120, 430, 480)), c.thin(line(50, 480, 430, 120)))
    elif ch == '÷':
        s = S(c.h(30, 450, 285), circle(240, 100, r * 0.85), circle(240, 470, r * 0.85))
    elif ch == '=':
        s = S(c.h(30, 450, 200), c.h(30, 450, 380))
    elif ch == '<':
        s = S(c.thin(Pth(430, 80).L(50, 290).L(430, 500)))
    elif ch == '>':
        s = S(c.thin(Pth(50, 80).L(430, 290).L(50, 500)))
    elif ch == '*':
        cx, cy, R = 200, C * 0.80, 160
        s = Shape()
        for k in range(3):
            t = math.radians(90 + k * 60)
            s.add(c.thin(line(cx - R * math.cos(t), cy - R * math.sin(t), cx + R * math.cos(t), cy + R * math.sin(t))))
    elif ch == '#':
        s = S(c.thin(line(150, -20, 230, C + 20)), c.thin(line(330, -20, 410, C + 20)),
              c.h(40, 480, C * 0.36), c.h(60, 500, C * 0.64))
    elif ch == '$':
        sg, i = U_S_small(c)
        s = S(sg, c.v(sg_w(c) / 2, -60, C + 70))
    elif ch == '%':
        s = S(c.thin(line(80, -20, 600, C + 20)),
              c.ell(150, C * 0.76, 100 - a / 2, 120 - b / 2), c.ell(530, C * 0.24, 100 - a / 2, 120 - b / 2))
    elif ch == '&':
        p = Pth(500, 60).C(420, -10, 300, b / 2, 230, b / 2)
        p.C(110, b / 2, 40, C * 0.12, 60, C * 0.28).C(80, C * 0.42, 200, C * 0.52, 260, C * 0.60)
        p.C(320, C * 0.68, 340, C * 0.80, 300, C * 0.90).C(260, C - b / 2, 140, C - b / 2, 130, C * 0.80)
        p.C(124, C * 0.68, 300, C * 0.40, 520, 0)
        s = S(c.pen(p))
        s.add(c.thin(line(300, 80, 560, C * 0.50))) if False else None
    elif ch == '@':
        s = S(c.ell(300, C * 0.38, 270 - a / 2, 300 - b / 2),
              c.ell(300, C * 0.38, 100, 100))
        s.add(c.v(400, C * 0.12, C * 0.60))
        s.clip(-5, -90, 620, C + 90)
    elif ch == '^':
        s = S(c.thin(Pth(40, C * 0.6).L(230, C + 10).L(420, C * 0.6)))
    elif ch == '_':
        s = S(rect(0, -110, 640, -110 + hb))
    elif ch == '~':
        s = S(c.pen(Pth(30, 200).C(110, 330, 190, 330, 240, 250).C(290, 170, 370, 170, 450, 300)))
    elif ch == '|':
        s = S(c.v(a / 2 + 10, -170, C + 60))
    elif ch == '·':
        s = S(circle(r + 6, X * 0.5, r + 6))
    elif ch == '•':
        s = S(circle(150, X * 0.55, 130))
    elif ch == '…':
        s = Shape()
        for i in range(3):
            s.add(circle(r + 6 + i * 250, r + 4, r + 6))
    elif ch in '‘’“”„':
        def comma_up(x):
            return S(circle(x + 56, C - 76, 56), c.pen(Pth(x + 60, C - 80).C(x + 60, C - 140, x + 20, C - 190, x - 20, C - 210)))

        def comma_down(x):
            return S(circle(x + 56, 56, 56), c.pen(Pth(x + 60, 40).C(x + 60, -20, x + 20, -80, x - 20, -100)))

        def turned(x):
            q = rot180(comma_up(0))
            q2 = Shape()
            q2.path = xform(q.path, 1, 1, x, 0)
            return q2
        if ch == '’':
            s = comma_up(0)
        elif ch == '‘':
            s = turned(0)
        elif ch == '”':
            s = S(comma_up(0).path, comma_up(190).path)
        elif ch == '“':
            s = S(turned(0).path, turned(190).path)
        else:
            s = S(comma_down(0).path, comma_down(190).path)
    elif ch in '«»':
        L = Pth(230, 80).L(60, 220).L(230, 360)
        L2 = Pth(400, 80).L(230, 220).L(400, 360)
        s = S(c.thin(L), c.thin(L2))
        if ch == '»':
            b0 = s.bounds()
            t = Shape()
            t.path = xform(s.path, -1, 1, b0[0] + b0[2], 0)
            s = t
    elif ch == '°':
        s = S(c.ell(120, C * 0.78, 100 - a / 2, 100 - b / 2))
    elif ch == '§':
        sg, i = U_S_small(c)
        top = Shape(); top.path = xform(sg.path, 0.80, 0.60, 0, C * 0.40)
        bot = Shape(); bot.path = xform(sg.path, 0.80, 0.60, 0, -C * 0.02)
        s = S(top, bot)
    elif ch == '¶':
        s = S(c.v(300, -80, C), c.v(440, -80, C), c.h(300, 600, C - b / 2),
              c.pen(Pth(300, C - b / 2).C(80, C - b / 2, 80, C * 0.50, 300, C * 0.46)))
        s.add(poly([(300, C * 0.46), (300, C - b), (200, C - b), (200, C * 0.46)])) if False else None
    elif ch == '©':
        s = S(c.ell(330, C * 0.5, 320 - a / 2, C * 0.52 - b / 2),
              c.pen(Pth(450, C * 0.36).arc(330, C * 0.5, 130, 150, -40, -320)))
    elif ch == '₪':   # new shekel sign: shin-like and lamed-like glyphs side by side
        s = S(c.pen(Pth(60, C).L(60, 90).C(60, 10, 120, b / 2, 200, b / 2).L(240, b / 2).C(300, b / 2, 330, 40, 330, 120).L(330, C * 0.45)),
              c.pen(Pth(330, C * 0.45).L(330, C * 0.45)) if False else Shape().path)
        s.add(c.v(330 + 0, C * 0.0, C)) if False else None
        s = S(c.pen(Pth(60, C).L(60, 120).C(60, 10, 120, b / 2, 200, b / 2).L(330, b / 2).L(330, C * 0.0 + b / 2)),
              c.pen(Pth(60, C).L(60, 120)),
              c.pen(Pth(350, C).L(350, 150).C(350, 30, 430, b / 2, 540, b / 2)),
              c.pen(Pth(540, C * 0.0 + b / 2).L(540, C)))
    else:
        raise KeyError(ch)
    return s, info(s)


def sg_w(c):
    return 540 * c.wf


def U_S_small(c, sc=1.0):
    from .latin import U_S
    s, i = U_S(c)
    return s, i


# ============================ Hebrew punctuation ========================
def heb_punct(c, cp):
    """c is an HCtx."""
    H, V, T = c.H, c.V, c.T
    if cp == 0x05BE:  # maqaf
        y = T * 0.46
        s = S(rect(0, y, 330, y + H * 0.75))
    elif cp == 0x05F3:  # geresh
        s = S(poly([(0, T), (V * 1.5, T), (V * 0.9, T - 190), (V * 0.2, T - 190)]))
    elif cp == 0x05F4:  # gershayim
        s = S(poly([(0, T), (V * 1.5, T), (V * 0.9, T - 190), (V * 0.2, T - 190)]),
              poly([(V * 3.4, T), (V * 4.9, T), (V * 4.3, T - 190), (V * 3.6, T - 190)]))
    elif cp == 0x05C0:  # paseq
        s = S(rect(0, -60, V * 1.1, T + 60))
    elif cp == 0x05C3:  # sof pasuq
        r = V * 0.62 + 12
        s = S(circle(r, T * 0.12 + r, r), circle(r, T * 0.62 - r, r))
    elif cp == 0x05C6:  # nun hafukha
        s = S(rect(0, 0, 0, 0))
    else:
        raise KeyError(cp)
    return s, info(s)


# ============================ combining marks ===========================
class MarkCtx:
    def __init__(self, hc):
        self.r = hc.mark_r
        self.t = hc.H * 0.62
        self.V = hc.V


def mk(hc, cp):
    """Return (shape, kind).  Below marks hang from y=0; above marks stand
    on y=0; the dagesh is centred on the origin."""
    m = MarkCtx(hc)
    r, t, V = m.r, m.t, m.V

    def dot(x, y, rr=None):
        return circle(x, y, rr or r)

    def sheva(x):
        return [dot(x, -r - 6), dot(x, -r * 3.4 - 6)]

    def patah(x, wd=r * 4.6):
        return [rect(x - wd / 2, -t - 6, x + wd / 2, -6)]

    def segol(x):
        return [dot(x - r * 1.7, -r - 6), dot(x + r * 1.7, -r - 6), dot(x, -r * 3.3 - 6)]

    def qamats(x):
        return patah(x) + [rect(x - V * 0.55, -t - 6 - r * 3.0, x + V * 0.55, -t - 5)]

    k = "below"
    if cp == 0x05B0:
        parts = sheva(0)
    elif cp == 0x05B1:
        parts = sheva(-r * 2.9) + segol(r * 2.6)
    elif cp == 0x05B2:
        parts = sheva(-r * 2.9) + patah(r * 2.6, r * 4.2)
    elif cp == 0x05B3:
        parts = sheva(-r * 2.9) + qamats(r * 2.6)
    elif cp == 0x05B4:
        parts = [dot(0, -r - 6)]
    elif cp == 0x05B5:
        parts = [dot(-r * 1.7, -r - 6), dot(r * 1.7, -r - 6)]
    elif cp == 0x05B6:
        parts = segol(0)
    elif cp == 0x05B7:
        parts = patah(0)
    elif cp in (0x05B8, 0x05C7):
        parts = qamats(0)
    elif cp in (0x05B9, 0x05BA):
        parts = [dot(0, r)]
        k = "above"
    elif cp == 0x05BB:
        parts = [dot(r * 1.8, -r - 6), dot(0, -r * 3.0 - 6), dot(-r * 1.8, -r * 5.0 - 6)]
    elif cp == 0x05BC:
        parts = [dot(0, 0, r * 0.95)]
        k = "inside"
    elif cp == 0x05BD:
        parts = [rect(-V * 0.55, -r * 6.2, V * 0.55, -6)]
    elif cp == 0x05BF:
        parts = [rect(-r * 2.0, 0, r * 2.0, hc.H * 0.38)]
        k = "above"
    elif cp in (0x05C1, 0x05C2):
        parts = [dot(0, r)]
        k = "above"
    else:
        raise KeyError(cp)
    s = S(*parts)
    return s, k
