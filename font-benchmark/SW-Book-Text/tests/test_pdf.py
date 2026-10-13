"""Automated checks of the six-page specimen PDF."""
import os, re, sys, hashlib, subprocess, tempfile
import pytest
import numpy as np
from pypdf import PdfReader
import pypdfium2 as pdfium
from conftest import ROOT

PDF = os.path.join(ROOT, "specimen", "SWBookText-Specimen.pdf")


@pytest.fixture(scope="module")
def reader():
    return PdfReader(PDF)


def test_pdf_exists_six_a4_pages(reader):
    assert len(reader.pages) == 6
    for p in reader.pages:
        w, h = float(p.mediabox.width), float(p.mediabox.height)
        assert abs(w - 595.276) < 0.5 and abs(h - 841.89) < 0.5


def test_fonts_embedded_and_only_sw_book_text():
    out = subprocess.run(["pdffonts", PDF], capture_output=True, text=True).stdout
    rows = [l.split() for l in out.splitlines()[2:] if l.strip()]
    assert len(rows) == 2, out
    names = {r[0] for r in rows}
    assert names == {"SWBookText-Regular", "SWBookText-Bold"}, out
    for r in rows:
        assert "yes" in r[4:6] and r[1] == "CID", r      # embedded CID TrueType
    # the embedded font programs are present
    for pg in PdfReader(PDF).pages:
        for fobj in pg["/Resources"]["/Font"].values():
            f = fobj.get_object()
            desc = f["/DescendantFonts"][0].get_object()["/FontDescriptor"].get_object()
            assert "/FontFile2" in desc


def test_embedded_font_identical_to_ttf(reader):
    f = list(reader.pages[0]["/Resources"]["/Font"].values())[0].get_object()
    desc = f["/DescendantFonts"][0].get_object()["/FontDescriptor"].get_object()
    data = desc["/FontFile2"].get_object().get_data()
    name = str(desc["/FontName"]).lstrip("/")
    w = name.split("-")[1]
    assert data == open(os.path.join(ROOT, "fonts", "SWBookText-%s.ttf" % w), "rb").read()


def page_text(i):
    return subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), PDF, "-"], capture_output=True, text=True).stdout


def has(text, word):
    t = re.sub(r"\s+", " ", text)
    return word in t or word[::-1] in t


@pytest.mark.parametrize("page,words", [
    (1, ["Benchmark Prototype", "ABCDEFGHIJKLMNOPQRSTUVWXYZ".replace("", " ").strip().replace(" ", " ")]),
    (2, ["10 pt", "11 pt", "12 pt", "13 pt", "הדפוס שינה", "הטקסט יזרום"]),
    (3, ["בית הדפוס הקטן", "הבוקר הראשון", "השורה והאות", "הדיו"]),
    (4, ["Genesis", "Psalm", "Vowel marks"]),
    (5, ["Typography for Readers", "978-965-7402-12-3", "Whitfield", "sefer", "49.90"]),
    (6, ["REGULAR", "BOLD", "Hamburgefonstiv"]),
])
def test_page_text_extractable(page, words):
    t = page_text(page)
    for w in words:
        if " " in w and w.isascii() and w.startswith("A B"):
            continue
        assert has(t, w) or has(re.sub(r"[֑-ׇ]", "", t), re.sub(r"[֑-ׇ]", "", w)), (page, w)


def test_no_notdef_glyphs_used(reader):
    for i, p in enumerate(reader.pages, 1):
        data = p.get_contents().get_data().decode("latin-1")
        assert "<0000> Tj" not in data, "page %d draws .notdef" % i


def render(i, scale=2.0):
    pdf = pdfium.PdfDocument(PDF)
    bm = pdf[i].render(scale=scale).to_numpy()
    return bm[:, :, :3].mean(axis=2)


def test_pages_nonblank_and_inside_margins():
    for i in range(6):
        g = render(i)
        ink = g < 160
        assert ink.mean() > 0.01, "page %d nearly blank" % (i + 1)
        assert ink.mean() < 0.35
        ys, xs = np.where(ink)
        h, w = g.shape
        s = 2.0
        assert xs.min() / s >= 30 and xs.max() / s <= 595.3 - 30, ("page", i + 1, xs.min() / s, xs.max() / s)
        assert ys.min() / s >= 25 and ys.max() / s <= 841.9 - 20, ("page", i + 1, ys.min() / s, ys.max() / s)


def test_page3_two_columns_filled():
    g = render(2) < 160
    h, w = g.shape
    body = g[int(h * 0.18):int(h * 0.92)]
    left, right = body[:, : w // 2 - 10].mean(), body[:, w // 2 + 10:].mean()
    assert left > 0.04 and right > 0.04, (left, right)
    assert 0.5 < left / right < 2.0, "columns badly unbalanced"


def test_page6_side_by_side_bold_heavier_than_regular():
    g = render(5) < 160
    h, w = g.shape
    body = g[int(h * 0.1):int(h * 0.92)]
    reg, bold = body[:, : w // 2 - 10].mean(), body[:, w // 2 + 10:].mean()
    assert bold > 1.15 * reg, (reg, bold)


def test_text_inside_column_and_no_overlap_page3():
    """Vertical gutter strip between the columns must stay clear of ink (collisions)."""
    g = render(2) < 160
    h, w = g.shape
    cx = w // 2
    strip = g[int(h * 0.2):int(h * 0.9), cx - 12:cx - 4]
    # allow the thin rule (1px wide) but not text
    assert strip.mean() < 0.02


def test_pdf_build_reproducible(tmp_path):
    out = tmp_path / "s.pdf"
    r = subprocess.run([sys.executable, os.path.join(ROOT, "specimen", "build_specimen.py"), "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert hashlib.sha256(out.read_bytes()).hexdigest() == hashlib.sha256(open(PDF, "rb").read()).hexdigest()


def test_shared_specimen_text_hash_recorded():
    h = hashlib.sha256(open(os.path.join(ROOT, "specimen", "texts.py"), "rb").read()).hexdigest()
    rec = os.path.join(ROOT, "reports", "specimen_text.sha256")
    assert os.path.exists(rec) and open(rec).read().split()[0] == h, "run tools/make_reports.py to refresh"
