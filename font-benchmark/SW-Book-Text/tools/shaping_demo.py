"""Print HarfBuzz shaping output (glyph names, advances, mark offsets) for sample clusters."""
import os, sys
import uharfbuzz as hb
from fontTools.ttLib import TTFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for w in ("Regular", "Bold"):
    p = os.path.join(ROOT, "fonts", "SWBookText-%s.ttf" % w)
    tt = TTFont(p)
    font = hb.Font(hb.Face(hb.Blob.from_file_path(p)))
    for text, rtl in (("בָּ", True), ("שֹׁ", True), ("ךָ", True), ("שָׁלוֹם", True), ("AV To", False)):
        buf = hb.Buffer(); buf.add_str(text)
        buf.direction = "rtl" if rtl else "ltr"; buf.script = "Hebr" if rtl else "Latn"
        hb.shape(font, buf, {})
        row = ["%s(adv=%d,dx=%d,dy=%d)" % (tt.getGlyphName(i.codepoint), q.x_advance, q.x_offset, q.y_offset)
               for i, q in zip(buf.glyph_infos, buf.glyph_positions)]
        print(w, repr(text), " ".join(row))
