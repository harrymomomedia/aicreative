"""Justice Covered 'eligibility quiz' UI-card image ad — clone of the IL-juvie quiz format,
adapted to the CA women's-prison campaign. PIL render (pixel-exact regulated text; gpt-image-2
mangles UI text). 1080x1080 (1:1 FB feed) + optional 4:5.

Format (from the reference): white card; bold black question headline naming audience + harm;
4 rounded option rows with blue radio rings (facility qualifier styled as a tappable form);
reassurance + compensation line ("significant potential compensation" — locked phrase, NOT the
reference's "possible financial compensation"); bright-green pill CTA; optional brand logo.

  python scripts/jc_quiz_card.py [--logo path.png] [--out path.png]
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W = H = 1080
BLACK = (17, 17, 17)
BLUE = (41, 171, 232)      # radio ring
GREY = (210, 212, 216)     # option-row border
GREEN = (34, 197, 94)      # CTA pill
WHITE = (255, 255, 255)

HEADLINE = ["Experienced sexual abuse in", "a California women's prison?"]
OPTIONS = [
    ("Chowchilla", "(CCWF)"),
    ("Valley State Prison", "(Chowchilla)"),
    ("CIW (Chino)", None),
    ("Folsom Women's Facility", None),
]
SUB = ["You're not alone. You may qualify", "for significant potential compensation."]
CTA = "Start your free eligibility quiz"

FONT = "/System/Library/Fonts/HelveticaNeue.ttc"   # index 1 = Bold


def F(px):
    return ImageFont.truetype(FONT, px, index=1)


def render(logo_path=None, out="outputs/ccwf_women/image_ads/jc_quiz_1x1.png"):
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    head_f, opt_f = F(56), F(40)
    sub_f, cta_f = F(42), F(44)

    y = 34
    # brand logo top-center (branded-form look)
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA")
        lh = 76
        lw = int(logo.width * lh / logo.height)
        logo = logo.resize((lw, lh), Image.LANCZOS)
        img.paste(logo, ((W - lw) // 2, y), logo)
        y += lh + 20
    for line in HEADLINE:
        d.text((W // 2, y), line, font=head_f, fill=BLACK, anchor="ma")
        y += 68

    # option rows
    row_w, row_h, gap, rad = 760, 108, 22, 22
    rx = (W - row_w) // 2
    y += 22
    for main, sub2 in OPTIONS:
        d.rounded_rectangle([rx, y, rx + row_w, y + row_h], radius=rad,
                            outline=GREY, width=3, fill=WHITE)
        cyy = y + row_h // 2
        r = 20
        d.ellipse([rx + 44 - r, cyy - r, rx + 44 + r, cyy + r], outline=BLUE, width=9)
        tx = rx + 94
        if sub2:
            d.text((tx, cyy - 23), main, font=opt_f, fill=BLACK, anchor="lm")
            d.text((tx, cyy + 23), sub2, font=opt_f, fill=BLACK, anchor="lm")
        else:
            d.text((tx, cyy), main, font=opt_f, fill=BLACK, anchor="lm")
        y += row_h + gap

    y += 20
    for line in SUB:
        d.text((W // 2, y), line, font=sub_f, fill=BLACK, anchor="ma")
        y += 54

    # CTA pill
    y += 22
    pill_w, pill_h = 820, 100
    px0 = (W - pill_w) // 2
    d.rounded_rectangle([px0, y, px0 + pill_w, y + pill_h], radius=pill_h // 2, fill=GREEN)
    d.text((W // 2, y + pill_h // 2), CTA, font=cta_f, fill=WHITE, anchor="mm")

    Path(out).parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"saved {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--logo", default=None)
    ap.add_argument("--out", default="outputs/ccwf_women/image_ads/jc_quiz_1x1.png")
    a = ap.parse_args()
    render(a.logo, a.out)
