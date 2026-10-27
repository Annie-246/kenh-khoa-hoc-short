# Paper/PDF figures for the media frame.
#   pages: python -I -X utf8 paper_figs.py pages doc.pdf outdir        -> outdir/pageN.png at 110 dpi (look at them)
#   crop:  python -I -X utf8 paper_figs.py crop doc.pdf crops.json outdir
#          crops.json = {"p_fig1": [page_no(1-based), x0, y0, x1, y1], ...} in pixels of the 110-dpi page images;
#          writes outdir/<name>.png at 300 dpi.
import json, os, sys
import pymupdf

mode, pdf = sys.argv[1], sys.argv[2]
d = pymupdf.open(pdf)
if mode == "pages":
    out = sys.argv[3]
    os.makedirs(out, exist_ok=True)
    for i, p in enumerate(d):
        p.get_pixmap(dpi=110).save(os.path.join(out, f"page{i + 1}.png"))
    print(d.page_count, "pages ->", out)
else:
    crops, out = json.load(open(sys.argv[3], encoding="utf-8")), sys.argv[4]
    os.makedirs(out, exist_ok=True)
    k = 72 / 110
    for name, (pg, x0, y0, x1, y1, *hl) in crops.items():
        # optional 6th item: list of phrases to mark with a yellow highlighter ("evidence" look)
        page = pymupdf.open(pdf)[pg - 1]  # fresh copy so highlights don't leak into other crops of the same page
        for phrase in (hl[0] if hl else []):
            quads = page.search_for(phrase, quads=True)
            if not quads:
                print("  phrase not found:", phrase)
                continue
            a = page.add_highlight_annot(quads)
            a.set_colors(stroke=(1, 0.86, 0.1))
            a.update()
        pm = page.get_pixmap(dpi=300, clip=pymupdf.Rect(x0 * k, y0 * k, x1 * k, y1 * k), annots=True)
        pm.save(os.path.join(out, name + ".png"))
        print(name, pm.width, pm.height)
