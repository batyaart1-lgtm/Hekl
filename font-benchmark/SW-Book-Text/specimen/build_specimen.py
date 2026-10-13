"""Build the six-page SW Book Text print specimen (PDF 1.7, A4).

    python3 specimen/build_specimen.py [--fonts DIR] [--out FILE]

Only SW Book Text Regular/Bold are used (embedded in full).
"""
import os
import sys
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pdflib import Doc, Font, A4, shape_line, measure
import texts as T

EPOCH = 1767225600
M = 52.0                       # page margin (pt)
W = A4[0] - 2 * M              # text width
R, B = 0, 1                    # font indices


def fa(s, fi):
    return s, [fi] * len(s)


def cat(*parts):
    t, f = "", []
    for s, fi in parts:
        t += s
        f += [fi] * len(s)
    return t, f


def frame(doc, fonts, n, title, sub):
    p = doc.new_page()
    t, f = fa("SW Book Text — Benchmark Prototype", B)
    p.text_line(t, f, fonts, 11, M, A4[1] - 40, False, gray=0.0)
    t, f = fa("Specimen page %d of 6 · %s" % (n, title), R)
    p.text_line(t, f, fonts, 8.5, A4[0] - M, A4[1] - 40, False, align="right", gray=0.35)
    p.rule(M, A4[1] - 47, W, 0.5, 0.3)
    t, f = fa(sub, R)
    p.text_line(t, f, fonts, 8, M, 34, False, gray=0.4)
    p.rule(M, 46, W, 0.4, 0.5)
    return p


def label(p, fonts, text, x, y, size=7.5, align="left", gray=0.4):
    t, f = fa(text, R)
    return p.text_line(t, f, fonts, size, x, y, False, align=align, gray=gray)


def fit(p, fonts, text, fi, size, x, y, width, rtl, align=None, gray=0.0):
    """Draw a single line, shrinking the size until it fits ``width``."""
    t, f = fa(text, fi)
    while measure(t, f, fonts, size, rtl) > width and size > 6:
        size -= 0.5
    if align is None:
        align = "right" if rtl else "left"
    x0 = x + width if align == "right" else x
    p.text_line(t, f, fonts, size, x0, y, rtl, align=align, gray=gray)
    return size


def spaced(s):
    return " ".join(s)


def page1(doc, fonts):
    p = frame(doc, fonts, 1, "Alphabet, finals, digits, punctuation",
              "Row 1: 22 letters · Row 2: 5 final forms · then digits, Hebrew & Latin punctuation, Latin alphabet.")
    y = A4[1] - 74
    for fi, name in ((R, "Regular"), (B, "Bold")):
        label(p, fonts, name.upper(), M, y, 8.5, gray=0.0)
        y -= 40
        fit(p, fonts, spaced(T.ALPHABET), fi, 34, M, y, W, True)
        y -= 40
        fit(p, fonts, spaced(T.FINALS) + "   — אותיות סופיות", fi, 34, M, y, W, True)
        y -= 34
        fit(p, fonts, spaced(T.DIGITS), fi, 26, M, y, W, False)
        y -= 28
        fit(p, fonts, T.HEB_PUNCT, fi, 20, M, y, W, True)
        y -= 26
        fit(p, fonts, spaced(T.LAT_UP), fi, 20, M, y, W, False)
        y -= 25
        fit(p, fonts, spaced(T.LAT_LO), fi, 20, M, y, W, False)
        y -= 25
        fit(p, fonts, T.LAT_PUNCT, fi, 17, M, y, W, False)
        y -= 20
        p.rule(M, y, W, 0.4, 0.6)
        y -= 40
    # coverage note
    label(p, fonts, "Hebrew rows are set right-to-left; Latin and digits left-to-right. All glyphs shaped with HarfBuzz.",
          M, y + 8, 7.5)


def page2(doc, fonts):
    p = frame(doc, fonts, 2, "Hebrew paragraphs, 10\u201313 pt",
              "Same paragraph, Regular, justified, leading = 1.45 × size. Column width 183 mm.")
    y = A4[1] - 70
    for size in (10, 11, 12, 13):
        label(p, fonts, "%d pt / %.1f pt leading" % (size, size * 1.45), M, y, 7.5)
        y -= 6 + size * 1.2
        t, f = fa(T.PARA_BODY, R)
        y, _, _ = p.paragraph(t, f, fonts, size, M, W, y, size * 1.45, True, justify=True)
        y -= 16
    # Bold at 11
    label(p, fonts, "Bold, 11 pt", M, y, 7.5)
    y -= 6 + 11 * 1.2
    t, f = fa(T.PARA_BODY, B)
    p.paragraph(t, f, fonts, 11, M, W, y, 11 * 1.45, True, justify=True)


def flow(p, fonts, items, cols, y_top, y_bot, size, leading):
    """Flow (kind, text, faces, extra) items through columns [(x, w), ...]."""
    ci = 0
    y = y_top
    x, w = cols[0]
    for it in items:
        kind, t, f = it
        if kind == "h2":
            if y - 2.6 * leading < y_bot and ci + 1 < len(cols):
                ci += 1
                x, w = cols[ci]
                y = y_top
            y -= leading * 0.5
            y, _, _ = p.paragraph(t, f, fonts, size + 2.5, x, w, y, leading, True, justify=False)
            y -= leading * 0.15
            continue
        first = True
        while t:
            indent = size * 1.2 if (kind == "p" and first) else 0
            y2, drawn, over = p.paragraph(t, f, fonts, size, x, w, y, leading, True, justify=True,
                                          indent=indent, y_min=y_bot)
            y = y2
            if over is None:
                break
            t, f = t[over:].lstrip(" "), f[over:][len(t[over:]) - len(t[over:].lstrip(" ")):]
            first = False
            ci += 1
            if ci >= len(cols):
                return y
            x, w = cols[ci]
            y = y_top
        y -= leading * 0.25
    return y


def page3(doc, fonts):
    p = frame(doc, fonts, 3, "Two-column justified book layout",
              "10.5 pt on 14.5 pt leading, justified, run-in bold openings, bold headings. Gutter 8 mm.")
    gut = 8 * 72 / 25.4
    cw = (W - gut) / 2
    cols = [(M + cw + gut, cw), (M, cw)]       # RTL: first column on the right
    top = A4[1] - 74
    t, f = fa(T.CHAPTER_TITLE, B)
    p.text_line(t, f, fonts, 22, A4[0] / 2, top - 8, True, align="center")
    p.rule(A4[0] / 2 - 40, top - 22, 80, 0.8, 0.0)
    items = []
    for it in T.CHAPTER + [("h2", "ג. על הקריאה"), ("p", "הדפוס שינה", T.PARA_BODY[len("הדפוס שינה"):])]:
        if it[0] == "h2":
            items.append(("h2",) + fa(it[1], B))
        else:
            t, f = cat((it[1], B), (it[2], R))
            items.append(("p", t, f))
    flow(p, fonts, items, cols, top - 52, 70, 10.5, 14.5)
    p.rule(M + cw + gut / 2 - 0.2, 70, 0.4, top - 52 - 70 + 8, 0.7)


def page4(doc, fonts):
    p = frame(doc, fonts, 4, "Vowel marks, dagesh and punctuation",
              "Marks are positioned by the font's GPOS 'mark' feature (mark-to-base anchors); no manual offsets.")
    y = A4[1] - 82
    label(p, fonts, "Genesis 1:1–5 · Regular 17 pt", M, y + 8)
    y -= 16
    for line in T.NIQQUD_GENESIS:
        fit(p, fonts, line, R, 17, M, y, W, True)
        y -= 29
    y -= 4
    label(p, fonts, "Psalm 23:1–3 · Bold 15 pt", M, y + 8)
    y -= 12
    for line in T.NIQQUD_PSALM:
        fit(p, fonts, line, B, 15, M, y, W, True)
        y -= 26
    y -= 4
    label(p, fonts, "Genesis 1:1–2 · Regular 11 pt and 9 pt (small-size mark clearance)", M, y + 8)
    y -= 10
    for size in (11, 9):
        t, f = fa(" ".join(T.NIQQUD_GENESIS[:2]), R)
        y, _, _ = p.paragraph(t, f, fonts, size, M, W, y, size * 1.9, True, justify=True)
        y -= 4
    y -= 4
    label(p, fonts, "Marks on letters (Regular / Bold)", M, y + 8)
    y -= 4
    cols = 6
    cw = W / cols
    rows = (len(T.MARKS_ROW) + cols - 1) // cols
    for i, (nm, s) in enumerate(T.MARKS_ROW):
        c, r = i % cols, i // cols
        cx = M + cw * (cols - 1 - c) + cw / 2       # RTL grid
        ry = y - 40 - r * 64
        p.rect_stroke(cx - cw / 2 + 2, ry - 31, cw - 4, 62, 0.8, 0.3)
        t, f = fa(s, R)
        p.text_line(t, f, fonts, 27, cx - 16, ry, True, align="center")
        t, f = fa(s, B)
        p.text_line(t, f, fonts, 27, cx + 16, ry, True, align="center")
        label(p, fonts, nm, cx, ry - 26, 6, align="center")
    y -= 28 + rows * 64
    label(p, fonts, "Hebrew punctuation: geresh, gershayim, maqaf, sof pasuq, paseq, quotation marks, shekel", M, y + 8)
    y -= 14
    fit(p, fonts, T.PUNCT_LINE, R, 14, M, y, W, True)
    y -= 22
    fit(p, fonts, T.PUNCT_LINE, B, 14, M, y, W, True)


def page5(doc, fonts):
    p = frame(doc, fonts, 5, "Mixed Hebrew / English, numbers, citations",
              "Bidirectional runs: UAX#9 subset (see pdflib.bidi_levels). 11 pt on 16 pt, justified.")
    y = A4[1] - 76
    label(p, fonts, "Hebrew paragraphs with embedded Latin, numbers and citations (RTL base)", M, y + 6)
    y -= 14
    for kind, s in T.MIXED:
        t, f = fa(s, R)
        y, _, _ = p.paragraph(t, f, fonts, 11, M, W, y, 16.5, True, justify=True, indent=14)
        y -= 7
    y -= 6
    label(p, fonts, "English paragraph with embedded Hebrew (LTR base)", M, y + 6)
    y -= 14
    ltr = ("In Hebrew typesetting the word ספר (sefer) means “book”, while "
           "ספרייה (sifriya) means “library”. Numbers such as 1,250 and 3.14 keep their "
           "left-to-right order inside right-to-left text: דף 12, עמ׳ 305–310, "
           "שנת 2025. A citation (Cohen, 2021, p. 17) may appear in either language, "
           "e.g. בריאון (כהן, תשפ״א, עמ׳ 17).")
    t, f = fa(ltr, R)
    y, _, _ = p.paragraph(t, f, fonts, 11, M, W, y, 16.5, False, justify=True, indent=14)
    y -= 12
    label(p, fonts, "Latin lines (Regular / Bold), 13 pt", M, y + 6)
    y -= 18
    for s in T.LATIN_PANGRAMS:
        fit(p, fonts, s, R, 13, M, y, W, False)
        y -= 18
        fit(p, fonts, s, B, 13, M, y, W, False)
        y -= 22
    label(p, fonts, "Digits in running text, Regular and Bold, 12 pt", M, y + 6)
    y -= 16
    for fi in (R, B):
        fit(p, fonts, "בשנה 2025 הודפסו 12,500 עותקים (46.4%) במחיר ₪ 49.90 — ISBN 978-965-7402-12-3",
            fi, 12, M, y, W, True)
        y -= 20


def page6(doc, fonts):
    p = frame(doc, fonts, 6, "Regular and Bold side by side",
              "Left column: Regular. Right column: Bold. Identical text and size in each row.")
    gut = 14.0
    cw = (W - gut) / 2
    xl, xr = M, M + cw + gut
    y = A4[1] - 76
    for x, nm, fi in ((xl, "REGULAR", R), (xr, "BOLD", B)):
        label(p, fonts, nm, x, y, 8.5, gray=0.0)
    p.rule(xl + cw + gut / 2 - 0.2, 60, 0.4, y - 52, 0.7)
    y -= 38

    def row(text, size, rtl, desc, par=False, lead=None):
        nonlocal y
        label(p, fonts, desc, M, y + size * 0.9 + 4, 6.5)
        ys = []
        for x, fi in ((xl, R), (xr, B)):
            t, f = fa(text, fi)
            if par:
                yy, _, _ = p.paragraph(t, f, fonts, size, x, cw, y, lead, rtl, justify=True)
            else:
                fit(p, fonts, t, fi, size, x, y, cw, rtl)
                yy = y - (lead or size * 1.25)
            ys.append(yy)
        y = min(ys) - 14

    row(spaced(T.ALPHABET[:11]), 26, True, "36 pt alphabet (1/2)", lead=34)
    row(spaced(T.ALPHABET[11:]), 26, True, "alphabet (2/2)", lead=34)
    row(spaced(T.FINALS) + " 0123456789", 26, True, "final forms + digits", lead=34)
    row("בבבדדד ההה ררר חחח תתת םםם ססס ששש", 22, True, "letter-spacing rhythm", lead=30)
    row("הדפוס שינה את דרכו של האדם אל הידע. ספר שנדפס היטב נקרא בנחת: האותיות ברורות, הרווחים שקולים, והשורות נושאות את העין מן הפסקה הראשונה ועד האחרונה.",
        11, True, "11 pt paragraph, justified", par=True, lead=16)
    row(T.NIQQUD_GENESIS[0], 15, True, "niqqud, 15 pt", lead=26)
    row(T.NIQQUD_PSALM[0], 15, True, "niqqud, 15 pt", lead=26)
    row("Hamburgefonstiv Sphinx of black quartz, 0123456789", 17, False, "Latin 17 pt", lead=24)
    row("ספר (book) — 2025, 12,500 ₪ 49.90", 17, True, "mixed 17 pt", lead=24)


def build(fontdir, out):
    fonts = [Font(os.path.join(fontdir, "SWBookText-Regular.ttf"), "F1"),
             Font(os.path.join(fontdir, "SWBookText-Bold.ttf"), "F2")]
    doc = Doc("SW Book Text - Benchmark Prototype - Specimen", fonts)
    for fn in (page1, page2, page3, page4, page5, page6):
        fn(doc, fonts)
    doc.save(out, EPOCH)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    root = os.path.dirname(HERE)
    ap.add_argument("--fonts", default=os.path.join(root, "fonts"))
    ap.add_argument("--out", default=os.path.join(HERE, "SWBookText-Specimen.pdf"))
    a = ap.parse_args()
    print(build(a.fonts, a.out))
