#!/usr/bin/env python3
"""Render a CV JSON file (same shape as cv_master.json) to a compact .docx.

Usage: python3 render_docx.py <cv.json> <output.docx>
Kept small (no embedded fonts or images) so it can be uploaded to Naukri from page script.
"""
import json, sys
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Mm, RGBColor

NAVY = RGBColor(0x1F, 0x3A, 0x68)
FONT = "Calibri"


def para(doc, text="", size=9.5, bold=False, italic=False, color=None, align=None, after=1.5, before=0):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after, pf.space_before, pf.line_spacing = Pt(after), Pt(before), 1.05
    if align:
        p.alignment = align
    if text:
        r = p.add_run(text)
        r.font.size, r.bold, r.italic = Pt(size), bold, italic
        if color:
            r.font.color.rgb = color
    return p


def heading(doc, text):
    p = para(doc, text, size=11, bold=True, color=NAVY, before=6, after=2)
    pPr = p._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    for k, v in (("w:val", "single"), ("w:sz", "10"), ("w:space", "1"), ("w:color", "1F3A68")):
        b.set(qn(k), v)
    bdr.append(b)
    pPr.append(bdr)


def bullet(doc, text, bold_label=None):
    p = doc.add_paragraph(style="List Bullet")
    pf = p.paragraph_format
    pf.space_after, pf.line_spacing = Pt(1), 1.05
    if bold_label:
        r = p.add_run(bold_label + ": ")
        r.bold, r.font.size = True, Pt(9.5)
    r = p.add_run(text)
    r.font.size = Pt(9.5)


def two_side(doc, left, right, color=None, size=9.5):
    p = para(doc, after=0, before=3)
    p.paragraph_format.tab_stops.add_tab_stop(Mm(184), WD_TAB_ALIGNMENT.RIGHT)
    r = p.add_run(left)
    r.bold, r.font.size = True, Pt(size)
    if color:
        r.font.color.rgb = color
    r2 = p.add_run("\t" + right)
    r2.bold, r2.font.size = True, Pt(size)


def main():
    cv = json.load(open(sys.argv[1], encoding="utf-8"))
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    sec.left_margin = sec.right_margin = Mm(13)
    sec.top_margin, sec.bottom_margin = Mm(11), Mm(10)
    st = doc.styles["Normal"]
    st.font.name, st.font.size = FONT, Pt(9.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

    C = WD_ALIGN_PARAGRAPH.CENTER
    para(doc, cv["name"], size=19, bold=True, color=NAVY, align=C, after=1)
    para(doc, cv["headline"], size=11, bold=True, align=C, after=1)
    para(doc, cv["tagline"], size=9, align=C, after=0)
    para(doc, cv["contact"], size=9, align=C, after=2)

    heading(doc, "PROFESSIONAL SUMMARY")
    for s in cv["summary"]:
        p = para(doc, s, after=4)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    if cv.get("ai_bullets"):
        heading(doc, cv.get("ai_section_title", "AI IN eLEARNING"))
        for b in cv["ai_bullets"]:
            bullet(doc, b)

    heading(doc, "CORE COMPETENCIES")
    comps = cv["competencies"]
    half = (len(comps) + 1) // 2
    t = doc.add_table(rows=1, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for col, items in enumerate((comps[:half], comps[half:])):
        cell = t.rows[0].cells[col]
        cell.paragraphs[0].text = ""
        for i, c in enumerate(items):
            p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
            p.style = doc.styles["List Bullet"]
            p.paragraph_format.space_after = Pt(1)
            p.add_run(c).font.size = Pt(9.5)

    heading(doc, "PROFESSIONAL EXPERIENCE")
    for job in cv["experience"]:
        two_side(doc, job["title"], job["dates"], color=NAVY)
        para(doc, job["company"], italic=True, after=1)
        for g in job["groups"]:
            if g.get("heading"):
                para(doc, g["heading"], bold=True, after=1, before=1)
            for b in g["bullets"]:
                bullet(doc, b)

    heading(doc, "TOOLS & METHODS")
    for tl in cv["tools"]:
        bullet(doc, tl["text"], bold_label=tl["label"])

    heading(doc, "EDUCATION")
    ed = cv["education"]
    two_side(doc, ed["degree"], ed["dates"])
    para(doc, ed["school"], italic=True, after=0)

    doc.core_properties.author = cv["name"].title()
    doc.core_properties.title = cv["name"].title() + " - Resume"
    doc.save(sys.argv[2])
    slim(sys.argv[2])
    print(sys.argv[2])


def slim(path):
    """Drop unused template parts (thumbnail, effects styles, unused styles) to keep the file tiny."""
    import re, zipfile, io
    from lxml import etree
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    drop = {"word/stylesWithEffects.xml", "docProps/thumbnail.jpeg", "customXml/item1.xml",
            "customXml/_rels/item1.xml.rels", "customXml/itemProps1.xml"}
    zin = zipfile.ZipFile(path)
    files = {n: zin.read(n) for n in zin.namelist() if n not in drop}
    zin.close()
    used = set(re.findall(rb'w:(?:pStyle|rStyle|tblStyle) w:val="([^"]+)"', files["word/document.xml"]))
    used |= {b"Normal", b"ListBullet", b"DefaultParagraphFont", b"TableNormal", b"NoList", b"ListParagraph"}
    st = etree.fromstring(files["word/styles.xml"])
    for s in st.findall(f"{{{W}}}style"):
        if s.get(f"{{{W}}}styleId").encode() not in used:
            st.remove(s)
    for ls in st.findall(f"{{{W}}}latentStyles"):
        st.remove(ls)
    files["word/styles.xml"] = etree.tostring(st, xml_declaration=True, encoding="UTF-8", standalone=True)
    for n in ("[Content_Types].xml", "_rels/.rels", "word/_rels/document.xml.rels"):
        x = files[n].decode()
        x = re.sub(r'<(Override|Relationship)[^>]*(stylesWithEffects|thumbnail|customXml|itemProps)[^>]*/>', "", x)
        files[n] = x.encode()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n, b in files.items():
            z.writestr(n, b)
    open(path, "wb").write(buf.getvalue())


if __name__ == "__main__":
    main()
