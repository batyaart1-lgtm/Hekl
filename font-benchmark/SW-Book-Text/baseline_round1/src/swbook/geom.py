"""Geometry kit for SW Book Text.

Every outline in the family is produced by this module from first principles:
straight-edged polygons and *elliptical-pen strokes* along hand-written
centre-lines.  No third-party outline data is read anywhere.

Elliptical pen
--------------
A pen with horizontal extent ``a`` and vertical extent ``b`` is simulated by
scaling x by b/a, stroking with a round-symmetric Skia stroke of width b and
scaling back.  Hebrew uses a pen that is wide vertically (thick horizontals,
thin verticals); Latin uses the opposite pen.
"""
import math
import pathops
from pathops import Path, PathOp, LineCap, LineJoin

BUTT, ROUND, SQUARE = LineCap.BUTT_CAP, LineCap.ROUND_CAP, LineCap.SQUARE_CAP
MITER, RJOIN, BEVEL = LineJoin.MITER_JOIN, LineJoin.ROUND_JOIN, LineJoin.BEVEL_JOIN

KAPPA = 0.5522847498


class Shape:
    """A union-accumulating outline."""

    def __init__(self):
        self.path = Path()

    def add(self, p):
        if isinstance(p, Shape):
            p = p.path
        p = _simplified(p)
        if len(list(self.path.segments)) == 0:
            self.path = p
        else:
            self.path = pathops.op(self.path, p, PathOp.UNION, fix_winding=True)
        return self

    def sub(self, p):
        self.path = pathops.op(self.path, _simplified(p), PathOp.DIFFERENCE,
                               fix_winding=True)
        return self

    def clip(self, x0, y0, x1, y1):
        self.path = pathops.op(self.path, rect(x0, y0, x1, y1),
                               PathOp.INTERSECTION, fix_winding=True)
        return self

    def bounds(self):
        return self.path.bounds


def _simplified(p):
    q = Path(p)
    q.simplify(fix_winding=True)
    return q


def rect(x0, y0, x1, y1):
    return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def poly(pts):
    p = Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    return p


def circle(cx, cy, r):
    return ellipse(cx, cy, r, r)


def ellipse(cx, cy, rx, ry):
    k = KAPPA
    p = Path()
    p.moveTo(cx + rx, cy)
    p.cubicTo(cx + rx, cy + k * ry, cx + k * rx, cy + ry, cx, cy + ry)
    p.cubicTo(cx - k * rx, cy + ry, cx - rx, cy + k * ry, cx - rx, cy)
    p.cubicTo(cx - rx, cy - k * ry, cx - k * rx, cy - ry, cx, cy - ry)
    p.cubicTo(cx + k * rx, cy - ry, cx + rx, cy - k * ry, cx + rx, cy)
    p.close()
    return p


class Pth:
    """Tiny centre-line builder.  Methods return self for chaining."""

    def __init__(self, x, y):
        self.p = Path()
        self.p.moveTo(x, y)
        self.x, self.y = x, y

    def L(self, x, y):
        self.p.lineTo(x, y)
        self.x, self.y = x, y
        return self

    def C(self, x1, y1, x2, y2, x, y):
        self.p.cubicTo(x1, y1, x2, y2, x, y)
        self.x, self.y = x, y
        return self

    def Q(self, x1, y1, x, y):
        self.p.quadTo(x1, y1, x, y)
        self.x, self.y = x, y
        return self

    def arc(self, cx, cy, rx, ry, a0, a1):
        """Elliptical arc from angle a0 to a1 (degrees, ccw positive, y up).
        Starts by line-joining to the arc start if not already there."""
        n = max(1, int(math.ceil(abs(a1 - a0) / 90.0)))
        step = (a1 - a0) / n
        for i in range(n):
            t0 = math.radians(a0 + i * step)
            t1 = math.radians(a0 + (i + 1) * step)
            k = 4.0 / 3.0 * math.tan((t1 - t0) / 4.0)
            x0, y0 = cx + rx * math.cos(t0), cy + ry * math.sin(t0)
            x3, y3 = cx + rx * math.cos(t1), cy + ry * math.sin(t1)
            x1, y1 = x0 - k * rx * math.sin(t0), y0 + k * ry * math.cos(t0)
            x2, y2 = x3 + k * rx * math.sin(t1), y3 - k * ry * math.cos(t1)
            if i == 0 and (abs(self.x - x0) > 0.01 or abs(self.y - y0) > 0.01):
                self.L(x0, y0)
            self.C(x1, y1, x2, y2, x3, y3)
        return self

    def close(self):
        self.p.close()
        return self


def stroke(path, a, b, cap=BUTT, join=RJOIN, miter=3.0):
    """Stroke ``path`` (Path or Pth) with an elliptical pen: horizontal extent
    ``a``, vertical extent ``b``."""
    if isinstance(path, Pth):
        path = path.p
    s = b / a
    q = path.transform(s, 0, 0, 1, 0, 0)
    q.stroke(b, cap, join, miter)
    r = q.transform(1.0 / s, 0, 0, 1, 0, 0)
    r.convertConicsToQuads(0.25)
    return r


def line(x0, y0, x1, y1):
    return Pth(x0, y0).L(x1, y1)


def xform(path, sx=1, sy=1, dx=0, dy=0, skew=0.0):
    """Affine transform; ``skew`` is the horizontal shear (x += skew*y)."""
    return path.transform(sx, 0, skew, sy, dx, dy)
