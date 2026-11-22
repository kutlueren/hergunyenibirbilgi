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

    # ---------- illustrated visuals ----------
    @staticmethod
    def _ridge(x0, y0, x1, y1, n, amp, rng):
        """Jagged line from (x0,y0) to (x1,y1): a mountain slope."""
        pts = []
        for k in range(n + 1):
            f = k / n
            jit = 0 if k in (0, n) else rng.uniform(-amp, amp) * math.sin(math.pi * f)
            pts.append((x0 + (x1 - x0) * f + rng.uniform(-amp, amp) * 0.4 * (0 < k < n), y0 + (y1 - y0) * f + jit))
        return pts

    def _axis(self):
        """Value axis for illustrated charts. When all values are close (e.g. every mountain > 8.000 m),
        start the axis near the smallest value so the differences are visible; the labels stay honest."""
        vals = [float(m["deger"]) for m in self.items]
        vmin, vmax = min(vals), max(vals)
        floor = 0.0
        if vmin / vmax > 0.6:
            for st in (100, 250, 500, 1000, 2000, 5000, 10000):
                if (vmax - vmin) / st <= 4:
                    floor = max(0.0, math.floor((vmin - (vmax - vmin) * 0.25) / st) * st); break
        span = vmax - floor
        step = next(st for st in (100, 250, 500, 1000, 2000, 5000, 10000, 20000) if span / st <= 5)
        return floor, vmax, step

    def draw_mountain(self, d, it, v, ac, t, gt, is_top):
        th = self.th; acc = th["accent"]; c = th["circle"]
        ground, Hmax, cx = 1350, 480, W / 2
        floor, vmax, step = self._axis()
        unit = self.T.get("birim", "")
        frac = (v - floor) / (vmax - floor)
        # value scale on the left
        lab = SEMI(28)
        k0 = math.ceil(floor / step)
        for k in range(k0, int(vmax // step) + 1):
            val = k * step
            y = ground - Hmax * (val - floor) / (vmax - floor)
            d.line([(60, y), (90, y)], fill=(255, 255, 255, int(110 * ac)), width=3)
            d.text((98, y - 16), f"{fmt_num(val, val)} {unit}".strip(), font=lab, fill=(255, 255, 255, int(130 * ac)))
        # reference outline: the tallest one
        if not is_top:
            rr = np.random.default_rng(7)
            hw = 300
            left = self._ridge(cx - hw, ground, cx, ground - Hmax, 9, 16, rr)
            right = self._ridge(cx, ground - Hmax, cx + hw, ground, 9, 16, rr)
            d.line(left + right[1:], fill=(255, 255, 255, int(90 * ac)), width=4, joint="curve")
            lw = d.textlength("#1 ?", font=lab)
            d.text((cx - 40 - lw, ground - Hmax - 14), "#1 ?", font=lab, fill=(255, 255, 255, int(140 * ac)))
        # the mountain, growing from the ground
        h = max(40.0, Hmax * frac) * ac
        if h < 4:
            return
        hw = 220 + 80 * frac
        rng = np.random.default_rng(sum(map(ord, it["ad"])))
        peak = (cx + rng.uniform(-25, 25), ground - h)
        left = self._ridge(cx - hw, ground, peak[0], peak[1], 10, 0.06 * h + 5, rng)
        right = self._ridge(peak[0], peak[1], cx + hw, ground, 10, 0.06 * h + 5, rng)
        dark = tuple(int(x * 0.45) for x in c); mid = tuple(int(x * 0.7) for x in c)
        d.polygon(left + right[1:], fill=mid + (255,))
        d.polygon([peak] + right[1:] + [(peak[0] + hw * 0.25, ground)], fill=dark + (255,))
        # snow cap on the top ~30 %
        snow_y = peak[1] + 0.30 * h
        def slope_x(pts, y):
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
                    return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
            return pts[-1][0]
        lx, rx = slope_x(left, snow_y), slope_x(right, snow_y)
        cap = [p for p in left if p[1] <= snow_y] + [p for p in right[1:] if p[1] <= snow_y]
        zig = [(rx + (lx - rx) * k / 7, snow_y + (14 if k % 2 else -6) + rng.uniform(-4, 4)) for k in range(8)]
        if len(cap) >= 2:
            d.polygon([(lx, snow_y)] + cap + [(rx, snow_y)] + zig, fill=(245, 250, 255, 255))
            rcap = [p for p in right if p[1] <= snow_y]
            if rcap:
                d.polygon([peak] + rcap + [(rx, snow_y), (peak[0] + (rx - peak[0]) * 0.35, snow_y + 8)], fill=(200, 215, 235, 255))
        # summit flag once fully grown
        af = ease_out(prog(t, 1.15, 1.45))
        if af > 0:
            fx, fy = peak
            d.line([(fx, fy), (fx, fy - 64 * af)], fill=(255, 255, 255, 255), width=4)
            wave = 6 * math.sin(gt * 6)
            d.polygon([(fx, fy - 64 * af), (fx + 46 * af, fy - 53 * af + wave), (fx, fy - 42 * af)], fill=acc + (255,))
        # two small clouds drifting across the mountain only
        for k in range(2):
            cy_ = ground - h * (0.42 + 0.22 * k)
            rngx = hw * 1.2
            cx_ = cx - rngx / 2 + ((gt * (24 + 12 * k) + k * 170) % rngx) - 60
            sc = min(1.0, 0.45 + h / 500)
            for dx, dy, r in ((0, 0, 30), (32, -10, 36), (70, 0, 28), (36, 9, 27)):
                dx, dy, r = dx * sc, dy * sc, r * sc
                d.ellipse([cx_ + dx - r, cy_ + dy - r * 0.6, cx_ + dx + r, cy_ + dy + r * 0.6], fill=(255, 255, 255, int(150 * ac)))

    def _tower_shape(self, cx, ground, h, bw, rng, tiers):
        """Stepped skyscraper outline: list of (x0, x1, y_top) blocks from bottom to top + spire height."""
        spire = h * rng.uniform(0.08, 0.14)
        body = h - spire
        blocks, y, w = [], ground, bw
        heights = rng.dirichlet(np.ones(tiers) * 3) * body
        for i, th in enumerate(sorted(heights, reverse=True)):
            blocks.append((cx - w / 2, cx + w / 2, y - th))
            y -= th
            w *= rng.uniform(0.62, 0.8)
        return blocks, spire

    @staticmethod
    def _stepped_outline(blocks, ground):
        """Outline (left side up, across the top, right side down) of stacked blocks."""
        pts = [(blocks[0][0], ground)]
        for x0, x1, yt in blocks:
            pts += [(x0, pts[-1][1]), (x0, yt)]
        for i in range(len(blocks) - 1, -1, -1):
            x0, x1, yt = blocks[i]
            below = blocks[i - 1][2] if i > 0 else ground
            pts += [(x1, yt), (x1, below)]
        return pts

    def draw_building(self, d, it, v, ac, t, gt, is_top):
        th = self.th; acc = th["accent"]; c = th["circle"]
        ground, Hmax, cx = 1350, 540, W / 2
        floor, vmax, step = self._axis()
        unit = self.T.get("birim", "")
        lab = SEMI(28)
        for k in range(math.ceil(floor / step), int(vmax // step) + 1):
            val = k * step
            y = ground - Hmax * (val - floor) / (vmax - floor)
            d.line([(60, y), (90, y)], fill=(255, 255, 255, int(110 * ac)), width=3)
            d.text((98, y - 16), f"{fmt_num(val, val)} {unit}".strip(), font=lab, fill=(255, 255, 255, int(130 * ac)))
        d.line([(150, ground), (W - 150, ground)], fill=(255, 255, 255, int(120 * ac)), width=3)
        # small city skyline at the foot, for scale and atmosphere
        rs = np.random.default_rng(11)
        x = 150
        while x < W - 150:
            bw_ = rs.uniform(30, 70); bh_ = rs.uniform(25, 90)
            if abs(x + bw_ / 2 - cx) > 120:
                d.rectangle([x, ground - bh_ * ac, x + bw_ - 6, ground], fill=tuple(int(q * 0.35) for q in c) + (220,))
            x += bw_
        # reference outline: the tallest one
        if not is_top:
            rr = np.random.default_rng(5)
            blocks, spire = self._tower_shape(cx, ground, Hmax, 190, rr, 4)
            d.line(self._stepped_outline(blocks, ground) , fill=(255, 255, 255, int(90 * ac)), width=3)
            top_y = blocks[-1][2]
            d.line([(cx, top_y), (cx, top_y - spire)], fill=(255, 255, 255, int(90 * ac)), width=3)
            lw = d.textlength("#1 ?", font=lab)
            d.text((cx - 95 - lw, ground - Hmax - 10), "#1 ?", font=lab, fill=(255, 255, 255, int(140 * ac)))
        # the building, rising from the ground
        frac = (v - floor) / (vmax - floor)
        h = max(60.0, Hmax * frac) * ac
        rng = np.random.default_rng(sum(map(ord, it["ad"])))
        tiers = int(rng.integers(2, 5)) if not is_top else 6
        blocks, spire = self._tower_shape(cx, ground, h, 170 + 40 * frac, rng, tiers)
        body = tuple(int(q * 0.62) for q in c); side = tuple(int(q * 0.38) for q in c); edge = tuple(min(255, q + 110) for q in c)
        prev_top = ground
        for i, (x0, x1, yt) in enumerate(blocks):
            yb = prev_top
            d.rectangle([x0, yt, x1, yb], fill=body + (255,))
            d.polygon([(x1, yt), (x1 + 18, yt - 10), (x1 + 18, yb - 10), (x1, yb)], fill=side + (255,))  # 3D side face
            d.line([(x0, yt), (x1, yt)], fill=edge + (255,), width=3)
            # windows
            cols = int((x1 - x0 - 16) // 22); rows = int((yb - yt - 10) // 26)
            if cols < 1 or rows < 1:
                prev_top = yt; continue
            ww = (x1 - x0 - 16) / cols
            for r_ in range(rows):
                for c_ in range(cols):
                    seed = (i * 131 + r_ * 17 + c_ * 7) % 23
                    lit = (seed + int(gt * 1.5 + seed)) % 5 != 0 and seed % 3 != 0
                    wx = x0 + 8 + c_ * ww; wy = yb - 14 - r_ * 26
                    col = (255, 236, 170, 230) if lit else tuple(int(q * 0.6) for q in c) + (200,)
                    d.rectangle([wx + 3, wy - 13, wx + ww - 4, wy], fill=col)
            prev_top = yt
        top = blocks[-1][2]
        d.line([(cx, top), (cx, top - spire)], fill=edge + (255,), width=5)
        if ease_out(prog(t, 1.15, 1.3)) > 0 and int(gt * 2) % 2 == 0:  # blinking aircraft warning light
            d.ellipse([cx - 9, top - spire - 9, cx + 9, top - spire + 9], fill=(255, 70, 60, 255))
            d.ellipse([cx - 22, top - spire - 22, cx + 22, top - spire + 22], fill=(255, 70, 60, 60))

    # --- organic shapes: land, water, desert, ice -------------------------------------
    STYLES = {
        "kara": dict(fill=(70, 150, 90), inner=(110, 180, 110), edge=(235, 215, 160)),
        "su":   dict(fill=(40, 130, 205), inner=(70, 165, 230), edge=(170, 220, 255)),
        "col":  dict(fill=(225, 175, 95), inner=(240, 200, 125), edge=(170, 120, 55)),
        "buz":  dict(fill=(232, 243, 255), inner=(205, 228, 250), edge=(160, 205, 240)),
    }

    @staticmethod
    def _blob(cx, cy, r, seed, n=72):
        rng = np.random.default_rng(seed)
        amps = rng.uniform(0.03, 0.11, 6) / np.arange(1, 7) ** 0.4
        phs = rng.uniform(0, 2 * math.pi, 6)
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n
            k = 1 + sum(amps[j] * math.sin((j + 2) * a + phs[j]) for j in range(6))
            pts.append((cx + r * k * math.cos(a), cy + r * k * 0.92 * math.sin(a)))
        return pts

    def draw_shape(self, d, it, v, ac, t, gt, is_top):
        cx, cy, R = W / 2, 1090, 255
        lab = SEMI(32)
        top = max(self.items, key=lambda m: float(m["deger"]))
        if not is_top:
            ref = self._blob(cx, cy, R, sum(map(ord, top["ad"])))
            d.line(ref + [ref[0]], fill=(255, 255, 255, int(85 * ac)), width=4, joint="curve")
            lw = d.textlength("#1 ölçeği", font=lab)
            d.text((cx - lw / 2, cy - R - 58), "#1 ölçeği", font=lab, fill=(255, 255, 255, int(130 * ac)))
        frac = v / self.maxv
        r = R * (frac if self.T.get("olcek") == "dogrusal" else math.sqrt(frac)) * ac
        if r < 3:
            return
        st = self.STYLES.get(it.get("stil") or self.T.get("stil", "kara"), self.STYLES["kara"])
        seed = sum(map(ord, it["ad"]))
        pts = self._blob(cx, cy, r, seed)
        d.polygon(pts, fill=st["fill"] + (255,))
        inner = self._blob(cx - r * 0.12, cy - r * 0.1, r * 0.55, seed + 1)
        d.polygon(inner, fill=st["inner"] + (255,))
        d.line(pts + [pts[0]], fill=st["edge"] + (255,), width=max(2, int(r / 40) + 2), joint="curve")
        stil = it.get("stil") or self.T.get("stil", "kara")
        rng = np.random.default_rng(seed + 2)
        if stil == "su":      # moving ripples
            for k in range(4):
                yy = cy - r * 0.5 + k * r * 0.3; xx = cx - r * 0.45 + (gt * 25 + k * 40) % (r * 0.6)
                d.arc([xx - r * 0.18, yy - r * 0.06, xx + r * 0.18, yy + r * 0.06], 200, 340, fill=(255, 255, 255, 150), width=max(2, int(r / 60)))
        elif stil == "col":   # dune lines
            for k in range(4):
                yy = cy - r * 0.45 + k * r * 0.28
                d.arc([cx - r * 0.55, yy, cx + r * 0.35, yy + r * 0.25], 200, 330, fill=st["edge"] + (180,), width=max(2, int(r / 55)))
        elif stil == "buz":   # cracks
            for k in range(5):
                a = rng.uniform(0, 2 * math.pi); l = r * rng.uniform(0.3, 0.7)
                d.line([(cx, cy), (cx + l * math.cos(a), cy + l * math.sin(a) * 0.9)], fill=st["edge"] + (200,), width=max(2, int(r / 70)))
        else:                 # land: a few hills/forest dots
            for k in range(6):
                a = rng.uniform(0, 2 * math.pi); l = r * rng.uniform(0.1, 0.6)
                x, y = cx + l * math.cos(a), cy + l * math.sin(a) * 0.8; rr_ = max(3, r * 0.05)
                d.ellipse([x - rr_, y - rr_, x + rr_, y + rr_], fill=(45, 110, 65, 230))

    # --- icon charts: people, planes, speech bubbles ------------------------------------
    @staticmethod
    def _icon(d, kind, x, y, s, col):
        """Draws one icon in the box (x, y, s×s)."""
        if kind == "ucak":
            cxi, cyi = x + s / 2, y + s / 2
            d.polygon([(x + s * 0.08, cyi - s * 0.05), (x + s * 0.85, cyi - s * 0.06), (x + s * 0.98, cyi),
                       (x + s * 0.85, cyi + s * 0.06), (x + s * 0.08, cyi + s * 0.05)], fill=col)          # body
            d.polygon([(cxi - s * 0.05, cyi), (cxi + s * 0.12, cyi), (cxi - s * 0.12, cyi - s * 0.42), (cxi - s * 0.22, cyi - s * 0.42)], fill=col)
            d.polygon([(cxi - s * 0.05, cyi), (cxi + s * 0.12, cyi), (cxi - s * 0.12, cyi + s * 0.42), (cxi - s * 0.22, cyi + s * 0.42)], fill=col)
            d.polygon([(x + s * 0.1, cyi), (x + s * 0.22, cyi), (x + s * 0.12, cyi - s * 0.25), (x + s * 0.05, cyi - s * 0.25)], fill=col)
        elif kind == "balon":
            d.rounded_rectangle([x + s * 0.06, y + s * 0.12, x + s * 0.94, y + s * 0.7], s * 0.18, fill=col)
            d.polygon([(x + s * 0.25, y + s * 0.66), (x + s * 0.2, y + s * 0.92), (x + s * 0.48, y + s * 0.66)], fill=col)
            for k in range(3):
                dx = x + s * (0.3 + 0.2 * k); d.ellipse([dx - s * 0.05, y + s * 0.36, dx + s * 0.05, y + s * 0.46], fill=(255, 255, 255, 200))
        else:  # insan: head + shoulders
            hr = s * 0.19
            d.ellipse([x + s / 2 - hr, y + s * 0.04, x + s / 2 + hr, y + s * 0.04 + 2 * hr], fill=col)
            d.pieslice([x + s * 0.12, y + s * 0.5, x + s * 0.88, y + s * 1.26], 180, 360, fill=col)

    def draw_icons(self, d, it, v, ac, t, gt, is_top):
        kind = self.T.get("ikon", "insan"); unit = float(self.T.get("ikon_deger", 1))
        maxn = math.ceil(self.maxv / unit - 1e-9)
        x0, y0, bw, bh = 120, 830, W - 240, 500
        cols = max(1, math.ceil(math.sqrt(maxn * bw / bh))); rows = math.ceil(maxn / cols)
        while rows * (bw / cols) > bh and cols < maxn:
            cols += 1; rows = math.ceil(maxn / cols)
        cell = min(bw / cols, bh / rows); s_ = cell * 0.86
        gx = x0 + (bw - cols * cell) / 2; gy = y0 + (bh - rows * cell) / 2
        lab = SEMI(32)
        legend = f"1 simge = {self.T.get('ikon_etiket', fmt_num(unit, unit))}"
        lw = d.textlength(legend, font=lab)
        d.text((W / 2 - lw / 2, y0 - 58), legend, font=lab, fill=(255, 255, 255, int(150 * ac)))
        c = self.th["circle"]; on = tuple(min(255, q + 40) for q in c) + (255,); off = (255, 255, 255, 38)
        shown = (v / unit) * ac
        img = d._image
        for i in range(maxn):
            r_, c_ = divmod(i, cols)
            x = gx + c_ * cell + (cell - s_) / 2; y = gy + r_ * cell + (cell - s_) / 2
            self._icon(d, kind, x, y, s_, off)
            if i + 1 <= shown:
                self._icon(d, kind, x, y, s_, on)
            elif i < shown:  # partly filled icon, cut from the left
                tile = Image.new("RGBA", (int(s_) + 2, int(s_) + 2), (0, 0, 0, 0))
                self._icon(ImageDraw.Draw(tile), kind, 0, 0, s_, on)
                wcut = max(1, int((shown - i) * s_))
                img.alpha_composite(tile.crop((0, 0, wcut, tile.height)), (int(x), int(y)))

    # --- planets ---------------------------------------------------------------------
    def _sphere(self, r, look, gt):
        """Shaded planet as an RGBA tile of size 2r (+ room for rings)."""
        pad = int(r * 0.9) if look.get("halka") else 4
        size = int(2 * r) + 2 * pad
        tile = Image.new("RGBA", (size, size), (0, 0, 0, 0)); td = ImageDraw.Draw(tile)
        c0 = tuple(look.get("renk", [180, 180, 180])); cxp = cyp = size / 2
        body = Image.new("RGBA", (size, size), (0, 0, 0, 0)); bd = ImageDraw.Draw(body)
        bd.ellipse([cxp - r, cyp - r, cxp + r, cyp + r], fill=c0 + (255,))
        doku = look.get("doku", "duz"); rng = np.random.default_rng(int(sum(c0)))
        if doku == "bant":
            for k in range(-6, 7):
                y = cyp + k * r / 6.5; hh = r / 13
                shade = 1.12 if k % 2 else 0.86
                col = tuple(min(255, int(q * shade)) for q in c0)
                bd.rectangle([cxp - r, y - hh, cxp + r, y + hh], fill=col + (255,))
            if look.get("leke"):
                sx = cxp + r * 0.35 * math.sin(gt * 0.4)
                bd.ellipse([sx - r * 0.2, cyp + r * 0.25, sx + r * 0.2, cyp + r * 0.4], fill=(190, 85, 60, 255))
        elif doku == "krater":
            for k in range(14):
                a = rng.uniform(0, 2 * math.pi); l = r * math.sqrt(rng.uniform(0, 0.8)); cr = r * rng.uniform(0.05, 0.14)
                x = cxp + l * math.cos(a); y = cyp + l * math.sin(a)
                bd.ellipse([x - cr, y - cr, x + cr, y + cr], fill=tuple(int(q * 0.78) for q in c0) + (255,))
        elif doku == "bulut":
            for k in range(7):
                y = cyp - r + (k + 0.5) * 2 * r / 7; off_ = r * 0.2 * math.sin(k + gt * 0.3)
                bd.ellipse([cxp - r * 0.9 + off_, y - r * 0.08, cxp + r * 0.9 + off_, y + r * 0.08], fill=tuple(min(255, int(q * 1.1)) for q in c0) + (255,))
        elif doku == "dunya":
            for k in range(5):
                a = rng.uniform(0, 2 * math.pi); l = r * rng.uniform(0.1, 0.7)
                x = cxp + ((l * math.cos(a) + gt * r * 0.08) % (2 * r)) - r; y = cyp + l * math.sin(a) * 0.8
                pts = self._blob(x, y, r * rng.uniform(0.18, 0.32), k + 3, n=24)
                bd.polygon(pts, fill=(70, 160, 80, 255))
            bd.ellipse([cxp - r * 0.42, cyp - r * 1.04, cxp + r * 0.42, cyp - r * 0.8], fill=(240, 248, 255, 255))
        mask = Image.new("L", (size, size), 0); ImageDraw.Draw(mask).ellipse([cxp - r, cyp - r, cxp + r, cyp + r], fill=255)
        # light from the top-left: darken towards the bottom-right edge
        yy, xx = np.mgrid[0:size, 0:size]
        dist = np.sqrt(((xx - (cxp - r * 0.35)) / r) ** 2 + ((yy - (cyp - r * 0.35)) / r) ** 2)
        shade = np.clip(1.15 - 0.55 * dist, 0.25, 1.15)
        arr = np.asarray(body).astype(np.float32)
        arr[..., :3] = np.clip(arr[..., :3] * shade[..., None], 0, 255)
        body = Image.fromarray(arr.astype(np.uint8), "RGBA"); body.putalpha(mask)
        ring = look.get("halka")
        if ring:
            rw, rh = (r * 1.9, r * 0.45) if ring == "genis" else (r * 1.45, r * 0.6)
            col = (230, 210, 160, 230) if ring == "genis" else (200, 235, 240, 150)
            width = max(2, int(r * (0.12 if ring == "genis" else 0.03)))
            td.ellipse([cxp - rw, cyp - rh, cxp + rw, cyp + rh], outline=col, width=width)   # back half
            tile.alpha_composite(body)
            front = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            ImageDraw.Draw(front).arc([cxp - rw, cyp - rh, cxp + rw, cyp + rh], 0, 180, fill=col, width=width)
            tile.alpha_composite(front)
        else:
            tile.alpha_composite(body)
        return tile

    def draw_planet(self, d, it, v, ac, t, gt, is_top):
        img = d._image
        earth_d = 12742.0
        big = 215
        look = {k: it[k] for k in ("renk", "doku", "halka", "leke") if k in it}
        is_earth = it["ad"] == "Dünya"
        if is_earth:
            rp, re = big, 0
        elif v >= earth_d:
            rp, re = big, big * earth_d / v
        else:
            re, rp = big, big * v / earth_d
        rp *= ease_back(min(1, ac * 1.02)) if ac < 1 else 1
        if rp < 2:
            return
        cy = 1085
        ring_extra = {"genis": 0.9, "ince": 0.45}.get(look.get("halka"), 0) * rp   # ring sticks out on both sides
        gap = 60 if not is_earth else 0
        group = 2 * rp + 2 * ring_extra + (gap + 2 * re if not is_earth else 0)
        px = W / 2 - group / 2 + ring_extra + rp
        tile = self._sphere(max(2, rp), look, gt)
        img.alpha_composite(tile, (int(px - tile.width / 2), int(cy - tile.height / 2)))
        if not is_earth and re > 0:
            ex = W / 2 - group / 2 + 2 * ring_extra + 2 * rp + gap + re
            er = max(2, re * ac)
            et = self._sphere(er, {"renk": [50, 110, 200], "doku": "dunya"}, gt)
            img.alpha_composite(et, (int(ex - et.width / 2), int(cy - et.height / 2)))
            lab = SEMI(32); lw = d.textlength("Dünya", font=lab)
            d.text((ex - lw / 2, cy + max(er, 12) + 14), "Dünya", font=lab, fill=(255, 255, 255, int(170 * ac)))

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
        label = "#1 ölçeği"  # never the name: it would give away the answer
        lab = SEMI(32)
        if self.T.get("gorsel") == "dag":
            self.draw_mountain(d, it, v, ac, t, gt, is_top)
        elif self.T.get("gorsel") == "bina":
            self.draw_building(d, it, v, ac, t, gt, is_top)
        elif self.T.get("gorsel") == "sekil":
            self.draw_shape(d, it, v, ac, t, gt, is_top)
        elif self.T.get("gorsel") == "ikon":
            self.draw_icons(d, it, v, ac, t, gt, is_top)
        elif self.T.get("gorsel") == "gezegen":
            self.draw_planet(d, it, v, ac, t, gt, is_top)
        elif self.T.get("gorsel", "daire") == "cubuk":
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
