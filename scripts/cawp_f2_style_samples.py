"""F2 redesign — render the SAME card content in 3 type treatments over a photo backdrop
so the user can pick the direction. Output: outputs/cawp_f2_form/style_samples/style_{a,b,c}.png"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image, ImageDraw, ImageFont

BD = "outputs/cawp_f2_form/backdrops/bd1_fence.png"
OUT_DIR = "outputs/cawp_f2_form/style_samples"
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1080, 1920
KICKER = "QUESTION 1 OF 4"
HEADLINE = "Which facility were you at?"
SUB = "Chowchilla · CIW · there's a list"

FONT_DIRS = ["assets/fonts/", "/System/Library/Fonts/Supplemental/", "/System/Library/Fonts/"]


def load_font(names, size):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def backdrop():
    img = Image.open(BD).convert("RGB")
    scale = max(W / img.width, H / img.height)
    img = img.resize((int(img.width * scale), int(img.height * scale)))
    x = (img.width - W) // 2
    y = (img.height - H) // 2
    return img.crop((x, y, x + W, y + H))


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def style_a():
    """Docu: bottom-third black gradient, Montserrat Black white headline, amber kicker."""
    img = backdrop()
    grad = Image.new("L", (1, H), 0)
    for yy in range(H):
        a = 0 if yy < H * 0.45 else int(210 * min(1.0, (yy - H * 0.45) / (H * 0.30)))
        grad.putpixel((0, yy), a)
    black = Image.new("RGB", (W, H), (8, 8, 10))
    img = Image.composite(black, img, grad.resize((W, H)))
    d = ImageDraw.Draw(img)
    f_kick = load_font(["Montserrat-Black.ttf", "Arial Bold.ttf"], 40)
    f_head = load_font(["Montserrat-Black.ttf", "Arial Bold.ttf"], 96)
    f_sub = load_font(["Arial.ttf"], 46)
    y = int(H * 0.62)
    d.text((100, y), KICKER, font=f_kick, fill=(232, 163, 61))
    y += 40 + 34
    for ln in wrap(d, HEADLINE.upper(), f_head, W - 200):
        d.text((100, y), ln, font=f_head, fill=(252, 252, 250))
        y += 112
    y += 22
    for ln in wrap(d, SUB, f_sub, W - 200):
        d.text((100, y), ln, font=f_sub, fill=(206, 206, 208))
        y += 60
    img.save(f"{OUT_DIR}/style_a_docu.png")


def style_b():
    """Legal serif: full navy tint, centered cream Georgia, thin gold rule."""
    img = backdrop()
    tint = Image.new("RGB", (W, H), (18, 32, 54))
    img = Image.blend(img, tint, 0.55)
    d = ImageDraw.Draw(img)
    f_kick = load_font(["Arial Bold.ttf"], 38)
    f_head = load_font(["Georgia Bold.ttf", "Times New Roman Bold.ttf"], 100)
    f_sub = load_font(["Georgia.ttf"], 48)
    head_lines = wrap(d, HEADLINE, f_head, W - 240)
    block = 38 + 30 + 4 + 44 + len(head_lines) * 118 + 30 + 56
    y = (H - block) // 2
    kw = d.textlength(KICKER, font=f_kick)
    d.text(((W - kw) / 2, y), KICKER, font=f_kick, fill=(212, 175, 110))
    y += 38 + 30
    d.rectangle([(W - 160) / 2, y, (W + 160) / 2, y + 4], fill=(212, 175, 110))
    y += 4 + 44
    for ln in head_lines:
        lw = d.textlength(ln, font=f_head)
        d.text(((W - lw) / 2, y), ln, font=f_head, fill=(246, 242, 232))
        y += 118
    y += 30
    for ln in wrap(d, SUB, f_sub, W - 240):
        lw = d.textlength(ln, font=f_sub)
        d.text(((W - lw) / 2, y), ln, font=f_sub, fill=(216, 212, 200))
        y += 62
    img.save(f"{OUT_DIR}/style_b_legal.png")


def style_c():
    """Caption-strip: photo untouched, white text on dark rounded box, center-low."""
    img = backdrop().convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    f_kick = load_font(["Arial Bold.ttf"], 36)
    f_head = load_font(["Helvetica.ttc", "Arial Bold.ttf"], 84)
    f_sub = load_font(["Arial.ttf"], 42)
    head_lines = wrap(d, HEADLINE, f_head, W - 320)
    pad = 56
    box_h = pad + 36 + 26 + len(head_lines) * 98 + 20 + 48 + pad
    box_w = W - 160
    y0 = int(H * 0.58)
    d.rounded_rectangle([80, y0, 80 + box_w, y0 + box_h], radius=44, fill=(16, 16, 20, 224))
    y = y0 + pad
    kw = d.textlength(KICKER, font=f_kick)
    d.text(((W - kw) / 2, y), KICKER, font=f_kick, fill=(232, 163, 61))
    y += 36 + 26
    for ln in head_lines:
        lw = d.textlength(ln, font=f_head)
        d.text(((W - lw) / 2, y), ln, font=f_head, fill=(250, 250, 250))
        y += 98
    y += 20
    for ln in wrap(d, SUB, f_sub, W - 320):
        lw = d.textlength(ln, font=f_sub)
        d.text(((W - lw) / 2, y), ln, font=f_sub, fill=(200, 200, 204))
        y += 52
    img = Image.alpha_composite(img, overlay).convert("RGB")
    img.save(f"{OUT_DIR}/style_c_strip.png")


style_a()
style_b()
style_c()
print("samples:", os.listdir(OUT_DIR))
