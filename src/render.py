"""Render a vertical (1080x1920) top-N video from a topic JSON file.

python -m src.render topics/001-....json out/            # full video
python -m src.render topics/001-....json out/ --preview  # a few still frames
Env: THEME (optional), PIPER_MODEL (path to .onnx), IMG_DIR (optional photo folder)
"""
import argparse, datetime as dt, hashlib, json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .themes import THEMES, pick_theme
from .voice import synthesize_all
from .util import slug, fmt_num

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")
_fc = {}
def _font(name, size):
    k = (name, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(os.path.join(FONTS, name), size)
    return _fc[k]
BLACK = lambda s: _font("InterDisplay-Black.otf", int(s))
BOLD = lambda s: _font("InterDisplay-Bold.otf", int(s))
SEMI = lambda s: _font("InterDisplay-SemiBold.otf", int(s))
WHITE = (255, 255, 255)
VO_LEAD = 0.2

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_back(t):
    t = clamp(t); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def prog(t, a, b): return clamp((t - a) / (b - a))


class Renderer:
    def __init__(self, topic, theme_name, img_dir=None):
        self.T = topic
        self.th = THEMES[theme_name]; self.theme_name = theme_name
        self.img_dir = img_dir
        self.items = topic["maddeler"]
        self.maxv = max(float(m["deger"]) for m in self.items)
        self.top_name = max(self.items, key=lambda m: float(m["deger"]))["ad"]
        top = np.array(self.th["top"]); bot = np.array(self.th["bot"])
        yy = np.linspace(0, 1, H)[:, None]
        self.BG = Image.fromarray((top + (bot - top) * yy[..., None] ** 1.3).repeat(W, axis=1).astype(np.uint8), "RGB")
        sh = np.concatenate([np.linspace(0.75, 0.35, H // 3), np.full(H - 2 * (H // 3), 0.35), np.linspace(0.35, 0.85, H // 3)])
        self.SHADE = Image.fromarray((np.repeat(sh[:, None], W, 1) * 255).astype(np.uint8), "L")
        self._img = {}
        self.total = 1.0

    # ---------- backgrounds ----------
    def photo(self, key):
        if key in self._img: return self._img[key]
        im = None
        if self.img_dir:
            for ext in (".jpg", ".jpeg", ".png", ".webp"):
                p = os.path.join(self.img_dir, key + ext)
                if os.path.exists(p):
                    im = Image.open(p).convert("RGB")
                    sc = max(W * 1.12 / im.width, H * 1.12 / im.height)
                    im = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1), Image.LANCZOS)
                    break
        self._img[key] = im
        return im

    def photo_bg(self, im, t, dur):
        z = 1.0 + 0.08 * clamp(t / max(dur, 0.1))
        cw, ch = int(W * 1.12 / z), int(H * 1.12 / z)
        cx = im.width / 2 + (im.width - cw) * 0.4 * math.sin(t * 0.3); cy = im.height / 2
        box = (int(cx - cw / 2), int(cy - ch / 2), int(cx - cw / 2) + cw, int(cy - ch / 2) + ch)
        fr = im.crop(box).resize((W, H), Image.BILINEAR)
        tint = Image.blend(fr, self.BG, 0.25)
        return Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), tint, self.SHADE)

    def motif(self, d, gt):
        th = self.th; m = th["motif"]; c = th["circle"]; acc = th["accent"]
        rng = np.random.default_rng(3)
        if m == "waves":
            for i, (base, amp, wl, sp, al) in enumerate([(1560, 28, 520, 0.9, 60), (1640, 34, 680, -0.7, 80), (1730, 30, 460, 1.2, 110)]):
                pts = [(x, base + amp * math.sin(2 * math.pi * (x / wl) + gt * sp * 2 + i)) for x in range(0, W + 20, 20)]
                d.polygon(pts + [(W, H), (0, H)], fill=tuple(int(v * 0.7) for v in c) + (al,))
            for k in range(18):
                x0 = rng.uniform(0, W); spd = rng.uniform(25, 70); r = rng.uniform(3, 9)
                y = (H + 50) - ((gt * spd + rng.uniform(0, H)) % (H + 100)); x = x0 + 12 * math.sin(gt + k)
                d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, 50), width=2)
        elif m == "sun":
            for r, al in ((420, 25), (330, 35), (250, 60)):
                d.ellipse([W / 2 - r, 1500 - r, W / 2 + r, 1500 + r], fill=acc + (al,))
            for i, (base, amp, wl, col) in enumerate([(1600, 70, 900, (60, 15, 50, 200)), (1700, 50, 700, (35, 8, 35, 235))]):
                pts = [(x, base + amp * math.sin(2 * math.pi * x / wl + i * 2 + gt * 0.05)) for x in range(0, W + 20, 20)]
                d.polygon(pts + [(W, H), (0, H)], fill=col)
        elif m == "hills":
            for i, (base, amp, wl, sh) in enumerate([(1450, 90, 1100, 0.55), (1580, 70, 800, 0.38), (1720, 55, 600, 0.22)]):
                pts = [(x, base + amp * math.sin(2 * math.pi * x / wl + i * 1.7 + gt * 0.08 * (i + 1))) for x in range(0, W + 20, 20)]
                d.polygon(pts + [(W, H), (0, H)], fill=tuple(int(v * sh) for v in c) + (235,))
            for k in range(14):
                x = (rng.uniform(0, W) + gt * rng.uniform(10, 30)) % W; y = rng.uniform(300, 1400) + 20 * math.sin(gt + k)
                r = rng.uniform(3, 6); d.ellipse([x - r, y - r, x + r, y + r], fill=acc + (int(60 + 50 * math.sin(gt * 2 + k)),))
        elif m == "stars":
            for k in range(110):
                x = rng.uniform(0, W); y = rng.uniform(0, H); r = rng.uniform(1, 3.5)
                al = int(70 + 80 * (0.5 + 0.5 * math.sin(gt * rng.uniform(1, 3) + k)))
                d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, al))
            sx = (gt * 400) % (W + 800) - 400
            d.line([(sx, 300 + sx * 0.3), (sx - 160, 300 + (sx - 160) * 0.3)], fill=(255, 255, 255, 120), width=3)
        elif m == "embers":
            for k in range(45):
                x0 = rng.uniform(0, W); spd = rng.uniform(60, 160); r = rng.uniform(2, 6)
                y = H + 40 - ((gt * spd + rng.uniform(0, H)) % (H + 80)); x = x0 + 25 * math.sin(gt * 1.5 + k)
                d.ellipse([x - r, y - r, x + r, y + r], fill=acc + (int(90 + 90 * (y / H)),))
        elif m == "grid":
            hy = 1250
            for i in range(-12, 13):
                d.line([(W / 2 + i * 40, hy), (W / 2 + i * 260, H)], fill=c + (70,), width=2)
            off = (gt * 0.6) % 1
            for j in range(12):
                p = ((j + off) / 12) ** 2; y = hy + (H - hy) * p
                d.line([(0, y), (W, y)], fill=c + (int(30 + 80 * p),), width=2)
            d.line([(0, hy), (W, hy)], fill=acc + (160,), width=3)

        elif m == "snow":
            for k in range(90):
                x0 = rng.uniform(0, W); spd = rng.uniform(40, 120); r = rng.uniform(2, 6)
                y = ((gt * spd + rng.uniform(0, H)) % (H + 40)) - 20
                x = x0 + 30 * math.sin(gt * 0.8 + k)
                d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(90 + 20 * r)))
            pts = [(x, 1760 + 25 * math.sin(2 * math.pi * x / 700)) for x in range(0, W + 20, 20)]
            d.polygon(pts + [(W, H), (0, H)], fill=(230, 245, 255, 70))
        elif m == "dunes":
            for i, (base, amp, wl, sh, sp) in enumerate([(1380, 110, 1300, 0.55, 0.03), (1530, 90, 900, 0.40, 0.05), (1700, 70, 700, 0.26, 0.08)]):
                pts = [(x, base + amp * math.sin(2 * math.pi * x / wl + i * 2.1 + gt * sp)) for x in range(0, W + 20, 20)]
                d.polygon(pts + [(W, H), (0, H)], fill=tuple(int(v * sh) for v in c) + (240,))
            for r, al in ((160, 30), (110, 50)):
                d.ellipse([W * 0.78 - r, 330 - r, W * 0.78 + r, 330 + r], fill=acc + (al,))
            for k in range(25):  # drifting sand
                x = (rng.uniform(0, W) + gt * rng.uniform(60, 140)) % W; y = rng.uniform(900, 1700)
                d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=acc + (90,))
        elif m == "aurora":
            for i, (base, amp, col, al) in enumerate([(380, 90, acc, 55), (520, 70, c, 45), (640, 60, acc, 35)]):
                top = [(x, base + amp * math.sin(2 * math.pi * x / (900 + 200 * i) + gt * (0.4 + 0.15 * i) + i)) for x in range(0, W + 20, 20)]
                bot = [(x, y + 160 + 40 * math.sin(x / 140 + gt + i)) for x, y in reversed(top)]
                d.polygon(top + bot, fill=col + (al,))
            for k in range(70):
                x = rng.uniform(0, W); y = rng.uniform(0, H * 0.6); r = rng.uniform(1, 2.5)
                d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(60 + 60 * (0.5 + 0.5 * math.sin(gt * 2 + k)))))
        elif m == "bokeh":
            for k in range(16):
                r = rng.uniform(40, 140); x = (rng.uniform(0, W) + 20 * math.sin(gt * 0.3 + k)) % (W + 200) - 100
                y = (rng.uniform(0, H) - gt * rng.uniform(8, 25)) % (H + 300) - 150
                col = acc if k % 3 == 0 else c
                d.ellipse([x - r, y - r, x + r, y + r], fill=col + (int(18 + 14 * math.sin(gt + k) + 14),))
        elif m == "rings":
            cx, cy = W / 2, 1110
            for k in range(7):
                ph = (gt * 0.25 + k / 7) % 1
                r = 120 + ph * 900
                d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c + (int(110 * (1 - ph)),), width=4)
            for k in range(40):
                x = rng.uniform(0, W); y = rng.uniform(0, H); r = rng.uniform(1, 2.5)
                d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 70))

    def background(self, gt, key=None, t=0.0, dur=1.0):
        im = self.photo(key) if key else None
        if im is not None:
            return self.photo_bg(im, t, dur)
        img = self.BG.copy()
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); self.motif(ImageDraw.Draw(ov), gt)
        img.paste(ov, (0, 0), ov)
        return img

    # ---------- drawing helpers ----------
    def text_c(self, d, y, s, font, fill, alpha=255, stroke=0):
        w = d.textlength(s, font=font)
        d.text(((W - w) / 2, y), s, font=font, fill=fill + (int(alpha),), stroke_width=stroke, stroke_fill=(0, 0, 0, int(alpha * 0.6)))

    def fit(self, d, s, fontf, size, maxw):
        while size > 20 and d.textlength(s, font=fontf(size)) > maxw: size -= 4
        return fontf(size)

    def progress(self, d, gt):
        d.rounded_rectangle([90, 120, W - 90, 134], 7, fill=(255, 255, 255, 50))
        d.rounded_rectangle([90, 120, 90 + (W - 180) * clamp(gt / self.total), 134], 7, fill=self.th["accent"] + (255,))

    # ---------- scenes ----------
    def frame_hook(self, t, gt, dur):
        th = self.th; acc = th["accent"]
        img = self.background(gt, "hook", t, dur).convert("RGBA")
        ov = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(ov)
        self.progress(d, gt)
        b = self.T["baslik"]
        a = ease_out(prog(t, 0, 0.4))
        self.text_c(d, 470 - 60 * (1 - a), b[0], self.fit(d, b[0], BOLD, 86, W - 140), WHITE, 255 * a)
        self.text_c(d, 590, b[1], self.fit(d, b[1], BLACK, 150, W - 100), acc, 255 * a)
        s2 = ease_back(prog(t, 0.25, 0.8))
        f = BLACK(max(10, int(420 * s2)))
        d.text((W / 2, 1000), str(len(self.items)), font=f, fill=WHITE + (255,), anchor="mm")
        if len(b) > 2:
            self.text_c(d, 1190, b[2], self.fit(d, b[2], BLACK, 150, W - 100), WHITE, 255 * ease_out(prog(t, 0.45, 0.8)))
        k = self.T.get("kanca") or []
        if k:
            a3 = ease_out(prog(t, 1.0, 1.4)); dy = 20 * (1 - a3)
            d.rounded_rectangle([90, 1420 + dy, W - 90, 1600 + dy], 40, fill=(0, 0, 0, int(120 * a3)))
            self.text_c(d, 1440 + dy, k[0], self.fit(d, k[0], SEMI, 54, W - 240), WHITE, 255 * a3)
            if len(k) > 1:
                self.text_c(d, 1510 + dy, k[1], self.fit(d, k[1], BLACK, 58, W - 240), acc, 255 * a3)
        img.alpha_composite(ov)
        return img.convert("RGB")

    def frame_item(self, t, gt, dur, it):
        th = self.th; acc = th["accent"]; circ = th["circle"]
        img = self.background(gt, slug(it["ad"]), t, dur).convert("RGBA")
        ov = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(ov)
        self.progress(d, gt)
        rank = it["sira"]
        a = ease_out(prog(t, 0, 0.35)); xoff = (1 - a) * 700
        s = f"#{rank}"; fr = BLACK(300); w = d.textlength(s, font=fr)
        d.text(((W - w) / 2 + xoff, 200), s, font=fr, fill=(acc if rank <= 3 else WHITE) + (int(255 * a),))
        an = ease_back(prog(t, 0.12, 0.5))
        name = it["ad"].upper()
        self.text_c(d, 560 + 40 * (1 - an), name, self.fit(d, name, BLACK, 104, W - 120), WHITE, 255 * clamp(an))
        if it.get("yer"):
            self.text_c(d, 690, it["yer"], self.fit(d, it["yer"], SEMI, 46, W - 160), th["soft"], 255 * ease_out(prog(t, 0.25, 0.6)))
        v = float(it["deger"]); ac = ease_out(prog(t, 0.3, 1.2))
        is_top = abs(v - self.maxv) < 1e-9
        label = f"{self.top_name} ölçeği"
        lab = SEMI(32)
        if self.T.get("gorsel", "daire") == "cubuk":
            bx0, bx1, by1, bh = W / 2 - 110, W / 2 + 110, 1340, 520
            if not is_top:
                d.rounded_rectangle([bx0, by1 - bh, bx1, by1], 18, outline=(255, 255, 255, int(90 * ac)), width=4)
                lw = d.textlength(label, font=lab); d.text((W / 2 - lw / 2, by1 - bh - 50), label, font=lab, fill=(255, 255, 255, int(130 * ac)))
            h = bh * (v / self.maxv) * ac
            if h > 2:
                d.rounded_rectangle([bx0, by1 - h, bx1, by1], 18, fill=circ + (210,), outline=tuple(min(255, x + 110) for x in circ) + (255,), width=5)
        else:
            cx, cy, R = W / 2, 1110, 250
            if not is_top:
                d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(255, 255, 255, int(90 * ac)), width=4)
                lw = d.textlength(label, font=lab); d.text((cx - lw / 2, cy - R - 50), label, font=lab, fill=(255, 255, 255, int(130 * ac)))
            frac = v / self.maxv
            r = R * (frac if self.T.get("olcek") == "dogrusal" else math.sqrt(frac)) * ac
            if r > 1:
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=circ + (200,))
                d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=tuple(min(255, x + 110) for x in circ) + (255,), width=5)
        cur = v * ease_out(prog(t, 0.3, 1.3))
        sval = fmt_num(cur, v) + (" " + self.T["birim"] if self.T.get("birim") else "")
        self.text_c(d, 1400, sval, self.fit(d, sval, BLACK, 110, W - 120), acc, 255 * ease_out(prog(t, 0.3, 0.5)), stroke=4)
        fact = it.get("bilgi") or []
        if fact:
            af = ease_out(prog(t, 1.75, 2.15)); dy = 30 * (1 - af)
            d.rounded_rectangle([70, 1570 + dy, W - 70, 1780 + dy], 40, fill=(0, 0, 0, int(140 * af)))
            self.text_c(d, 1600 + dy, fact[0], self.fit(d, fact[0], SEMI, 52, W - 200), WHITE, 255 * af)
            if len(fact) > 1:
                self.text_c(d, 1680 + dy, fact[1], self.fit(d, fact[1], BOLD, 52, W - 200), WHITE, 255 * af)
        img.alpha_composite(ov)
        return img.convert("RGB")

    def frame_outro(self, t, gt, dur):
        th = self.th; acc = th["accent"]
        img = self.background(gt).convert("RGBA")
        ov = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(ov)
        self.progress(d, gt)
        a = ease_back(prog(t, 0, 0.5))
        ust = self.T.get("kapanis_ust", "Sen hangisini"); vurgu = self.T.get("kapanis_vurgu", "biliyordun?")
        self.text_c(d, 600 + 50 * (1 - a), ust, self.fit(d, ust, BLACK, 110, W - 120), WHITE, 255 * clamp(a))
        self.text_c(d, 730 + 50 * (1 - a), vurgu, self.fit(d, vurgu, BLACK, 110, W - 120), acc, 255 * clamp(a))
        a2 = ease_out(prog(t, 0.5, 0.9))
        self.text_c(d, 960, "Yorumlara yaz", BOLD(70), WHITE, 255 * a2)
        by = 1080 + 25 * abs(math.sin(t * 5)) * a2
        d.polygon([(W / 2 - 60, by), (W / 2 + 60, by), (W / 2, by + 80)], fill=acc + (int(255 * a2),))
        a3 = ease_out(prog(t, 1.1, 1.5))
        d.rounded_rectangle([170, 1330, W - 170, 1470], 70, fill=acc + (int(255 * a3),))
        self.text_c(d, 1362, "TAKİP ET", BLACK(70), th["ink"], 255 * a3)
        self.text_c(d, 1520, "Her gün yeni bir bilgi için", SEMI(44), th["soft"], 255 * a3)
        img.alpha_composite(ov)
        return img.convert("RGB")


def scene_list(topic, vo_durs):
    def dur(k, base): return max(base, round((VO_LEAD + vo_durs.get(k, 0) + 0.45) * FPS) / FPS)
    sc = [("hook", dur("hook", 3.0), None)]
    for i, it in enumerate(topic["maddeler"]):
        sc.append((f"m{i:02d}", dur(f"m{i:02d}", 3.4), it))
    sc.append(("outro", dur("outro", 3.2), None))
    return sc


def voice_lines(topic):
    L = {"hook": topic["kanca_seslendirme"]}
    for i, it in enumerate(topic["maddeler"]):
        L[f"m{i:02d}"] = it["seslendirme"]
    L["outro"] = topic.get("kapanis_seslendirme", "Sen hangisini biliyordun? Yorumlara yaz, ve takip etmeyi unutma!")
    return L


def make_music(dur, starts, sr=44100):
    N = int(sr * dur); t = np.arange(N) / sr; out = np.zeros(N)
    beat = 0.5; bar = beat * 4
    chords = [[220, 261.6, 329.6], [174.6, 220, 261.6], [196, 261.6, 329.6], [196, 246.9, 293.7]]
    env = lambda x, d_: np.exp(-x / d_)
    for bi in range(int(dur / bar) + 1):
        c = chords[bi % 4]; s0 = int(bi * bar * sr); s1 = min(N, int((bi + 1) * bar * sr))
        if s0 >= N: break
        tt = t[s0:s1] - bi * bar
        fade = np.minimum(1, tt / 0.3) * np.minimum(1, (bar - tt) / 0.3)
        for f in c: out[s0:s1] += 0.05 * fade * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt))
        for b in range(4):
            bs = int((bi * bar + b * beat) * sr)
            if bs >= N: break
            be = min(N, bs + int(0.4 * sr)); x = t[bs:be] - t[bs]
            out[bs:be] += 0.18 * env(x, 0.15) * np.sin(np.pi * c[0] * x)
    rng = np.random.default_rng(1)
    for k in range(int(dur / beat) + 1):
        s = int(k * beat * sr)
        if s >= N: break
        e = min(N, s + int(0.3 * sr)); x = t[s:e] - t[s]
        out[s:e] += 0.55 * env(x, 0.08) * np.sin(2 * np.pi * (50 + 90 * env(x, 0.03)) * x)
        h = int((k * beat + beat / 2) * sr); he = min(N, h + int(0.05 * sr))
        if h < N: out[h:he] += 0.06 * rng.standard_normal(he - h) * env(t[h:he] - t[h], 0.015)
    for st in starts[1:]:
        s = max(0, int((st - 0.15) * sr)); e = min(N, s + int(0.45 * sr)); x = t[s:e] - t[s]
        nz = np.convolve(rng.standard_normal(e - s), np.ones(8) / 8, mode="same")
        out[s:e] += 0.35 * nz * np.sin(np.pi * x / 0.45) ** 2
    out *= np.minimum(1, (dur - t) / 1.0)
    return np.tanh(out * 1.2) * 0.8


def render(topic_path, outdir, theme=None, img_dir=None, preview=False, piper_model=None):
    topic = json.load(open(topic_path, encoding="utf-8"))
    os.makedirs(outdir, exist_ok=True)
    theme = theme or os.environ.get("THEME") or pick_theme(topic["id"])
    R = Renderer(topic, theme, img_dir or os.environ.get("IMG_DIR"))
    vodir = os.path.join(outdir, "vo")
    lines = voice_lines(topic)
    if preview:
        vo = {k: 4.0 for k in lines}
    else:
        vo = synthesize_all(lines, vodir, piper_model or os.environ["PIPER_MODEL"])
    scenes = scene_list(topic, vo)
    starts = np.cumsum([0] + [s[1] for s in scenes])
    R.total = float(starts[-1])

    def frame(kind, t, gt, dur, it):
        if kind == "hook": return R.frame_hook(t, gt, dur)
        if kind == "outro": return R.frame_outro(t, gt, dur)
        return R.frame_item(t, gt, dur, it)

    if preview:
        for (k, d_, it), st in zip(scenes, starts):
            frame(k, d_ - 0.5, st + d_ - 0.5, d_, it).save(os.path.join(outdir, f"prev_{k}.jpg"), quality=85)
        return theme

    files = []
    for (k, d_, it), st in zip(scenes, starts):
        tmp = os.path.join(outdir, f"tmp_{k}.mp4"); fin = os.path.join(outdir, f"scene_{k}.mp4")
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                              "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                              "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
        for n in range(int(round(d_ * FPS))):
            t = n / FPS
            p.stdin.write(frame(k, t, st + t, d_, it).tobytes())
        p.stdin.close()
        if p.wait() != 0: raise RuntimeError(f"ffmpeg failed for scene {k}")
        os.replace(tmp, fin); files.append(fin)
    lst = os.path.join(outdir, "list.txt")
    with open(lst, "w") as f:
        for p_ in files: f.write(f"file '{os.path.abspath(p_)}'\n")
    silent = os.path.join(outdir, "silent.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)

    sr = 44100; N = int(R.total * sr)
    voice = np.zeros(N)
    for (k, d_, it), st in zip(scenes, starts):
        w = wave.open(os.path.join(vodir, f"{k}.wav"))
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768
        i0 = int((st + VO_LEAD) * sr); voice[i0:i0 + len(a)] += a[:max(0, N - i0)]
    music = make_music(R.total, starts)[:N]
    envv = np.convolve((np.abs(voice) > 0.02).astype(float), np.ones(int(0.25 * sr)) / int(0.25 * sr), mode="same")
    mix = np.tanh((music * (0.55 - 0.35 * np.clip(envv * 3, 0, 1)) + voice * 0.95) * 1.1) * 0.9
    pcm = (mix * 32767).astype(np.int16)
    mixp = os.path.join(outdir, "mix.wav")
    with wave.open(mixp, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(np.stack([pcm, pcm], 1).tobytes())
    final = os.path.join(outdir, "video.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", mixp, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final], check=True)
    for p_ in files + [silent, mixp, lst]: os.remove(p_)
    return theme


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("topic"); ap.add_argument("outdir")
    ap.add_argument("--theme"); ap.add_argument("--images"); ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    print("theme:", render(a.topic, a.outdir, a.theme, a.images, a.preview))
