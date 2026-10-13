"""Before/after comparison image for chosen Hebrew glyphs (rendered from compiled TTFs).

    python3 tools/cmp.py --old DIR --new DIR --glyphs vav,zayin --out file.png [--words "ויום זמן"]
Rows: glyph name; columns: Regular old | Regular new | Bold old | Bold new (enlarged, same guides),
optional rows: the given words at 11 pt/300 dpi (old|new) and at 40 pt.
"""
import os, sys, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auditlib import *
from auditlib import _draw_glyph
from PIL import Image, ImageDraw


def cell(face, ch, w=250, h=300, sc=0.20):
    g = face.cmap[ord(ch)]
    adv = face.tt["hmtx"][g][0]
    d_im = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(d_im)
    base = 70 + int(800 * sc)
    ox = (w - adv * sc) / 2
    for y, v in ((0, 150), (650, 205), (-230, 225), (800, 225)):
        d.line([(3, base - y * sc), (w - 3, base - y * sc)], fill=v)
    d.rectangle([ox, base - 800 * sc, ox + adv * sc, base + 230 * sc], outline=215)
    big = Image.new("L", (w * SS, h * SS), 255)
    _draw_glyph(big, face, g, ox * SS, base * SS, sc * SS)
    sm = big.resize((w, h), Image.BOX)
    d_im.paste(sm, (0, 0), Image.eval(sm, lambda v: 255 - v))
    return d_im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True); ap.add_argument("--new", required=True)
    ap.add_argument("--glyphs", default=""); ap.add_argument("--out", required=True)
    ap.add_argument("--words", default="")
    ap.add_argument("--latin", default="")
    a = ap.parse_args()
    O, N = faces(a.old), faces(a.new)
    names = dict(zip(HEB_NAMES, HEB))
    chars = [names.get(g, g) for g in a.glyphs.split(",") if g]
    cw, chh = 250, 300
    rows = []
    for ch in chars:
        row = Image.new("L", (cw * 4 + 30, chh), 255)
        for k, (F, w) in enumerate(((O, "Regular"), (N, "Regular"), (O, "Bold"), (N, "Bold"))):
            c = cell(F[w], ch)
            row.paste(c, (k * (cw + 10), 0))
        d = ImageDraw.Draw(row)
        for k, t in enumerate(("Regular OLD", "Regular NEW", "Bold OLD", "Bold NEW")):
            d.text((k * (cw + 10) + 4, chh - 14), "%s  %s" % (ch, t), fill=60, font=ImageFont.load_default())
        rows.append(row)
    W = cw * 4 + 30
    if a.words:
        for w in ("Regular", "Bold"):
            for pt, dpi in ((40, 100), (11, 300)):
                pair = []
                for F in (O, N):
                    pair.append(render_text(F[w], a.words, True, pt, dpi, width_px=W // 2 - 5))
                im = Image.new("L", (W, max(p.height for p in pair)), 255)
                im.paste(pair[0], (0, 0)); im.paste(pair[1], (W // 2 + 5, 0))
                ImageDraw.Draw(im).line([(W // 2, 0), (W // 2, im.height)], fill=180)
                rows.append(im)
    if a.latin:
        for w in ("Regular", "Bold"):
            pair = [render_text(F[w], a.latin, False, 30, 100, width_px=W // 2 - 5) for F in (O, N)]
            im = Image.new("L", (W, max(p.height for p in pair)), 255)
            im.paste(pair[0], (0, 0)); im.paste(pair[1], (W // 2 + 5, 0))
            rows.append(im)
    H = sum(r.height for r in rows) + 6 * len(rows)
    out = Image.new("L", (W, H), 255)
    y = 0
    for r in rows:
        out.paste(r, (0, y)); y += r.height + 6
    out.save(a.out)
    print(a.out, out.size)


if __name__ == "__main__":
    main()
