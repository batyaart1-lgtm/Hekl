"""Render a complete audit snapshot of a font directory.

    python3 tools/snapshot.py --fonts DIR --tag TAG
Writes round2/images/TAG/ : glyph sheets, context strips, size strips, metrics, confusion, pair stats, PDF pages.
"""
import os, sys, json, argparse, subprocess, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auditlib import *
from auditlib import _draw_glyph
sys.path.insert(0, os.path.join(ROOT, "src"))
import audit_text as AT
from PIL import Image, ImageDraw


def glyph_sheet(face, out, cols=7, ppem_px=230):
    cell_w, cell_h = 300, 340
    rows = (27 + cols - 1) // cols
    sheet = Image.new("L", (cols * cell_w, rows * cell_h), 255)
    d = ImageDraw.Draw(sheet)
    sc = ppem_px / 1000.0
    for i, (ch, nm) in enumerate(zip(HEB, HEB_NAMES)):
        cx, cy = (i % cols) * cell_w, (i // cols) * cell_h
        base = cy + 40 + int(880 * sc)       # baseline y inside cell
        g = face.cmap[ord(ch)]
        adv = face.tt["hmtx"][g][0]
        ox = cx + (cell_w - adv * sc) / 2
        # guides: baseline, letter top, advance box
        for y, v in ((0, 170), (715, 215), (-250, 230), (880, 235)):
            d.line([(cx + 5, base - y * sc), (cx + cell_w - 5, base - y * sc)], fill=v)
        d.rectangle([ox, base - 880 * sc, ox + adv * sc, base + 250 * sc], outline=225)
        big = Image.new("L", (cell_w * SS, cell_h * SS), 255)
        _draw_glyph(big, face, g, (ox - cx) * SS, (base - cy) * SS, sc * SS)
        small = big.resize((cell_w, cell_h), Image.BOX)
        sheet.paste(small, (cx, cy), Image.eval(small, lambda v: 255 - v))
        d.text((cx + 6, cy + cell_h - 16), "%s %s adv=%d" % (nm, ch, adv), fill=80, font=ImageFont.load_default())
    sheet.save(out)


def stack(images, pad=8, bg=255):
    W = max(i.width for i in images)
    H = sum(i.height for i in images) + pad * (len(images) - 1)
    out = Image.new("L", (W, H), bg)
    y = 0
    for im in images:
        out.paste(im, (0, y)); y += im.height + pad
    return out


def context_strips(face, outdir, w):
    # per-letter words at display size (48 pt @ 150 dpi) in rows of 3 letters
    rows = []
    for ch in HEB:
        txt = "   ".join(AT.WORDS[ch])
        rows.append(label(render_text(face, txt, True, 30, 150, width_px=1100), "%s" % ch, (4, 2)))
    for k in range(0, 27, 9):
        stack(rows[k:k + 9]).save(os.path.join(outdir, "words_%s_%d.png" % (w, k // 9 + 1)))
    # confusables and hard pairs
    conf = [render_text(face, "  ".join(AT.CONFUSABLES[:9]), True, 36, 150, width_px=1100),
            render_text(face, "  ".join(AT.CONFUSABLES[9:]), True, 36, 150, width_px=1100),
            render_text(face, "  ".join(AT.PAIRS[:10]), True, 36, 150, width_px=1100),
            render_text(face, "  ".join(AT.PAIRS[10:20]), True, 36, 150, width_px=1100),
            render_text(face, "  ".join(AT.PAIRS[20:]), True, 36, 150, width_px=1100)]
    stack(conf).save(os.path.join(outdir, "confusables_pairs_%s.png" % w))
    # actual-size running text 10-13 pt @ 300 dpi
    for pt in (10, 11, 12, 13):
        ims = [render_text(face, t, True, pt, 300, width_px=int(pt * 300 / 72 * 52)) for t in AT.RUNNING]
        stack(ims, pad=int(pt * 300 / 72 * 0.45)).save(os.path.join(outdir, "running_%s_%dpt.png" % (w, pt)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--pdf", action="store_true", help="also build+render the frozen specimen PDF")
    a = ap.parse_args()
    out = os.path.join(ROOT, "round2", "images", a.tag)
    os.makedirs(out, exist_ok=True)
    F = faces(a.fonts)
    summary = {"tag": a.tag, "fonts": a.fonts}
    for w, face in F.items():
        glyph_sheet(face, os.path.join(out, "glyphs_%s.png" % w))
        context_strips(face, out, w)
        summary["metrics_" + w] = metrics(face)
        summary["confusion_" + w] = confusion(face)
        mins, means = pair_stats(face)
        m = list(means.values())
        summary["pairs_" + w] = {
            "mean_clearance_mean": round(statistics.mean(m), 1), "mean_clearance_stdev": round(statistics.pstdev(m), 1),
            "pairs_min_clearance_below_20": sorted([(k, round(v)) for k, v in mins.items() if v < 20], key=lambda t: t[1])[:40],
            "n_pairs_below_20": sum(1 for v in mins.values() if v < 20),
        }
    json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1, ensure_ascii=False)
    if a.pdf:
        pdf = os.path.join(out, "specimen.pdf")
        subprocess.run([sys.executable, os.path.join(ROOT, "specimen", "build_specimen.py"), "--fonts", a.fonts, "--out", pdf], check=True)
        subprocess.run(["pdftoppm", "-r", "100", "-png", pdf, os.path.join(out, "page")], check=True)
    print("snapshot ->", out)


if __name__ == "__main__":
    main()
