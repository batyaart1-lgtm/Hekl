"""Minimal PDF writer + HarfBuzz layout engine for the SW Book Text specimen.

* Fonts are embedded in full as CIDFontType2 / Identity-H with a ToUnicode CMap.
* Text is shaped with HarfBuzz (uharfbuzz): kerning and the GPOS `mark`
  feature are applied, so niqqud/dagesh positions come from the font itself.
* A small, documented subset of the Unicode Bidirectional Algorithm is
  implemented (see `bidi_levels`) - sufficient for Hebrew paragraphs that
  contain Latin words, digits and common punctuation.
* Every glyph is placed with an absolute text matrix, so mark offsets are
  exact.  No font other than SW Book Text is referenced in the output.
"""
import os
import time
import zlib
import unicodedata
import uharfbuzz as hb
from fontTools.ttLib import TTFont

PT_PER_MM = 72 / 25.4
A4 = (595.276, 841.890)


# ----------------------------------------------------------------- fonts
class Font:
    def __init__(self, path, res_name):
        self.path = path
        self.res = res_name
        self.data = open(path, "rb").read()
        self.tt = TTFont(path)
        self.upm = self.tt["head"].unitsPerEm
        self.order = self.tt.getGlyphOrder()
        self.hmtx = self.tt["hmtx"]
        self.psname = self.tt["name"].getDebugName(6)
        blob = hb.Blob(self.data)
        self.hbfont = hb.Font(hb.Face(blob))
        cmap = self.tt.getBestCmap()
        self.gid2uni = {}
        for cp, gn in sorted(cmap.items()):
            gid = self.order.index(gn)
            self.gid2uni.setdefault(gid, cp)
        self.used = set()
        self._cache = {}

    def shape(self, text, rtl):
        key = (text, rtl)
        if key in self._cache:
            return self._cache[key]
        buf = hb.Buffer()
        buf.add_str(text)
        buf.direction = "rtl" if rtl else "ltr"
        buf.script = "Hebr" if rtl else "Latn"
        buf.language = "he" if rtl else "en"
        hb.shape(self.hbfont, buf, {})
        out = []
        for i, p in zip(buf.glyph_infos, buf.glyph_positions):
            out.append((i.codepoint, i.cluster, p.x_advance, p.x_offset, p.y_offset))
        self._cache[key] = out
        return out


# ------------------------------------------------------------------ bidi
def bidi_levels(text, base_rtl):
    """Return per-character direction ('R' or 'L') following UAX#9 N1/N2,
    W2-W7 (simplified).  Digits and Latin letters are 'L' (embedding level 2
    in an RTL paragraph), Hebrew letters/marks 'R'."""
    base = "R" if base_rtl else "L"
    t = [unicodedata.bidirectional(c) for c in text]
    n = len(t)
    for i in range(n):
        if t[i] == "NSM":
            t[i] = t[i - 1] if i else base
        if t[i] in ("AL",):
            t[i] = "R"
    # W4/W5: separators between numbers, terminators next to numbers
    for i in range(1, n - 1):
        if t[i] in ("ES", "CS") and t[i - 1] == "EN" and t[i + 1] == "EN":
            t[i] = "EN"
    for i in range(n):
        if t[i] == "ET":
            j = i
            while j < n and t[j] == "ET":
                j += 1
            if (j < n and t[j] == "EN") or (i > 0 and t[i - 1] == "EN"):
                for k in range(i, j):
                    t[k] = "EN"
    # W7: EN after L stays L
    last_strong = base
    for i in range(n):
        if t[i] in ("L", "R"):
            last_strong = t[i]
        elif t[i] == "EN" and last_strong == "L":
            t[i] = "L"
    # N0 (simplified): paired brackets take the direction of their content
    def sdir(k):
        return "L" if k == "L" else ("R" if k in ("R", "EN", "AN") else None)
    pairs, stack = [], []
    for i, ch in enumerate(text):
        if ch in "([{":
            stack.append((i, {"(": ")", "[": "]", "{": "}"}[ch]))
        elif ch in ")]}" and stack:
            for si in range(len(stack) - 1, -1, -1):
                if stack[si][1] == ch:
                    pairs.append((stack[si][0], i))
                    del stack[si:]
                    break
    for (i, j) in sorted(pairs):
        inside = {sdir(t[k]) for k in range(i + 1, j)} - {None}
        if not inside:
            continue
        e = base
        opp = "L" if e == "R" else "R"
        if e in inside:
            d = e
        else:
            before = None
            for k in range(i - 1, -1, -1):
                if sdir(t[k]):
                    before = sdir(t[k])
                    break
            d = opp if before == opp or (before is None and base == opp) else e
        t[i] = t[j] = "L" if d == "L" else "R"
    # N1/N2
    res = [None] * n
    for i in range(n):
        if t[i] in ("L",):
            res[i] = "L"
        elif t[i] in ("R", "EN", "AN"):
            res[i] = "R" if t[i] == "R" else ("EN")
    i = 0
    out = []
    # neutrals
    kinds = []
    for i in range(n):
        kinds.append(t[i])

    def cls(k):
        return "L" if k == "L" else ("R" if k in ("R", "EN", "AN") else None)
    dirs = [None] * n
    for i in range(n):
        k = kinds[i]
        if cls(k):
            dirs[i] = "L" if k in ("L", "EN") else "R"
    i = 0
    while i < n:
        if dirs[i] is None:
            j = i
            while j < n and dirs[j] is None:
                j += 1
            left = cls(kinds[i - 1]) if i > 0 else base
            right = cls(kinds[j]) if j < n else base
            d = left if left == right else base
            for k in range(i, j):
                dirs[k] = d
            i = j
        else:
            i += 1
    return dirs


def visual_runs(text, faces, base_rtl):
    """Split a logical line into runs (start, end, rtl, face) in visual order
    (left-to-right on the page)."""
    dirs = bidi_levels(text, base_rtl)
    runs = []
    s = 0
    for i in range(1, len(text) + 1):
        if i == len(text) or dirs[i] != dirs[s] or faces[i] != faces[s]:
            runs.append((s, i, dirs[s] == "R", faces[s], dirs[s]))
            s = i
    # reorder: group by direction sequences (level resolution for 2 levels)
    if base_rtl:
        # level 1 = R runs, level 2 = L runs; reverse whole sequence, keep
        # consecutive L runs internally in logical order
        out, i = [], 0
        seq = []
        while i < len(runs):
            j = i
            while j < len(runs) and runs[j][4] == runs[i][4]:
                j += 1
            seq.append(runs[i:j])
            i = j
        for grp in reversed(seq):
            if grp[0][4] == "R":
                out += list(reversed(grp))
            else:
                out += grp
        return out
    else:
        out, i = [], 0
        seq = []
        while i < len(runs):
            j = i
            while j < len(runs) and runs[j][4] == runs[i][4]:
                j += 1
            seq.append(runs[i:j])
            i = j
        for grp in seq:
            out += list(reversed(grp)) if grp[0][4] == "R" else grp
        return out


# ------------------------------------------------------------- layout
def shape_line(text, faces, fonts, size, base_rtl, extra_space=0.0):
    """Shape a logical line.  Returns (placements, width_pt); placements are
    (font, gid, x_pt, y_pt_offset) with x relative to the line's left edge."""
    placed = []
    x = 0.0
    for (s, e, rtl, fi, _) in visual_runs(text, faces, base_rtl):
        f = fonts[fi]
        sc = size / f.upm
        for gid, cl, xa, xo, yo in f.shape(text[s:e], rtl):
            ch = text[s + cl]
            adv = xa * sc
            if ch == " ":
                adv += extra_space
            placed.append((f, gid, x + xo * sc, yo * sc))
            f.used.add(gid)
            x += adv
    return placed, x


def measure(text, faces, fonts, size, base_rtl):
    return shape_line(text, faces, fonts, size, base_rtl)[1]


def break_lines(text, faces, fonts, size, width, base_rtl, indent=0.0):
    """Greedy line breaking on spaces.  Returns list of (start, end) slices."""
    words = []
    i = 0
    n = len(text)
    while i < n:
        j = text.find(" ", i)
        if j == -1:
            j = n
        words.append((i, j))
        i = j + 1
    lines, cur = [], None
    space_w = measure(" ", [faces[0]], fonts, size, base_rtl)
    cur_w = 0.0
    avail = width - indent
    for (a, b) in words:
        w = measure(text[a:b], faces[a:b], fonts, size, base_rtl)
        if cur is None:
            cur, cur_w = [a, b], w
        elif cur_w + space_w + w <= avail:
            cur[1] = b
            cur_w += space_w + w
        else:
            lines.append(tuple(cur))
            cur, cur_w = [a, b], w
            avail = width
    if cur:
        lines.append(tuple(cur))
    return lines


# -------------------------------------------------------------- PDF
class Page:
    def __init__(self, doc):
        self.doc = doc
        self.ops = []
        self.fonts_used = set()

    def rule(self, x, y, w, h, gray=0.0):
        self.ops.append("q %.3f g %.2f %.2f %.2f %.2f re f Q" % (gray, x, y, w, h))

    def rect_stroke(self, x, y, w, h, gray=0.6, lw=0.4):
        self.ops.append("q %.3f G %.2f w %.2f %.2f %.2f %.2f re S Q" % (gray, lw, x, y, w, h))

    def glyphs(self, placed, x0, y, size, gray=0.0):
        self.ops.append("q %.3f g BT" % gray)
        cur = None
        for f, gid, dx, dy in placed:
            if f is not cur:
                self.ops.append("/%s %.3f Tf" % (f.res, size))
                cur = f
            self.fonts_used.add(f)
            self.ops.append("1 0 0 1 %.3f %.3f Tm <%04X> Tj" % (x0 + dx, y + dy, gid))
        self.ops.append("ET Q")

    def text_line(self, text, faces, fonts, size, x, y, base_rtl, align="left",
                  extra_space=0.0, gray=0.0, width=None):
        placed, w = shape_line(text, faces, fonts, size, base_rtl, extra_space)
        if align == "right":
            x0 = x - w
        elif align == "center":
            x0 = x - w / 2
        else:
            x0 = x
        self.glyphs(placed, x0, y, size, gray)
        return w

    def paragraph(self, text, faces, fonts, size, x_left, width, y_top, leading,
                  base_rtl, justify=True, indent=0.0, gray=0.0, y_min=None, max_lines=None):
        """Lay out a paragraph; returns (y_after, lines_drawn, overflow_start)."""
        lines = break_lines(text, faces, fonts, size, width, base_rtl, indent)
        y = y_top
        drawn = 0
        for li, (a, b) in enumerate(lines):
            if y_min is not None and y < y_min:
                return y, drawn, a
            if max_lines is not None and drawn >= max_lines:
                return y, drawn, a
            seg, sf = text[a:b], faces[a:b]
            last = li == len(lines) - 1
            ind = indent if li == 0 else 0.0
            avail = width - ind
            w0 = measure(seg, sf, fonts, size, base_rtl)
            nsp = seg.count(" ")
            extra = 0.0
            if justify and not last and nsp:
                extra = (avail - w0) / nsp
            placed, w = shape_line(seg, sf, fonts, size, base_rtl, extra)
            if base_rtl:
                x0 = x_left + width - ind - w
            else:
                x0 = x_left + ind
            self.glyphs(placed, x0, y, size, gray)
            y -= leading
            drawn += 1
        return y, drawn, None


class Doc:
    def __init__(self, title, fonts):
        self.title = title
        self.fonts = fonts
        self.pages = []

    def new_page(self):
        p = Page(self)
        self.pages.append(p)
        return p

    # ---------------------------------------------------------------
    def save(self, path, creation_epoch):
        objs = []   # list of bytes (object bodies), 1-indexed ids

        def add(body):
            objs.append(body if isinstance(body, bytes) else body.encode("latin-1"))
            return len(objs)

        def stream(d, data, compress=True):
            raw = data
            if compress:
                raw = zlib.compress(data, 9)
                d += " /Filter /FlateDecode"
            return ("<< %s /Length %d >>\nstream\n" % (d, len(raw))).encode("latin-1") + raw + b"\nendstream"

        catalog_id = add(b"")      # 1
        pages_id = add(b"")        # 2
        font_ids = {}
        for f in self.fonts:
            ff = add(stream("/Length1 %d" % len(f.data), f.data))
            tt = f.tt
            bb = [tt["head"].xMin, tt["head"].yMin, tt["head"].xMax, tt["head"].yMax]
            scale = 1000.0 / f.upm
            fd = add("<< /Type /FontDescriptor /FontName /%s /Flags 34 /FontBBox [%d %d %d %d] "
                     "/ItalicAngle 0 /Ascent %d /Descent %d /CapHeight %d /StemV %d /FontFile2 %d 0 R >>" % (
                         f.psname, bb[0] * scale, bb[1] * scale, bb[2] * scale, bb[3] * scale,
                         880 * scale, -300 * scale, 650 * scale, 90 if "Bold" in f.psname else 50, ff))
            used = sorted(f.used)
            ws = " ".join("%d [%d]" % (g, round(f.hmtx[f.order[g]][0] * scale)) for g in used)
            cid = add("<< /Type /Font /Subtype /CIDFontType2 /BaseFont /%s /CIDSystemInfo << /Registry (Adobe) "
                      "/Ordering (Identity) /Supplement 0 >> /FontDescriptor %d 0 R /DW 600 /W [%s] "
                      "/CIDToGIDMap /Identity >>" % (f.psname, fd, ws))
            lines = ["/CIDInit /ProcSet findresource begin 12 dict begin begincmap",
                     "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def",
                     "/CMapName /Adobe-Identity-UCS def /CMapType 2 def",
                     "1 begincodespacerange <0000> <FFFF> endcodespacerange"]
            items = [(g, f.gid2uni[g]) for g in used if g in f.gid2uni]
            for k in range(0, len(items), 100):
                chunk = items[k:k + 100]
                lines.append("%d beginbfchar" % len(chunk))
                for g, u in chunk:
                    if u > 0xFFFF:
                        u -= 0x10000
                        h = "%04X%04X" % (0xD800 + (u >> 10), 0xDC00 + (u & 0x3FF))
                    else:
                        h = "%04X" % u
                    lines.append("<%04X> <%s>" % (g, h))
                lines.append("endbfchar")
            lines.append("endcmap CMapName currentdict /CMap defineresource pop end end")
            tu = add(stream("", "\n".join(lines).encode("latin-1")))
            t0 = add("<< /Type /Font /Subtype /Type0 /BaseFont /%s /Encoding /Identity-H "
                     "/DescendantFonts [%d 0 R] /ToUnicode %d 0 R >>" % (f.psname, cid, tu))
            font_ids[f.res] = t0
        page_ids = []
        for p in self.pages:
            content = add(stream("", "\n".join(p.ops).encode("latin-1")))
            res = " ".join("/%s %d 0 R" % (f.res, font_ids[f.res]) for f in self.fonts)
            pid = add("<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %.3f %.3f] /Contents %d 0 R "
                      "/Resources << /Font << %s >> >> >>" % (pages_id, A4[0], A4[1], content, res))
            page_ids.append(pid)
        objs[pages_id - 1] = ("<< /Type /Pages /Kids [%s] /Count %d >>" % (
            " ".join("%d 0 R" % i for i in page_ids), len(page_ids))).encode()
        objs[catalog_id - 1] = ("<< /Type /Catalog /Pages %d 0 R /Lang (he) >>" % pages_id).encode()
        d = time.strftime("D:%Y%m%d%H%M%SZ", time.gmtime(creation_epoch))
        info = add("<< /Title (%s) /Producer (SW Book Text specimen builder: custom Python writer) "
                   "/Creator (HarfBuzz via uharfbuzz) /CreationDate (%s) /ModDate (%s) >>" % (
                       self.title.replace("(", "").replace(")", ""), d, d))
        out = bytearray(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n")
        offs = []
        for i, body in enumerate(objs, 1):
            offs.append(len(out))
            out += ("%d 0 obj\n" % i).encode() + body + b"\nendobj\n"
        xref = len(out)
        out += ("xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)).encode()
        for o in offs:
            out += ("%010d 00000 n \n" % o).encode()
        out += ("trailer\n<< /Size %d /Root %d 0 R /Info %d 0 R /ID [<%s> <%s>] >>\nstartxref\n%d\n%%%%EOF\n" % (
            len(objs) + 1, catalog_id, info, "5357424f4f4b5445585400000000a001", "5357424f4f4b5445585400000000a001",
            xref)).encode()
        with open(path, "wb") as fh:
            fh.write(out)
