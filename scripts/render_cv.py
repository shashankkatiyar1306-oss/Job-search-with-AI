#!/usr/bin/env python3
"""Render a CV JSON file (same shape as cv_master.json) to a 2-page A4 PDF.

Usage: python3 render_cv.py <cv.json> <output.pdf>
Needs google-chrome (or chromium) for HTML-to-PDF. Fonts are read from ./fonts next to this script.
"""
import base64, html, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
NAVY = "#1f3a68"


def ensure_fonts():
    """Fetch the Lato font files from npm if they are not next to this script."""
    fdir = os.path.join(HERE, "fonts")
    if os.path.exists(os.path.join(fdir, "lato-latin-700-italic.woff2")):
        return
    os.makedirs(fdir, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["npm", "pack", "@fontsource/lato@5", "--silent"], cwd=td, check=True, capture_output=True)
        tgz = [f for f in os.listdir(td) if f.endswith(".tgz")][0]
        subprocess.run(["tar", "xzf", tgz], cwd=td, check=True)
        for w in ("400", "700"):
            for s in ("normal", "italic"):
                n = f"lato-latin-{w}-{s}.woff2"
                shutil.copy(os.path.join(td, "package", "files", n), os.path.join(fdir, n))


def font_face(weight, style, fname):
    path = os.path.join(HERE, "fonts", fname)
    data = base64.b64encode(open(path, "rb").read()).decode()
    return (f"@font-face{{font-family:'Lato';font-weight:{weight};font-style:{style};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")


def e(s):
    return html.escape(s or "")


def build_html(cv):
    fonts = "".join([
        font_face(400, "normal", "lato-latin-400-normal.woff2"),
        font_face(700, "normal", "lato-latin-700-normal.woff2"),
        font_face(400, "italic", "lato-latin-400-italic.woff2"),
        font_face(700, "italic", "lato-latin-700-italic.woff2"),
    ])
    css = fonts + f"""
    @page {{ size: A4; margin: 11mm 13mm 10mm 13mm; }}
    * {{ box-sizing: border-box; }}
    body {{ font-family: 'Lato', sans-serif; font-size: 9.4pt; line-height: 1.28; color: #111; margin: 0; }}
    h1 {{ text-align:center; color:{NAVY}; font-size: 19pt; margin: 0 0 2pt; letter-spacing: .3pt; }}
    .headline {{ text-align:center; font-weight:700; font-size: 11pt; margin-bottom: 2pt; }}
    .line {{ text-align:center; font-size: 9pt; margin: 0; }}
    h2 {{ color:{NAVY}; font-size: 11pt; margin: 7pt 0 3pt; padding-bottom: 1.5pt; border-bottom: 1.4pt solid {NAVY}; }}
    p {{ margin: 0 0 5pt; text-align: justify; }}
    ul {{ margin: 0 0 3pt; padding-left: 15pt; }}
    li {{ margin: 0 0 1pt; }}
    .cols {{ columns: 2; column-gap: 18pt; }}
    .cols li {{ break-inside: avoid; }}
    .job {{ margin-top: 4pt; }}
    .jobhead {{ display:flex; justify-content:space-between; font-weight:700; color:{NAVY}; }}
    .jobhead .d {{ color:#111; }}
    .company {{ font-style: italic; margin-bottom: 1.5pt; }}
    .grp {{ font-weight:700; margin: 2pt 0 1pt; }}
    .edu {{ display:flex; justify-content:space-between; font-weight:700; }}
    .school {{ font-style: italic; }}
    """
    out = [f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>"]
    out.append(f"<h1>{e(cv['name'])}</h1>")
    out.append(f"<div class='headline'>{e(cv['headline'])}</div>")
    out.append(f"<div class='line'>{e(cv['tagline'])}</div>")
    out.append(f"<div class='line'>{e(cv['contact'])}</div>")

    out.append("<h2>PROFESSIONAL SUMMARY</h2>")
    for para in cv["summary"]:
        out.append(f"<p>{e(para)}</p>")

    if cv.get("ai_bullets"):
        out.append(f"<h2>{e(cv.get('ai_section_title', 'AI IN eLEARNING'))}</h2><ul>")
        out += [f"<li>{e(b)}</li>" for b in cv["ai_bullets"]]
        out.append("</ul>")

    out.append("<h2>CORE COMPETENCIES</h2><ul class='cols'>")
    out += [f"<li>{e(c)}</li>" for c in cv["competencies"]]
    out.append("</ul>")

    out.append("<h2>PROFESSIONAL EXPERIENCE</h2>")
    for job in cv["experience"]:
        out.append("<div class='job'>")
        out.append(f"<div class='jobhead'><span>{e(job['title'])}</span><span class='d'>{e(job['dates'])}</span></div>")
        out.append(f"<div class='company'>{e(job['company'])}</div>")
        for g in job["groups"]:
            if g.get("heading"):
                out.append(f"<div class='grp'>{e(g['heading'])}</div>")
            out.append("<ul>" + "".join(f"<li>{e(b)}</li>" for b in g["bullets"]) + "</ul>")
        out.append("</div>")

    out.append("<h2>TOOLS &amp; METHODS</h2><ul>")
    out += [f"<li><b>{e(t['label'])}:</b> {e(t['text'])}</li>" for t in cv["tools"]]
    out.append("</ul>")

    ed = cv["education"]
    out.append("<h2>EDUCATION</h2>")
    out.append(f"<div class='edu'><span>{e(ed['degree'])}</span><span>{e(ed['dates'])}</span></div>")
    out.append(f"<div class='school'>{e(ed['school'])}</div>")
    out.append("</body></html>")
    return "\n".join(out)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    cv = json.load(open(src, encoding="utf-8"))
    ensure_fonts()
    chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if not chrome:
        sys.exit("No Chrome/Chromium found for PDF rendering")
    with tempfile.TemporaryDirectory() as td:
        page = os.path.join(td, "cv.html")
        open(page, "w", encoding="utf-8").write(build_html(cv))
        subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                        "--no-pdf-header-footer", f"--print-to-pdf={os.path.abspath(dst)}",
                        "file://" + page], check=True, capture_output=True, timeout=120)
    print(dst)


if __name__ == "__main__":
    main()
