import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auditlib import *
def sheet(fontdir, out, pt=44, dpi=100):
    F = faces(fontdir)
    lines = ["ABCDEFGHIJKLM", "NOPQRSTUVWXYZ", "abcdefghijklm", "nopqrstuvwxyz", "0123456789 &@%$#§",
             "Hamburgefonstiv, quick brown fox.", "(Cohen, 2021, p. 17) “quoted” 3.14 — a–b"]
    ims = []
    for w in ("Regular", "Bold"):
        for t in lines:
            ims.append(render_text(F[w], t, False, pt, dpi, width_px=1100))
    W = 1100
    H = sum(i.height for i in ims)
    o = Image.new("L", (W * 2, H // 2 + 20), 255)
    y = 0
    for k, im in enumerate(ims):
        col = k // len(lines)
        if k % len(lines) == 0: y = 0
        o.paste(im, (col * W, y)); y += im.height
    o.save(out)
if __name__ == "__main__":
    sheet(sys.argv[1], sys.argv[2])
