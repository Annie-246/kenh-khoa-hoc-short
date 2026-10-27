# Build tight "evidence zoom" crops around highlighted phrases; writes crops json for paper_figs.py
#   python -I -X utf8 paper_zoom.py doc.pdf spec.json crops.json
#          spec.json = {"h1_name": [page_no, ["one-line phrase to highlight", ...], 470], ...}  (470 = min width, 110-dpi px)
#          then: paper_figs.py crop doc.pdf crops.json assets/paper
#   python -I -X utf8 paper_zoom.py fade assets/paper/h1_name.png ...   -> fade the cut words at left/right edges
import json, sys, pymupdf
if sys.argv[1] == "fade":
    import numpy as np
    from PIL import Image
    for p in sys.argv[2:]:
        im = np.asarray(Image.open(p).convert("RGB")).astype(float)
        w = im.shape[1]; f = int(w * 0.08); ramp = np.ones(w)
        ramp[:f] = np.linspace(0, 1, f); ramp[-f:] = np.linspace(1, 0, f)
        Image.fromarray((255 - (255 - im) * ramp[None, :, None]).astype("uint8")).save(p)
    sys.exit()
pdf, spec, out = sys.argv[1], sys.argv[2], sys.argv[3]
d = pymupdf.open(pdf); k = 110 / 72
res = {}
for name, (pg, phrases, W) in json.load(open(spec, encoding="utf-8")).items():
    p = d[pg - 1]
    rs = [r for ph in phrases for r in p.search_for(ph)]
    x0 = min(r.x0 for r in rs) * k; x1 = max(r.x1 for r in rs) * k
    y0 = min(r.y0 for r in rs) * k; y1 = max(r.y1 for r in rs) * k
    cx = (x0 + x1) / 2; w = max(W, x1 - x0 + 30)
    L, R = cx - w / 2, cx + w / 2
    if L < 70: L, R = 70, 70 + w
    if R > 876: L, R = 876 - w, 876
    # snap vertically to whole lines: include one full line above and below
    lines = sorted({round(b[1] * k) for b in p.get_text("blocks")} | {round(s["bbox"][1] * k) for bl in p.get_text("dict")["blocks"] for s in bl.get("lines", [])})
    top = [l for l in lines if l < y0 - 5]; top = top[-3] if len(top) >= 3 else (top[0] if top else y0)
    bot = [l for l in lines if l > y1 + 2]; bot = bot[3] if len(bot) > 3 else (bot[-1] + 33 if bot else y1 + 40)
    res[name] = [pg, int(L), int(top - 6), int(R), int(bot - 8), phrases]
    print(name, res[name][:5])
json.dump(res, open(out, "w", encoding="utf-8"))
