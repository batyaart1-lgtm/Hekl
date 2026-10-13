"""HarfBuzz shaping + PIL rasterisation helper (development/tests)."""
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageChops
from .preview import FlatPen


class Face:
    def __init__(self, path):
        self.path = path
        self.tt = TTFont(path)
        self.gs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        blob = hb.Blob.from_file_path(path)
        self.hbface = hb.Face(blob)
        self.hbfont = hb.Font(self.hbface)
        self.upm = self.tt["head"].unitsPerEm

    def shape(self, text, rtl=False, features=None):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.direction = "rtl" if rtl else "ltr"
        buf.script = "Hebr" if rtl else "Latn"
        buf.language = "he" if rtl else "en"
        hb.shape(self.hbfont, buf, features or {})
        out = []
        for i, p in zip(buf.glyph_infos, buf.glyph_positions):
            out.append((i.codepoint, i.cluster, p.x_advance, p.y_advance, p.x_offset, p.y_offset))
        return out


def draw_run(im, face, shaped, x, y, size, color=0, rtl_origin=None):
    """Draw shaped glyphs starting at pen position x (left edge); returns end x."""
    sc = size / face.upm
    d = ImageDraw.Draw(im)
    pen_x = x
    for gid, cl, xa, ya, xo, yo in shaped:
        name = face.order[gid]
        fp = FlatPen()
        face.gs[name].draw(fp)
        m = Image.new("1", im.size, 0)
        for c in fp.contours:
            mm = Image.new("1", im.size, 0)
            ImageDraw.Draw(mm).polygon([(pen_x + (xo + px) * sc, y - (yo + py) * sc) for px, py in c], fill=1)
            m = ImageChops.logical_xor(m, mm)
        im.paste(color, mask=m)
        pen_x += xa * sc
    return pen_x


def render_lines(face, lines, size=96, width=1800, line_h=None):
    """lines: list of (text, rtl).  RTL lines right-aligned."""
    line_h = line_h or int(size * 1.6)
    im = Image.new("L", (width, line_h * len(lines) + 20), 255)
    for i, (t, rtl) in enumerate(lines):
        sh = face.shape(t, rtl)
        tw = sum(s[2] for s in sh) * size / face.upm
        x = width - 40 - tw if rtl else 40
        draw_run(im, face, sh, x, line_h * (i + 1) - int(size * 0.3), size)
    return im
