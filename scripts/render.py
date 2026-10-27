# Kênh khoa học short: 9:16 dark grain render. Fixed hook on top (white + yellow, hand-cut jitter font),
# glowing rounded square media frame, karaoke captions over the frame's lower part, coloured sparkles.
# Everything per-video lives in <project>/edit.json (hook, credit, timeline) and <project>/build/words.json.
# Usage (run from the project folder):
#   python -I -X utf8 <skill>/scripts/render.py            full render  -> build/video.mp4
#   python -I -X utf8 <skill>/scripts/render.py 15         first 15 s   -> build/video_15s.mp4
#   python -I -X utf8 <skill>/scripts/render.py @80        one frame    -> build/preview_80.png
import json, math, os, subprocess, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARG = sys.argv[1] if len(sys.argv) > 1 else ""
PREVIEW = float(ARG[1:]) if ARG.startswith("@") else None
LIMIT = float(ARG) if ARG and PREVIEW is None else None
W, H, FPS = 1080, 1920, 30
FW = FH = 940
FX, FY = (W - FW) // 2, 610
CAP_Y = FY + FH - 120                         # caption baseline area, inside the frame
WHITE, YELLOW, BLACK = (255, 255, 255), (255, 216, 77), (0, 0, 0)
PINK, BLUE = (255, 128, 182), (110, 168, 255)  # accent sparkles only

words = json.load(open("build/words.json", encoding="utf-8"))
TOTAL = words[-1]["end"] + 1.8
if LIMIT:
    TOTAL = min(TOTAL, LIMIT)
NF = int(TOTAL * FPS)

# ---------- per-video config ----------
CFG = json.load(open("edit.json", encoding="utf-8"))
TL = [tuple(x) for x in CFG["timeline"]]          # [start_s, path, offset_s]; .png = still (paper figure)
HOOK = CFG["hook"]                                # [[[text, "W"|"Y"], ...], line2]
PAPER_CREDIT = CFG.get("credit", "")
KEEP_CASE = CFG.get("keep_case", [])              # words that must not be upper-cased, e.g. "fMRI"


def nunito(size, wght):
    f = ImageFont.truetype(os.path.join(SKILL, "assets", "fonts", "Nunito.ttf"), size)
    f.set_variation_by_axes([wght])
    return f


F_HEAD = nunito(54, 900)
F_CAP = nunito(50, 900)
F_SMALL = nunito(26, 800)
TRACK_HEAD, TRACK_CAP = 1, 0
SQUISH = 0.9          # narrow the glyphs a bit, like the reference
BOIL_EVERY = 4        # frames between jitter variants ("run run nhẹ")
N_BOIL = 3


def up(s):
    s = s.upper()
    for k in KEEP_CASE:
        s = s.replace(k.upper(), k)
    return s


def star(size, color):
    """4-point sparkle sprite with soft glow (RGBA)."""
    s = size * 3
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    c, r, k = s / 2, size / 2, size * 0.12
    g = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((c - r * 0.5, c - r * 0.5, c + r * 0.5, c + r * 0.5), fill=color + (170,))
    im = Image.alpha_composite(im, g.filter(ImageFilter.GaussianBlur(size * 0.3)))
    pts = [(c, c - r), (c + k, c - k), (c + r, c), (c + k, c + k), (c, c + r), (c - k, c + k), (c - r, c), (c - k, c - k)]
    ImageDraw.Draw(im).polygon(pts, fill=color + (255,))
    return im


# ---------- background: black + vignette, animated film grain ----------
def make_bg():
    bg = Image.new("RGBA", (W, H), (10, 10, 10, 255))
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).ellipse((-300, 200, W + 300, H - 100), fill=60)
    lift = Image.new("RGBA", (W, H), (40, 34, 30, 255))
    bg.paste(lift, (0, 0), v.filter(ImageFilter.GaussianBlur(220)))
    return bg


def make_grain(seed):
    rnd = random.Random(seed)
    small = Image.effect_noise((W // 2, H // 2), 60).point(lambda p: p)
    small = small.rotate(rnd.choice([0, 180]))
    g = small.resize((W, H), Image.NEAREST)
    lay = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    lay.putalpha(g.point(lambda p: max(0, p - 128) // 5))  # bright specks only, subtle
    return lay


BG = make_bg()
GRAINS = [make_grain(i) for i in range(6)]

# ---------- frame: rounded square with soft warm glow ----------
RAD = 48
MASK = Image.new("L", (FW, FH), 0)
ImageDraw.Draw(MASK).rounded_rectangle((0, 0, FW - 1, FH - 1), RAD, fill=255)
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(glow).rounded_rectangle((FX - 6, FY - 6, FX + FW + 6, FY + FH + 6), RAD + 6, fill=(255, 236, 200, 120))
GLOW = glow.filter(ImageFilter.GaussianBlur(26))
BASE = Image.alpha_composite(BG, GLOW)

rnd = random.Random(7)
STARS = []
for x, y, s, c in [(160, 412, 42, PINK), (895, 395, 14, WHITE), (912, 500, 46, YELLOW), (185, 515, 12, BLUE),
                   (640, 478, 10, YELLOW), (FX + FW - 8, FY - 10, 52, BLUE), (FX + 10, FY + FH + 24, 48, PINK),
                   (980, 250, 18, PINK), (110, 300, 14, BLUE), (70, 1760, 18, BLUE), (1000, 1690, 42, YELLOW),
                   (860, 1820, 14, PINK), (200, 1660, 12, WHITE)]:
    STARS.append((x, y, star(s, c), rnd.uniform(0, 6.28), rnd.uniform(1.2, 2.2)))


# ---------- media readers ----------
def probe_dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))


def video_frames(f, off, dur):
    avail = probe_dur(f) - off
    k = max(1.0, dur / avail)  # slow down only if the clip is too short
    n = int(round(dur * FPS))
    cmd = ["ffmpeg", "-v", "error", "-ss", str(off), "-i", f, "-an",
           "-vf", f"setpts={k}*PTS,fps={FPS},scale={FW}:{FH}:force_original_aspect_ratio=increase,crop={FW}:{FH}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    last = None
    for _ in range(n):
        buf = p.stdout.read(FW * FH * 3)
        if len(buf) == FW * FH * 3:
            last = Image.frombytes("RGB", (FW, FH), buf)
        yield last
    p.kill()


def still_frames(f, dur):
    # paper figure: fit inside a white card, slow zoom
    src = Image.open(f).convert("RGB")
    pad = 36
    r = min((FW - 2 * pad) / src.width, (FH - 2 * pad - 190) / src.height)  # keep clear of captions
    n = int(round(dur * FPS))
    for i in range(n):
        z = 1.0 + 0.08 * (i / max(1, n - 1))
        w, h = int(src.width * r * z), int(src.height * r * z)
        card = Image.new("RGB", (FW, FH), WHITE)
        card.paste(src.resize((w, h), Image.LANCZOS), ((FW - w) // 2, (FH - 190 - h) // 2 + 10))
        yield card


def media_stream():
    for i, (t0, f, off) in enumerate(TL):
        t1 = TL[i + 1][0] if i + 1 < len(TL) else TOTAL
        # frame counts from rounded boundaries so segments always sum to NF
        dur = (round(min(t1, TOTAL) * FPS) - round(t0 * FPS)) / FPS
        if dur <= 0:
            continue
        gen = still_frames(f, dur) if f.endswith(".png") else video_frames(f, off, dur)
        for k, fr in enumerate(gen):
            yield fr, k, f.endswith(".png")


# ---------- hand-cut text: rough edges + per-letter jitter ----------
COL = {"W": WHITE, "Y": YELLOW}


def char_w(f, ch):
    return f.getlength(ch) * SQUISH


def line_w(f, s, tr):
    return sum(char_w(f, ch) for ch in s) + tr * (len(s) - 1)


def roughen(im, seed):
    a = im.getchannel("A").filter(ImageFilter.GaussianBlur(1.1))
    random.seed(seed)
    n = Image.effect_noise(im.size, 90)
    a = Image.blend(a, n, 0.15).point(lambda p: 255 if p > 118 else 0).filter(ImageFilter.GaussianBlur(0.5))
    im.putalpha(a)
    return im


def text_layer(lines, f, tr, seed, height, line_h, shadow=True):
    """lines: [[(text, colour), ...], ...] centered; each glyph slightly rotated/offset by seed."""
    r = random.Random(seed)
    lay = Image.new("RGBA", (W, height), (0, 0, 0, 0))
    gs = int(f.size * 2)
    for li, parts in enumerate(lines):
        s = "".join(t for t, _ in parts)
        x = (W - line_w(f, s, tr)) / 2
        base = int(line_h * (li + 1))
        for txt, col in parts:
            for ch in txt:
                if ch != " ":
                    g = Image.new("RGBA", (gs, gs), (0, 0, 0, 0))
                    ImageDraw.Draw(g).text((gs // 4, int(gs * 0.75)), ch, font=f, fill=COL.get(col, col) if isinstance(col, str) else col,
                                           anchor="ls")
                    g = g.resize((int(gs * SQUISH), gs), Image.BICUBIC)
                    g = g.rotate(r.uniform(-3.5, 3.5), resample=Image.BICUBIC)
                    lay.alpha_composite(g, (int(x - gs * SQUISH / 4), base - int(gs * 0.75) + int(r.uniform(-2.5, 2.5))))
                x += char_w(f, ch) + tr
    lay = roughen(lay, seed)
    if not shadow:
        return lay
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    sh.putalpha(lay.getchannel("A").filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(5)))
    out = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (3, 5))
    out.alpha_composite(lay)
    return out


HOOK_H = 210
HOOK_IMGS = [text_layer(HOOK, F_HEAD, TRACK_HEAD, 100 + i, HOOK_H, 80) for i in range(N_BOIL)]
HOOK_Y = FY - HOOK_H - 40


# ---------- captions ----------
def chunks(maxc=18):
    out, cur = [], []
    for w in words:
        if cur and (len(" ".join(x["w"] for x in cur + [w])) > maxc):
            out.append(cur); cur = []
        cur.append(w)
        if w["w"][-1] in ".?!,":
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    res = []
    for i, c in enumerate(out):
        start = c[0]["start"]
        end = out[i + 1][0]["start"] if i + 1 < len(out) else c[-1]["end"] + 0.6
        res.append((start, min(end, c[-1]["end"] + 0.8), c))
    return res


CHUNKS = chunks()
cap_cache = {}


def strip_punct(s):
    return s[:-3] if s.endswith("...") else s.rstrip(".,?!…")


def render_cap(ci, active, var):
    key = (ci, active, var)
    if key in cap_cache:
        return cap_cache[key]
    toks = [up(strip_punct(w["w"])) for w in CHUNKS[ci][2]]
    parts = [(t + (" " if i < len(toks) - 1 else ""), "Y" if i == active else "W") for i, t in enumerate(toks)]
    im = text_layer([parts], F_CAP, TRACK_CAP, ci * 10 + var, 160, 105)
    # dark outline so captions stay readable over bright footage
    ol = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ol.putalpha(im.getchannel("A").filter(ImageFilter.MaxFilter(9)))
    im = Image.alpha_composite(ol, im)
    cap_cache[key] = im
    return im


def cap_at(t):
    for i, (s, e, c) in enumerate(CHUNKS):
        if s <= t < e:
            act = max(j for j, w in enumerate(c) if w["start"] <= t) if c[0]["start"] <= t else 0
            return i, act, t - s
    return None


def ease_out(u):
    u = min(1, max(0, u))
    return 1 - (1 - u) ** 3


credit = Image.new("RGBA", (W, 50), (0, 0, 0, 0))
ImageDraw.Draw(credit).text((W // 2, 25), PAPER_CREDIT, font=F_SMALL, fill=(170, 170, 170), anchor="mm")
# optional label under archive footage, e.g. "(Hình ảnh minh họa)"
ILLUS = CFG.get("illus_label", "")
illus = Image.new("RGBA", (W, 50), (0, 0, 0, 0))
ImageDraw.Draw(illus).text((W // 2, 25), ILLUS, font=F_SMALL, fill=(170, 170, 170), anchor="mm")


def compose(t, fi, media, k, is_paper):
    fr = BASE.copy()
    # pop-in on each new shot
    sc = 0.94 + 0.06 * ease_out(k / 9)
    if sc < 0.999:
        mw, mh = int(FW * sc), int(FH * sc)
        m2 = Image.new("RGB", (FW, FH), (10, 10, 10))
        m2.paste(media.resize((mw, mh), Image.BILINEAR), ((FW - mw) // 2, (FH - mh) // 2))
        media = m2
    fr.paste(media, (FX, FY), MASK)
    if is_paper and PAPER_CREDIT:
        fr.alpha_composite(credit, (0, FY + FH + 40))
    elif not is_paper and ILLUS:
        fr.alpha_composite(illus, (0, FY + FH + 40))
    var = (fi // BOIL_EVERY) % N_BOIL
    fr.alpha_composite(HOOK_IMGS[var], (0, HOOK_Y))
    # captions
    ca = cap_at(t)
    if ca:
        ci, act, ct = ca
        cimg = render_cap(ci, act, var)
        cu = ease_out(ct / 0.15)
        if cu < 1:
            cw, ch = int(W * (0.92 + 0.08 * cu)), int(160 * (0.92 + 0.08 * cu))
            fr.alpha_composite(cimg.resize((cw, ch), Image.BILINEAR), ((W - cw) // 2, CAP_Y - ch // 2))
        else:
            fr.alpha_composite(cimg, (0, CAP_Y - 80))
    # twinkling sparkles
    for x, y, spr, ph, sp in STARS:
        a = 0.5 + 0.5 * math.sin(t * sp + ph)
        sz = max(4, int(spr.width * (0.75 + 0.3 * a)))
        st = spr.resize((sz, sz), Image.BILINEAR)
        st.putalpha(st.getchannel("A").point(lambda v, a=a: int(v * (0.3 + 0.7 * a))))
        fr.alpha_composite(st, (x - sz // 2, y - sz // 2))
    fr.alpha_composite(GRAINS[(fi // 2) % len(GRAINS)])  # grain over everything, changes every 2 frames
    return fr.convert("RGB")


if PREVIEW is not None:
    i = max(j for j, s in enumerate(TL) if s[0] <= PREVIEW)
    t0, f, off = TL[i]
    k = int((PREVIEW - t0) * FPS)
    gen = still_frames(f, k / FPS + 0.1) if f.endswith(".png") else video_frames(f, off + (PREVIEW - t0), 0.1)
    compose(PREVIEW, 0, list(gen)[-1], 99, f.endswith(".png")).save(f"build/preview_{int(PREVIEW)}.png")
    sys.exit()

out = f"build/video_{int(LIMIT)}s.mp4" if LIMIT else "build/video.mp4"  # partial runs never clobber a full render
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out],
                       stdin=subprocess.PIPE)
ms = media_stream()
for fi in range(NF):
    media, k, is_paper = next(ms)
    enc.stdin.write(compose(fi / FPS, fi, media, k, is_paper).tobytes())
    if fi % 300 == 0:
        print(f"{fi / FPS:6.1f}s / {TOTAL:.1f}s", flush=True)
enc.stdin.close()
enc.wait()
print("done", out)
