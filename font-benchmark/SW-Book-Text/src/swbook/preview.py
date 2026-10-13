"""Developer preview: rasterise construction outlines to a PNG contact sheet."""
import sys
from PIL import Image, ImageDraw
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.basePen import BasePen


class FlatPen(BasePen):
    def __init__(self):
        super().__init__(None)
        self.contours, self.cur = [], []

    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _curveToOne(self, a, b, c):
        p0 = self.cur[-1]
        for i in range(1, 13):
            t = i / 12; m = 1 - t
            self.cur.append((m**3*p0[0]+3*m*m*t*a[0]+3*m*t*t*b[0]+t**3*c[0],
                             m**3*p0[1]+3*m*m*t*a[1]+3*m*t*t*b[1]+t**3*c[1]))
    def _qCurveToOne(self, a, c):
        p0 = self.cur[-1]
        for i in range(1, 9):
            t = i / 8; m = 1 - t
            self.cur.append((m*m*p0[0]+2*m*t*a[0]+t*t*c[0], m*m*p0[1]+2*m*t*a[1]+t*t*c[1]))
    def _closePath(self):
        self.contours.append(self.cur); self.cur = []
    _endPath = _closePath


def sheet(items, out, cols=9, cell=330, scale=0.27):
    rows = (len(items) + cols - 1) // cols
    im = Image.new("L", (cols * cell, rows * cell), 255)
    d = ImageDraw.Draw(im)
    for i, (label, path) in enumerate(items):
        ox = (i % cols) * cell + 30
        oy = (i // cols) * cell + int(cell * 0.62)
        d.line([(ox - 20, oy), (ox + cell - 40, oy)], fill=200)
        pen = FlatPen(); path.draw(pen)
        # even-odd composite via mask xor
        m = Image.new("1", im.size, 0)
        for c in pen.contours:
            mm = Image.new("1", im.size, 0)
            ImageDraw.Draw(mm).polygon([(ox + x * scale, oy - y * scale) for x, y in c], fill=1)
            m = Image.composite(Image.new("1", im.size, 1), m, mm) if False else Image.eval(Image.merge("L", [m.convert("L")]).convert("L"), lambda v: v) if False else m
            from PIL import ImageChops
            m = ImageChops.logical_xor(m, mm)
        im.paste(0, mask=m)
        d.text((ox, oy + 75), label, fill=120)
    im.save(out)
