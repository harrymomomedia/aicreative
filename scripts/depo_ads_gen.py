"""
Depo-Provera / brain-meningioma image-ad batch — 20 formats, deliberately VARIED.

Angle (LOCKED): LEAD WITH THE DIAGNOSIS (meningioma / brain tumor) — the high-value, claim-ready
lead — then connect Depo-Provera as the link. Compliance phrase: "may qualify for significant
compensation". Generic lead-gen brand. Full taxonomy + copy: inventory/depo_provera_ad_formats.md

Variety is the point: every card uses a different palette / layout / imagery, distinct personas
(no repeated faces), and genuinely different chrome (FB post, Reddit, texts, letter, news,
advertorial). gpt-image-2 (KIE, 2K) renders BASE IMAGERY only; PIL lays ALL precise legal text.

Run:
  .venv/bin/python scripts/depo_ads_gen.py                       # all 20, 4:5
  .venv/bin/python scripts/depo_ads_gen.py --only quiz,stat      # subset
  .venv/bin/python scripts/depo_ads_gen.py --regen-base stat     # force a base regen
Skip-if-exists on base images AND composites.
"""
import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import kie_client as kie

OUT = "outputs/depo_ads"
BASE_DIR = os.path.join(OUT, "base")
FINAL_DIR = os.path.join(OUT, "final")
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)
W, H = 1080, 1350  # 4:5 feed

BRAND = "Depo-Provera Claims"
PHRASE = "You may qualify for significant compensation."
ATTY = "Attorney Advertising."
DRAMA = "Attorney Advertising.  Dramatization — not an actual client."

# palette
YELLOW = (250, 204, 21); WHITE = (248, 248, 248); INK = (22, 22, 24)
TEAL = (12, 58, 60); NAVY = (17, 27, 52); CRIMSON = (24, 22, 28); AMBER_BG = (40, 30, 14)
AMBER = (245, 176, 38); PLUM = (44, 20, 50); GOLD = (236, 196, 120); BLUE = (18, 44, 84)
GREEN = (32, 170, 92); REDX = (200, 46, 46); PAPER = (250, 248, 244); CREAM = (244, 239, 230)
RED = (178, 24, 24); GREY = (110, 110, 112); STEEL = (28, 40, 56)

FONT_DIRS = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts"),
    "/System/Library/Fonts/Supplemental/", "/System/Library/Fonts/", "/Library/Fonts/",
]


def font(names, size):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def F_black(s): return font(["Montserrat-Black.ttf", "Arial Black.ttf"], s)
def F_bold(s): return font(["Arial Bold.ttf", "HelveticaNeue.ttc"], s)
def F_reg(s): return font(["Arial.ttf", "Helvetica.ttc"], s)
def F_serif_b(s): return font(["Georgia Bold.ttf", "Times New Roman Bold.ttf"], s)
def F_serif(s): return font(["Georgia.ttf", "Times New Roman.ttf"], s)
def F_serif_i(s): return font(["Georgia Italic.ttf", "Times New Roman Italic.ttf", "Georgia.ttf"], s)
def F_quote(s): return font(["Georgia Bold Italic.ttf", "Georgia Bold.ttf"], s)


# --------------------------------------------------------------------------- helpers
def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def cover(img, tw, th):
    s = max(tw / img.width, th / img.height)
    img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))))
    x, y = (img.width - tw) // 2, (img.height - th) // 2
    return img.crop((x, y, x + tw, y + th))


def scrim(img, frac, strength, top=False):
    h = int(H * frac)
    grad = Image.new("L", (1, h), 0)
    for i in range(h):
        t = (1 - i / h) if top else (i / h)
        grad.putpixel((0, i), int(strength * t ** 1.4))
    grad = grad.resize((W, h))
    blk = Image.new("RGB", (W, h), (0, 0, 0))
    img.paste(blk, (0, 0 if top else H - h), grad)
    return img


def chip(draw, xy, text, fnt, pad=(34, 20), fill=YELLOW, fg=INK, radius=14):
    x, y = xy
    arr = text.rstrip().endswith("→")
    label = text.rstrip()[:-1].rstrip() if arr else text
    tw = draw.textlength(label, font=fnt); asc, desc = fnt.getmetrics(); th = asc + desc
    gap, aw = (20, int(th * 0.55)) if arr else (0, 0)
    draw.rounded_rectangle([x, y, x + tw + gap + aw + pad[0] * 2, y + th + pad[1] * 2], radius=radius, fill=fill)
    draw.text((x + pad[0], y + pad[1]), label, font=fnt, fill=fg)
    if arr:
        ax = x + pad[0] + tw + gap; cy = y + pad[1] + th / 2; ah = th * 0.46
        draw.polygon([(ax, cy - ah / 2), (ax, cy + ah / 2), (ax + aw, cy)], fill=fg)
    return y + th + pad[1] * 2


def block(draw, x, y, text, fnt, fill, lh, maxw, center_w=None):
    for ln in wrap(draw, text, fnt, maxw):
        if center_w is not None:
            tw = draw.textlength(ln, font=fnt); draw.text((x + (center_w - tw) / 2, y), ln, font=fnt, fill=fill)
        else:
            draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def footer(d, text, fg=GREY):
    d.text((64, H - 50), text, font=F_reg(23), fill=fg)


# --------------------------------------------------------------------------- render lanes
def r_testimonial(imgs, f):
    img = cover(imgs[""], W, H) if imgs.get("") else Image.new("RGB", (W, H), (60, 60, 66))
    img = scrim(img, 0.62, 240)
    d = ImageDraw.Draw(img)
    d.text((54, 54), BRAND.upper(), font=F_bold(30), fill=WHITE)
    q = F_quote(70); ql = wrap(d, f["quote"], q, W - 108)
    y = H - 54 - 150 - len(ql) * 84 - 70
    d.text((48, y - 72), "“", font=F_quote(150), fill=YELLOW)
    for ln in ql:
        d.text((54, y), ln, font=q, fill=WHITE); y += 84
    y += 18
    y = block(d, 54, y, PHRASE, F_bold(36), YELLOW, 46, W - 108); y += 14
    chip(d, (54, y), f["cta"], F_black(34))
    footer(d, DRAMA, (220, 220, 220))
    return img


def r_textcard(imgs, f):
    bg = f.get("bg", TEAL); img = Image.new("RGB", (W, H), bg)
    split = int(H * 0.40)
    if imgs.get(""):
        img.paste(cover(imgs[""], W, split), (0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, split, W, split + 8], fill=YELLOW)
    x, y = 64, split + 54
    d.text((x, y), BRAND.upper(), font=F_bold(28), fill=(150, 200, 200)); y += 52
    for q in f["questions"]:
        y = block(d, x, y, q, F_black(58), WHITE, 70, W - 128); y += 12
    y += 8
    y = block(d, x, y, PHRASE, F_bold(40), YELLOW, 50, W - 128); y += 26
    chip(d, (x, y), f["cta"], F_black(38))
    footer(d, ATTY, (150, 190, 190))
    return img


def r_news(imgs, f):
    img = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 16], fill=RED); M = 70; y = 70
    d.text((M, y), f["kicker"], font=F_bold(38), fill=RED); y += 56
    d.line([M, y, W - M, y], fill=(214, 210, 202), width=3); y += 40
    for ln in wrap(d, f["headline"], F_serif_b(74), W - 2 * M):
        d.text((M, y), ln, font=F_serif_b(74), fill=INK); y += 86
    y += 18
    df = F_serif(38); hl = f.get("highlight", "").lower()
    for ln in wrap(d, f["deck"], df, W - 2 * M):
        cx = M
        for word in ln.split(" "):
            if hl and word.lower().strip(".,—") == hl:
                a, de = df.getmetrics()
                d.rectangle([cx - 4, y + 6, cx + d.textlength(word, font=df) + 6, y + a + de], fill=YELLOW)
            d.text((cx, y), word, font=df, fill=(44, 44, 46)); cx += d.textlength(word + " ", font=df)
        y += 50
    y += 30
    if imgs.get(""):
        hh = 520; img.paste(cover(imgs[""], W - 2 * M, hh), (M, y)); y += hh + 36
    chip(d, (M, y), f["cta"], F_black(36), fill=RED, fg=WHITE)
    footer(d, f.get("foot", "Dramatized news graphic.  " + ATTY))
    return img


def r_checklist(imgs, f):
    bg = f.get("bg", NAVY); img = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(img)
    M = 76; y = 120
    d.text((M, y), BRAND.upper(), font=F_bold(28), fill=f.get("muted", (120, 150, 200))); y += 64
    y = block(d, M, y, f["title"], F_black(60), WHITE, 72, W - 2 * M); y += 46
    acc = f.get("accent", YELLOW)
    for it in f["items"]:
        d.ellipse([M, y + 6, M + 46, y + 52], outline=acc, width=5)
        d.line([M + 12, y + 30, M + 21, y + 42], fill=acc, width=6)
        d.line([M + 21, y + 42, M + 37, y + 16], fill=acc, width=6)
        ny = block(d, M + 74, y, it, F_bold(38), WHITE, 46, W - 2 * M - 74)
        y = max(ny, y + 58) + 14
    y += 12
    if f.get("note"):
        y = block(d, M, y, f["note"], F_bold(38), acc, 48, W - 2 * M); y += 22
    chip(d, (M, y), f["cta"], F_black(36), fill=acc)
    footer(d, ATTY, f.get("muted", (120, 150, 200)))
    return img


def r_stat(imgs, f):
    img = cover(imgs[""], W, H) if imgs.get("") else Image.new("RGB", (W, H), CRIMSON)
    ov = Image.new("RGB", (W, H), (0, 0, 0)); img = Image.blend(img, ov, 0.55)
    d = ImageDraw.Draw(img); M = 70
    d.text((M, 110), BRAND.upper(), font=F_bold(28), fill=(220, 180, 180))
    y = block(d, M, 320, f["over"], F_bold(40), WHITE, 50, W - 2 * M); y += 8
    big = F_black(230); d.text((M - 6, y), f["big"], font=big, fill=REDX)
    by = y + big.getmetrics()[0] + big.getmetrics()[1]
    y = block(d, M, by + 4, f["under"], F_black(54), WHITE, 64, W - 2 * M); y += 26
    y = block(d, M, y, PHRASE, F_bold(36), YELLOW, 46, W - 2 * M); y += 22
    chip(d, (M, y), f["cta"], F_black(36), fill=REDX, fg=WHITE)
    footer(d, f.get("foot", "Source: BMJ, 2024.  " + ATTY), (200, 180, 180))
    return img


def r_notice(imgs, f):
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img); M = 78
    d.rectangle([0, 0, W, 14], fill=NAVY); d.rectangle([0, 14, W, 20], fill=GOLD)
    y = 150
    d.text((M, y), "OFFICIAL LEGAL NOTICE", font=F_bold(30), fill=NAVY); y += 56
    d.line([M, y, W - M, y], fill=(200, 192, 176), width=3); y += 50
    y = block(d, M, y, f["header"], F_serif_b(60), NAVY, 70, W - 2 * M); y += 36
    y = block(d, M, y, f["body"], F_serif(38), (40, 40, 44), 52, W - 2 * M); y += 18
    y = block(d, M, y, PHRASE, F_serif_b(40), NAVY, 50, W - 2 * M); y += 34
    chip(d, (M, y), f["cta"], F_bold(34), fill=NAVY, fg=WHITE); y += 100
    block(d, M, H - 132, f.get("fine", ""), F_reg(22), GREY, 30, W - 2 * M)
    return img


def r_statement(imgs, f):
    bg = f.get("bg", PLUM); img = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(img); M = 90
    acc = f.get("accent", GOLD)
    if f.get("kicker"):
        kt = f["kicker"]; tw = d.textlength(kt, font=F_black(34))
        d.text(((W - tw) / 2, 200), kt, font=F_black(34), fill=acc)
    y = 300
    y = block(d, M, y, f["big"], F_black(72), WHITE, 84, W - 2 * M, center_w=W - 2 * M); y += 40
    y = block(d, M, y, f["sub"], F_bold(40), acc, 52, W - 2 * M, center_w=W - 2 * M); y += 50
    tw = d.textlength(f["cta"].rstrip()[:-1].strip(), font=F_black(38)) + 120
    chip(d, ((W - tw) / 2, y), f["cta"], F_black(38), fill=acc)
    ft = f.get("fine", ATTY); tw = d.textlength(ft, font=F_reg(23))
    d.text(((W - tw) / 2, H - 56), ft, font=F_reg(23), fill=(200, 200, 210))
    return img


def r_mythfact(imgs, f):
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img); M = 76
    half = H // 2
    d.rectangle([0, 0, W, half], fill=(56, 22, 24))
    d.rectangle([0, half, W, H], fill=(14, 48, 32))
    d.text((M, 110), "MYTH", font=F_black(64), fill=REDX)
    block(d, M, 210, f["myth"], F_serif_i(46), WHITE, 58, W - 2 * M)
    d.text((M, half + 70), "FACT", font=F_black(64), fill=GREEN)
    y = block(d, M, half + 170, f["fact"], F_bold(44), WHITE, 56, W - 2 * M); y += 30
    chip(d, (M, y), f["cta"], F_black(36), fill=GREEN, fg=WHITE)
    footer(d, ATTY, (180, 180, 180))
    return img


def r_social(imgs, f):
    img = Image.new("RGB", (W, H), (242, 243, 245)); d = ImageDraw.Draw(img)
    card = (255, 255, 255); pad = 36
    d.rectangle([pad, pad, W - pad, H - pad], fill=card)
    x = pad + 30; y = pad + 30
    d.ellipse([x, y, x + 84, y + 84], fill=(20, 70, 72))
    d.text((x + 22, y + 22), "D", font=F_black(44), fill=WHITE)
    d.text((x + 104, y + 8), BRAND, font=F_bold(34), fill=(20, 20, 22))
    d.text((x + 104, y + 50), "Sponsored · ", font=F_reg(26), fill=(120, 120, 124))
    y += 110
    y = block(d, x, y, f["text"], F_reg(36), (28, 28, 30), 48, W - 2 * pad - 60); y += 24
    # embedded photo
    ph = 560
    if imgs.get(""):
        img.paste(cover(imgs[""], W - 2 * pad - 60, ph), (x, y))
    y += ph + 26
    d.line([x, y, W - pad - 30, y], fill=(228, 228, 230), width=2); y += 22
    for lab in ["👍 Like", "💬 Comment", "↪ Share"]:
        pass
    d.text((x, y), "1.2K        324 comments        88 shares", font=F_reg(26), fill=(120, 120, 124)); y += 50
    chip(d, (x, y), f["cta"], F_bold(34), fill=(24, 119, 242), fg=WHITE)
    d.text((x, H - pad - 40), ATTY, font=F_reg(22), fill=(150, 150, 154))
    return img


def r_reddit(imgs, f):
    img = Image.new("RGB", (W, H), (26, 26, 28)); d = ImageDraw.Draw(img); M = 60
    card = (33, 35, 38); d.rounded_rectangle([40, 90, W - 40, H - 90], radius=22, fill=card)
    x = M + 24; y = 140
    d.ellipse([x, y, x + 56, y + 56], fill=(255, 90, 40))
    d.text((x + 74, y + 4), "r/legaladvice", font=F_bold(30), fill=(230, 230, 232))
    d.text((x + 74, y + 40), "Posted by u/throwaway_depo · 14h", font=F_reg(24), fill=(140, 140, 144))
    y += 96
    y = block(d, x, y, f["title"], F_black(48), WHITE, 58, W - 2 * M - 48); y += 24
    y = block(d, x, y, f["body"], F_reg(34), (208, 208, 212), 46, W - 2 * M - 48); y += 30
    d.text((x, y), "▲  342      ▼      💬 96 comments", font=F_bold(28), fill=(140, 140, 144)); y += 64
    d.rounded_rectangle([x, y, W - M - 24, y + 210], radius=16, fill=(42, 44, 48))
    d.text((x + 22, y + 18), "u/case_help · top comment", font=F_bold(26), fill=(120, 180, 255))
    block(d, x + 22, y + 58, f["reply"], F_reg(32), (224, 224, 228), 44, W - 2 * M - 92)
    d.text((M + 24, H - 130), "Dramatization.  " + ATTY, font=F_reg(22), fill=(130, 130, 134))
    return img


def r_texts(imgs, f):
    img = Image.new("RGB", (W, H), (18, 20, 24)); d = ImageDraw.Draw(img); M = 56
    d.text((M, 70), "Messages", font=F_bold(34), fill=(150, 150, 156))
    d.line([0, 130, W, 130], fill=(40, 42, 48), width=2)
    y = 180
    for side, txt in f["bubbles"]:
        out = side == "out"
        bf = F_reg(36); maxw = 620
        lines = wrap(d, txt, bf, maxw - 60)
        bw = max(d.textlength(l, font=bf) for l in lines) + 60
        bh = len(lines) * 48 + 36
        bx = W - M - bw if out else M
        col = (10, 132, 255) if out else (58, 60, 66)
        d.rounded_rectangle([bx, y, bx + bw, y + bh], radius=28, fill=col)
        ty = y + 18
        for l in lines:
            d.text((bx + 30, ty), l, font=bf, fill=WHITE); ty += 48
        y += bh + 26
    # link bubble
    y += 6
    d.rounded_rectangle([M, y, W - M, y + 150], radius=20, fill=(40, 42, 48))
    d.text((M + 28, y + 26), BRAND, font=F_bold(34), fill=WHITE)
    d.text((M + 28, y + 74), "See if you qualify  ▸", font=F_bold(34), fill=YELLOW)
    d.text((M, H - 56), ATTY, font=F_reg(22), fill=(120, 120, 126))
    return img


def r_letter(imgs, f):
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img); M = 96
    # faint ruled lines
    for ly in range(220, H - 120, 64):
        d.line([M, ly, W - M, ly], fill=(228, 222, 210), width=2)
    y = 150
    for para in f["lines"]:
        y = block(d, M, y, para, F_serif_i(42), (40, 38, 40), 64, W - 2 * M); y += 26
    y += 10
    d.text((M, y), f.get("sign", "— " + BRAND), font=F_quote(46), fill=NAVY)
    footer(d, DRAMA, GREY)
    return img


def r_advertorial(imgs, f):
    img = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(img); M = 72
    d.text((M, 80), f["kicker"], font=F_black(32), fill=REDX)
    y = 140
    y = block(d, M, y, f["headline"], F_serif_b(66), INK, 78, W - 2 * M); y += 28
    if imgs.get(""):
        hh = 560; img.paste(cover(imgs[""], W - 2 * M, hh), (M, y)); y += hh + 30
    y = block(d, M, y, f["para"], F_serif(37), (44, 44, 46), 50, W - 2 * M); y += 26
    chip(d, (M, y), f["cta"], F_black(34), fill=INK, fg=WHITE)
    footer(d, ATTY)
    return img


def r_caption_photo(imgs, f):
    img = cover(imgs[""], W, H) if imgs.get("") else Image.new("RGB", (W, H), STEEL)
    top = f.get("text_pos", "bottom") == "top"
    img = scrim(img, 0.5, 235, top=top)
    d = ImageDraw.Draw(img); M = 60
    y = 90 if top else None
    if not top:
        # measure then bottom-anchor
        tmp = []
        for ln in wrap(d, f["headline"], F_black(58), W - 2 * M):
            tmp.append(ln)
        sub_lines = wrap(d, f["sub"], F_bold(34), W - 2 * M)
        y = H - 60 - 150 - len(sub_lines) * 44 - len(tmp) * 70 - 60
    if f.get("kicker"):
        d.text((M, y), f["kicker"], font=F_black(30), fill=YELLOW); y += 50
    y = block(d, M, y, f["headline"], F_black(58), WHITE, 70, W - 2 * M); y += 14
    y = block(d, M, y, f["sub"], F_bold(34), (235, 235, 235), 44, W - 2 * M); y += 10
    y = block(d, M, y, PHRASE, F_bold(34), YELLOW, 44, W - 2 * M); y += 18
    chip(d, (M, y), f["cta"], F_black(34))
    footer(d, DRAMA, (220, 220, 220))
    return img


def r_thennow(imgs, f):
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img)
    bar = 150; ph = (H - bar) // 2
    for key, y0, lab, cap in [("then", 0, "THEN", f["then"]), ("now", ph, "NOW", f["now"])]:
        seg = cover(imgs[key], W, ph) if imgs.get(key) else Image.new("RGB", (W, ph), STEEL)
        seg = scrim(seg, 0.6, 220) if False else seg
        img.paste(seg, (0, y0))
    d = ImageDraw.Draw(img)
    # darken strips for labels
    for y0, lab, cap, col in [(0, "THEN", f["then"], (120, 120, 130)), (ph, "NOW", f["now"], REDX)]:
        d.rectangle([0, y0 + ph - 120, W, y0 + ph], fill=(0, 0, 0)) if False else None
        ov = Image.new("RGBA", (W, 130), (0, 0, 0, 150)); img.paste(Image.new("RGB", (W, 130), (0, 0, 0)), (0, y0 + ph - 130), ov.split()[3])
        d.text((60, y0 + ph - 116), lab, font=F_black(40), fill=col)
        block(d, 60, y0 + ph - 70, cap, F_bold(34), WHITE, 40, W - 240)
    d.rectangle([0, ph - 4, W, ph + 4], fill=YELLOW)
    d.rectangle([0, H - bar, W, H], fill=INK)
    block(d, 60, H - bar + 22, f["bar"], F_bold(33), WHITE, 40, W - 380)
    chip(d, (W - 360, H - bar + 36), f["cta"], F_black(30))
    return img


LANES = {"testimonial": r_testimonial, "textcard": r_textcard, "news": r_news, "checklist": r_checklist,
         "stat": r_stat, "notice": r_notice, "statement": r_statement, "mythfact": r_mythfact,
         "social": r_social, "reddit": r_reddit, "texts": r_texts, "letter": r_letter,
         "advertorial": r_advertorial, "caption_photo": r_caption_photo, "thennow": r_thennow}

NOTEXT = (" Absolutely NO text, no letters, no numbers, no words, no captions, no watermark, no logo "
          "anywhere in the image.")
REAL = (" Photoreal candid documentary photo, natural skin texture with visible pores and fine lines, "
        "no beauty retouching, no filter, no makeup, ordinary relatable person, NOT a glamour or stock-model shot.")


# --------------------------------------------------------------------------- formats (all 20)
FORMATS = [
    dict(n=1, slug="quiz", lane="textcard", aspect="4:5", bg=TEAL,
         images={"": "Photoreal clinical still: a brain MRI scan glowing on a backlit radiology light-box, "
                     "cool teal and white tones, shallow depth of field, serious hospital mood, no people." + NOTEXT},
         questions=["Diagnosed with a brain tumor (meningioma)?", "Were you on the Depo-Provera shot?"],
         cta="Take the 60-second quiz →"),
    dict(n=2, slug="criteria", lane="checklist", aspect="4:5", bg=NAVY, accent=YELLOW, muted=(120, 150, 200),
         images={}, title="Living with a meningioma? See if you qualify.",
         items=["Diagnosed with a meningioma (brain tumor) — MRI or CT confirmed",
                "Used Depo-Provera or its generic for 1+ year (2+ shots)", "Diagnosed in 1992 or later"],
         note=None, cta="Check your eligibility →"),
    dict(n=3, slug="stat", lane="stat", aspect="4:5",
         images={"": "Photoreal dark clinical background: a brain MRI scan on a dim backlit display, deep "
                     "shadows, moody red-and-charcoal tone, no people." + NOTEXT},
         over="A new study found women who used the Depo-Provera shot for over a year were",
         big="5.6×", under="more likely to develop a meningioma — a brain tumor.",
         cta="See if you qualify →"),
    dict(n=4, slug="everything_right", lane="caption_photo", aspect="4:5", text_pos="bottom",
         images={"": "An athletic, healthy woman about 38 with an olive complexion and dark hair in a ponytail, "
                     "in activewear in a bright modern kitchen after a workout holding a water bottle, looking "
                     "quietly worried and far-off." + REAL + NOTEXT},
         kicker="DIAGNOSED WITH A MENINGIOMA?",
         headline="You did everything right. So where did the brain tumor come from?",
         sub="Long-term Depo-Provera use is now linked to meningioma.", cta="See if you qualify →"),
    dict(n=5, slug="symptom", lane="checklist", aspect="4:5", bg=AMBER_BG, accent=AMBER, muted=(200, 160, 90),
         images={}, title="A meningioma can grow quietly.",
         items=["Headaches that won't quit", "Vision changes or loss", "Memory problems", "Seizures"],
         note="Diagnosed — and once on Depo-Provera? You may qualify for significant compensation.",
         cta="Check eligibility →"),
    dict(n=6, slug="authority", lane="caption_photo", aspect="4:5", text_pos="bottom",
         images={"": "A warm, reassuring professional woman about 46 with light-brown skin and shoulder-length "
                     "hair, in a softly lit office, looking at the camera with calm compassion." + REAL + NOTEXT},
         headline="Diagnosed with a meningioma after the Depo-Provera shot?",
         sub="We're helping women across the country review their claims.", cta="Start your free case review →"),
    dict(n=7, slug="native_post", lane="social", aspect="4:5",
         images={"": "Photoreal product still: a small glass medical vial and a syringe on a clean clinical "
                     "stainless surface under soft daylight, pharmacy feel, no people." + NOTEXT},
         text="If you've been diagnosed with a meningioma (a brain tumor) and you were on the Depo shot, the two "
              "may be linked — and you may qualify for significant compensation.", cta="Learn more"),
    dict(n=8, slug="notice", lane="notice", aspect="4:5", images={},
         header="Meningioma / Brain-Tumor Legal Review",
         body="Claims involving meningioma (brain tumor) diagnoses following use of the Depo-Provera injection "
              "are now under review. A free, confidential case review is available.",
         cta="Request a free review →",
         fine="No guarantee of outcome. Eligibility requirements apply.  " + ATTY),
    dict(n=9, slug="news_headline", lane="news", aspect="4:5",
         images={"": "Photoreal news-documentary still: a radiologist in a dim hospital reading room examining a "
                     "brain MRI on a large backlit display, broadcast health-news b-roll feel, slight grain." + NOTEXT},
         kicker="HEALTH WATCH", headline="Brain-Tumor Diagnoses Tied to Common Birth-Control Shot",
         deck="Studies link the Depo-Provera shot to meningioma — a tumor in the lining of the brain. Women "
              "diagnosed are now filing claims nationwide.", highlight="meningioma", cta="See if you qualify →"),
    dict(n=10, slug="value", lane="statement", aspect="4:5", bg=PLUM, accent=GOLD,
         big="A meningioma diagnosis changes everything.",
         sub="If you used Depo-Provera, you may qualify for significant compensation.",
         cta="See if you qualify →", fine="Results not guaranteed. Eligibility applies.  " + ATTY, images={}),
    dict(n=11, slug="testimonial", lane="testimonial", aspect="4:5",
         images={"": "An ordinary, relatable woman about 50 sitting quietly at her kitchen table at home in soft "
                     "natural window light, tired and worried, gazing off-camera, plain casual top." + REAL + NOTEXT},
         quote="They said it was a brain tumor. A meningioma.", cta="See if you qualify →"),
    dict(n=12, slug="advertorial", lane="advertorial", aspect="4:5",
         images={"": "An editorial portrait of a thoughtful woman about 45 by a rain-streaked window, soft "
                     "natural light, serious and reflective, magazine health-feature feel." + REAL + NOTEXT},
         kicker="HEALTH", headline="Thousands of women, one brain tumor, one common link",
         para="A meningioma grows in the lining of the brain. For years, women diagnosed with one were told it "
              "was just bad luck. Now researchers see a shared cause — the Depo-Provera birth-control shot.",
         cta="Read more →"),
    dict(n=13, slug="open_letter", lane="letter", aspect="4:5", images={},
         lines=["To every woman living with a meningioma —",
                "If you've been diagnosed with this brain tumor, please read this.",
                "It may not be a coincidence, and it may not be your fault. The Depo-Provera shot has been "
                "linked to these tumors, and most of us were never warned.",
                "You may qualify for significant compensation. It's free and private to find out.",
                "You're not alone."], sign="— Depo-Provera Claims"),
    dict(n=14, slug="reddit", lane="reddit", aspect="4:5", images={},
         title="Diagnosed with a meningioma — turns out my old birth control may have caused it?",
         body="I was on Depo-Provera from about 2016–2021. Got diagnosed with a meningioma last year and my "
              "sister sent me an article saying they're connected. Is there really a lawsuit over this?",
         reply="If you were diagnosed with a meningioma after using Depo, you may qualify for significant "
               "compensation. It's free to check."),
    dict(n=15, slug="texts", lane="texts", aspect="4:5", images={},
         bubbles=[("in", "you know that brain tumor i had removed? the meningioma?"),
                  ("in", "they're saying the depo shot causes them"),
                  ("out", "wait WHAT. i was on depo for YEARS"),
                  ("in", "there's a lawsuit now. you might qualify for compensation"),
                  ("in", "it's free to check 👇")]),
    dict(n=16, slug="faq", lane="checklist", aspect="4:5", bg=(16, 52, 54), accent=YELLOW, muted=(150, 195, 195),
         images={}, title="Diagnosed years ago? Read this.",
         items=["I used Depo years ago — too late to file? Not necessarily. If you were diagnosed with a "
                "meningioma, you may still qualify — even years later.",
                "What does it cost to check? Nothing. It's free and confidential."],
         note=None, cta="See if you qualify →"),
    dict(n=17, slug="then_now", lane="thennow", aspect="4:5",
         images={"then": "A woman about 32 in a bright pharmacy/clinic in 2015, rolling down her sleeve after an "
                         "injection, everyday and trusting, warm daylight." + REAL + NOTEXT,
                 "now": "A woman about 40 in a hospital gown with a head scarf after brain surgery, sitting on a "
                        "hospital bed, tired but composed, clinical light." + REAL + NOTEXT},
         then="Years on the Depo shot. I trusted it.", now="Diagnosed with a meningioma.",
         bar="Used Depo-Provera and diagnosed with a brain tumor?", cta="See if you qualify →"),
    dict(n=18, slug="myth_fact", lane="mythfact", aspect="4:5", images={},
         myth="It's been too long. There's nothing I can do now.",
         fact="If you were diagnosed with a meningioma after using Depo-Provera, you may still qualify for "
              "significant compensation.", cta="See if you qualify →"),
    dict(n=19, slug="psa", lane="statement", aspect="4:5", bg=BLUE, accent=YELLOW, images={},
         kicker="DID YOU KNOW?",
         big="The Depo-Provera shot is now part of a federal lawsuit over brain tumors.",
         sub="Women diagnosed with a meningioma after using it may qualify for significant compensation.",
         cta="See if you qualify →", fine=ATTY),
    dict(n=20, slug="referral", lane="caption_photo", aspect="4:5", text_pos="top",
         images={"": "Two women at home on a sofa, one about 30 gently comforting an older woman about 58 with "
                     "an arm around her, warm lamplight, tender supportive moment." + REAL + NOTEXT},
         kicker="FOR SOMEONE YOU LOVE", headline="Your mom. Your sister. Your best friend.",
         sub="If a woman you love was diagnosed with a meningioma and used Depo-Provera, she may qualify.",
         cta="Help her check →"),
]


def gen_base(slug, key, prompt, aspect, regen=False):
    fn = f"{slug}.png" if key == "" else f"{slug}__{key}.png"
    dest = os.path.join(BASE_DIR, fn)
    if os.path.exists(dest) and not regen:
        return slug, key, dest, "skip"
    try:
        res = kie.generate_gpt_image(prompt, aspect_ratio=aspect, resolution="2K")
    except Exception as e:
        return slug, key, None, f"err:{e}"
    if res.get("status") != "success" or not res.get("urls"):
        return slug, key, None, f"fail:{str(res.get('raw'))[:100]}"
    kie.download(res["urls"][0], dest)
    return slug, key, dest, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--regen-base", default="")
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()

    fmts = FORMATS
    if args.only:
        want = {s.strip() for s in args.only.split(",")}
        fmts = [f for f in FORMATS if f["slug"] in want]
    regen = {s.strip() for s in args.regen_base.split(",") if s.strip()}

    jobs = [(f["slug"], k, p, f["aspect"]) for f in fmts for k, p in f.get("images", {}).items()]
    bases = {}
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(gen_base, s, k, p, a, s in regen): (s, k) for s, k, p, a in jobs}
        for fut in as_completed(futs):
            s, k, path, st = fut.result()
            print(f"[base:{st}] {s} {k or ''} -> {path}", flush=True)
            bases[(s, k)] = path

    print("---- rendering ----", flush=True)
    for f in fmts:
        imgs = {}
        for k in f.get("images", {}):
            p = bases.get((f["slug"], k))
            imgs[k] = Image.open(p).convert("RGB") if p and os.path.exists(p) else None
        img = LANES[f["lane"]](imgs, f)
        out = os.path.join(FINAL_DIR, f"{f['n']:02d}_{f['slug']}_4x5.png")
        img.save(out)
        miss = [k or "(main)" for k in f.get("images", {}) if imgs.get(k) is None]
        print(f"[render] {out}{'  MISSING:' + ','.join(miss) if miss else ''}", flush=True)


if __name__ == "__main__":
    main()
