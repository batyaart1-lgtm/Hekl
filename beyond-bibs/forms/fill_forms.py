"""Types Batya's answers onto Creative Group Marketing's two submission forms.

Usage: python3 fill_forms.py <CREA-REC2.pdf> <CREA-NON42.pdf>
Writes the filled copies next to this script. Fields set to "" stay blank
for handwriting. Needs: pip install pymupdf
"""
import sys, textwrap, pathlib
import pymupdf

OUT = pathlib.Path(__file__).parent
BLUE = (0, 0, 0.55)

# Fill these in, then re-run.
ADDRESS = "105 5th Street"
CITY, STATE, ZIP, COUNTRY = "Lakewood", "NJ", "08701", "USA"
CITIZENSHIP = "Israeli citizen"
OCCUPATION = ""
CONCEPTION = "Summer 2021"

NAME = "Batya Wachmann"
COMPANY = "Crawling Always LLC (brand: Beyond Bibs)"
PHONE = "+1 929-377-2999"
INVENTION = 'Beyond Bibs crawling bib ("Unitary Baby Bib", US Pat. 11,986,026 B2)'

DESCRIPTION = """\
Beyond Bibs is a full-length crawling bib for babies, protected by US utility patent 11,986,026 B2 ("Unitary Baby Bib", granted May 21, 2024, 14 claims). Also Israeli design registration no. 67877 and Israeli patent application no. 286884. Copy of patent, photos and video link attached.

The problem: crawling babies rub against the floor all day. Their clothes get dirty, sometimes for good; bare knees get cold and sore; spit-up and drool soak them. Parents limit floor time to protect clothes, although crawling is important for development.

The product: one front panel covers the chest, belly and both legs, everywhere the baby touches the floor. Soft elastic straps cross in an X behind the back, so the bib closes at the back, not the neck, and stays flat against the body. Three straps on each leg (thigh, knee and heel) keep it in place whether the baby crawls, sits, stands or lies down. The elastic is sewn closed: no snaps or Velcro to wear out, and the baby cannot pull it off. Outer layer: dark, absorbent fabric. Inner layer: soft cotton with a waterproof lining. It goes over any outfit, including dresses and special-occasion clothes, and doubles as a feeding and drool bib. Sizes: 6-12 and 12-18 months.

Second product: a matching eating bib for ages 1-3 (Israeli patent pending) with the same back closure; it cannot be pulled off and nothing rubs the neck.

Market proof: 500+ units sold in Israel at about $33 retail through three baby stores, a network of home sales points and local print ads. Unit cost about $8 in small batches. A UK reseller sells it on Amazon UK. Never marketed in the US or online. Available with a deal: about 200 finished units, 19 rolls of production fabric, packaging and supplier contacts.

Seeking: a license (advance plus royalties) or sale of the full package. Inventor and sole owner.
Video: https://drive.google.com/file/d/1urOBLM5yUDk13d0Yr26_Q_bEkMO9QAlo/view"""


def put(page, x, y, text, size=10):
    if text:
        page.insert_text((x, y), text, fontsize=size, fontname="helv", color=BLUE)


def data_sheet(src):
    d = pymupdf.open(src)
    p = d[0]
    put(p, 130, 234, NAME)
    put(p, 178, 276, COMPANY)
    put(p, 156, 303, ADDRESS)
    put(p, 122, 331, CITY, 9)
    put(p, 236, 331, STATE, 9)
    put(p, 292, 331, ZIP, 9)
    put(p, 392, 331, COUNTRY, 9)
    put(p, 395, 359, PHONE)
    put(p, 168, 386, CITIZENSHIP, 9)
    put(p, 395, 386, OCCUPATION, 9)
    put(p, 132, 441, "N/A")
    put(p, 162, 579, INVENTION, 9)
    put(p, 172, 621, CONCEPTION)

    p = d[1]
    put(p, 92, 300, "Patent, drawings and photographs attached:", 11)
    for i, line in enumerate([
        "- US Patent 11,986,026 B2 (includes 6 drawing sheets of the design)",
        "- Studio photos: front view, X-strap back view, baby crawling, eating bib",
        "- Video of the bib in use:",
        "  https://drive.google.com/file/d/1urOBLM5yUDk13d0Yr26_Q_bEkMO9QAlo/view",
    ]):
        put(p, 100, 322 + i * 16, line)

    p = d[2]
    lines = []
    for para in DESCRIPTION.split("\n"):
        lines += textwrap.wrap(para, 108) or [""]
    y0, step = 237, 11.55
    for i, line in enumerate(lines):
        put(p, 92, y0 + i * step, line, 7.6)
    if len(lines) > 38:
        print(f"warning: description runs {len(lines)} lines, page holds 38")
    d.save(OUT / "CREA-REC2-filled.pdf")


def confidentiality(src):
    d = pymupdf.open(src)
    p = d[0]
    put(p, 175, 293, NAME, 11)
    put(p, 150, 316, ADDRESS, 10)
    put(p, 95, 340, CITY, 10)
    put(p, 200, 340, STATE, 10)
    put(p, 380, 340, ZIP, 10)
    put(p, 486, 391, PHONE, 9)
    put(p, 190, 500, "Beyond Bibs crawling bib and eating bib", 10)
    put(p, 190, 514, '("Unitary Baby Bib", US Patent 11,986,026 B2)', 10)
    d.save(OUT / "CREA-NON42-filled.pdf")


if __name__ == "__main__":
    data_sheet(sys.argv[1])
    confidentiality(sys.argv[2])
    print("saved to", OUT)
