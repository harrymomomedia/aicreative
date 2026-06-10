"""F1 news-reaction ad — headline backdrop cards (1080x1920, 9:16).
Stylized news-headline RE-CREATIONS (no outlet branding/screenshots — rights-clean).
Facts per inventory/womens_prison_testimonial_research.md. Headline text stays in the
top ~55% so the bottom-right PIP persona + captions (vpos 0.85) never collide."""
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.join("outputs", "cawp_f1_news", "cards")
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1080, 1920
MARGIN = 90
PAPER = (250, 248, 244)
INK = (24, 24, 26)
RED = (178, 24, 24)
GREY = (110, 110, 112)

FONT_DIRS = [
    "/System/Library/Fonts/Supplemental/",
    "/System/Library/Fonts/",
    "/Library/Fonts/",
]


def load_font(names, size):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


F_KICK = load_font(["Arial Bold.ttf", "Helvetica.ttc"], 40)
F_HEAD = load_font(["Georgia Bold.ttf", "Times New Roman Bold.ttf", "Georgia.ttf"], 92)
F_DATE = load_font(["Arial.ttf", "Helvetica.ttc"], 38)
F_BODY = load_font(["Georgia.ttf", "Times New Roman.ttf"], 37)

HERO_DIR = os.path.join("outputs", "cawp_f1_news", "cards", "heroes")

CARDS = [
    {
        "slug": "card1_sentence",
        "kicker": "CALIFORNIA",
        "headline": "Chowchilla prison guard sentenced to 224 years",
        "sub": "Convicted of sexually abusing incarcerated women",
        "dateline": "Madera County — August 2025",
        "hero": "hero1_prison.png",
        "body": [
            "A former correctional officer who worked at the Central California Women's Facility for more than a decade was sentenced to 224 years in state prison, the maximum allowed, after a jury convicted him of dozens of counts of sexual abuse against incarcerated women.",
            "Thirteen women testified at the four-month trial, several of them still incarcerated. The first report against the officer was made in 2014.",
            "Advocates say the case has prompted hundreds of additional survivors to come forward.",
        ],
    },
    {
        "slug": "card2_doj",
        "kicker": "JUSTICE DEPARTMENT",
        "headline": "Federal civil rights investigation opened into California’s two women’s prisons",
        "dateline": "CCWF Chowchilla & CIW — September 2024",
        "hero": "hero2_federal.png",
        "body": [
            "The U.S. Department of Justice has opened a civil rights investigation into whether California protects women incarcerated at its two women's prisons from sexual abuse by staff.",
            "The inquiry covers the Central California Women's Facility in Chowchilla and the California Institution for Women, and will examine how complaints of staff sexual misconduct are prevented, reported and investigated.",
        ],
    },
    {
        "slug": "card3_filings",
        "kicker": "COURTS",
        "headline": "Nearly 500 women file lawsuits over sexual abuse at California women’s prisons",
        "dateline": "CCWF & CIW — 2026",
        "hero": "hero3_files.png",
        "body": [
            "Nearly 500 civil lawsuits have been filed by women who say they were sexually abused by staff while incarcerated in California's women's prisons, and new cases continue to be filed.",
            "The suits describe abuse spanning decades at the Central California Women's Facility and the California Institution for Women. Attorneys say many more survivors have not yet come forward.",
        ],
    },
]


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


for card in CARDS:
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # top accent bar + thin rule
    d.rectangle([0, 0, W, 18], fill=RED)
    y = 150
    d.text((MARGIN, y), card["kicker"], font=F_KICK, fill=RED)
    y += 40 + 46
    d.line([MARGIN, y, W - MARGIN, y], fill=(210, 206, 198), width=3)
    y += 56
    lines = wrap(d, card["headline"], F_HEAD, W - 2 * MARGIN)
    for ln in lines:
        d.text((MARGIN, y), ln, font=F_HEAD, fill=INK)
        y += 112
    if card.get("sub"):
        y += 24
        for ln in wrap(d, card["sub"], F_DATE, W - 2 * MARGIN):
            d.text((MARGIN, y), ln, font=F_DATE, fill=INK)
            y += 50
    y += 36
    d.text((MARGIN, y), card["dateline"], font=F_DATE, fill=GREY)
    y += 38 + 44

    # hero image — full content width, center-cropped to ~16:9.5
    hero_path = os.path.join(HERO_DIR, card["hero"])
    if os.path.exists(hero_path):
        hero = Image.open(hero_path).convert("RGB")
        target_w, target_h = W - 2 * MARGIN, 540
        scale = target_w / hero.width
        hero = hero.resize((target_w, int(hero.height * scale)))
        if hero.height > target_h:
            top = (hero.height - target_h) // 2
            hero = hero.crop((0, top, target_w, top + target_h))
        img.paste(hero, (MARGIN, y))
        y += hero.height + 44

    # body paragraphs (lower part may sit behind the PIP persona — intentional)
    for para in card["body"]:
        for ln in wrap(d, para, F_BODY, W - 2 * MARGIN):
            if y > 1840:
                break
            d.text((MARGIN, y), ln, font=F_BODY, fill=(40, 40, 42))
            y += 52
        y += 26
        if y > 1840:
            break

    out = os.path.join(OUT_DIR, f"{card['slug']}.png")
    img.save(out)
    print(f"[ok] {out}  (content ends at y={min(y,1840)}, {min(y,1840)/H:.0%} of frame)")
print("done")
