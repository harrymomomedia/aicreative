"""F2 'What it actually asks' v2 — photographic backdrops + docu type (style A).
Each beat: gpt-image-2 documentary backdrop + bottom-third gradient + amber kicker +
Montserrat Black headline + grey sub, slow varied zoompan, hard cuts on the cached
Scribe word timings, VO + static gain + limiter. ONE output (disclaimer burned after).
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image, ImageDraw, ImageFont

BASE = "outputs/cawp_f2_form"
VO = f"{BASE}/vo_full_v3.mp3"
WORDS_CACHE = f"{BASE}/vo_words_v3.json"
BD = f"{BASE}/backdrops"
CARD_DIR = f"{BASE}/cards_v3"
SEG_DIR = f"{BASE}/segs_v3"
OUT = f"{BASE}/f2_form_explainer_v3.mp4"
W, H, FPS = 1080, 1920, 30
os.makedirs(CARD_DIR, exist_ok=True)
os.makedirs(SEG_DIR, exist_ok=True)

FONT_DIRS = ["assets/fonts/", "/System/Library/Fonts/Supplemental/", "/System/Library/Fonts/"]


def load_font(names, size):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


F_KICK = load_font(["Montserrat-Black.ttf", "Arial Bold.ttf"], 40)
F_HEAD = load_font(["Montserrat-Black.ttf", "Arial Bold.ttf"], 92)
F_SUB = load_font(["Arial.ttf"], 46)
AMBER = (232, 163, 61)

# (slug, backdrop, anchor_word, kicker, headline, sub)
CARDS = [
    ("a1", "bd1_fence", None, "REAL QUICK", "Chowchilla · CCWF · CIW", "Or any other California women's prison. This is for you."),
    ("a2", "bd7_qualify", "abused", "STAFF SEXUAL ABUSE", "You may qualify for significant potential compensation.", "It starts with one private claim form."),
    ("c0", "bd0_phone_porch", "tell", "THE FORM", "What it actually asks", "It's shorter than you think."),
    ("c1", "bd1_fence", "facility", "QUESTION 1 OF 4", "Which facility were you at?", "Chowchilla · CIW · there's a list"),
    ("c2", "bd2_years", "around", "QUESTION 2 OF 4", "When were you there?", "No exact dates. Just the years is fine."),
    ("c3", "bd3_corridor", "who", "QUESTION 3 OF 4", "Who was it?", "A guard · medical staff · another worker"),
    ("c4", "bd4_ownwords", "part", "QUESTION 4 OF 4", "What happened?", "In your own words. As much or as little as you want."),
    ("c5", "bd5_norecords", "everything", "THAT'S IT", "That's everything it asks.", "No police report. No court records."),
    ("c6", "bd6_private", "answers", "PRIVATE", "Only the law firm sees your answers.", "If a lawyer calls, that's confidential too."),
    ("c7", "bd7_qualify", "qualify", "", "You may qualify for significant potential compensation.", "For the sexual abuse that happened inside."),
    ("c8", "bd8_free", "free", "NO RISK", "Free to check.", "A couple minutes. You only pay if you win."),
    ("c9", "bd9_cta", "link", "NOW", "The link is under this video.", "Go see if you qualify."),
]

# varied zoompan recipes, rotated (photos — center anchoring is fine here)
RECIPES = [
    "z='min(1+0.12*on/{F},1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    "z='min(1+0.10*on/{F},1.10)':x='iw/3-(iw/zoom/3)':y='ih/2-(ih/zoom/2)'",
    "z='if(eq(on,0),1.14,max(zoom-0.12/{F},1.02))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    "z='1.08':x='iw/2-(iw/zoom/2)':y='ih*0.10+(ih*0.28-ih*0.10)*on/{F}'",
]


def wrap(d, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def style_a_card(slug, backdrop, kicker, headline, sub):
    out = f"{CARD_DIR}/{slug}.png"
    img = Image.open(f"{BD}/{backdrop}.png").convert("RGB")
    scale = max(W / img.width, H / img.height)
    img = img.resize((int(img.width * scale), int(img.height * scale)))
    x = (img.width - W) // 2
    y = (img.height - H) // 2
    img = img.crop((x, y, x + W, y + H))
    grad = Image.new("L", (1, H), 0)
    for yy in range(H):
        a = 0 if yy < H * 0.36 else int(215 * min(1.0, (yy - H * 0.36) / (H * 0.30)))
        grad.putpixel((0, yy), a)
    img = Image.composite(Image.new("RGB", (W, H), (8, 8, 10)), img, grad.resize((W, H)))
    d = ImageDraw.Draw(img)
    # Reels eye-line: center the whole text block at ~62% of frame height (user rule
    # 2026-06-10 — the reading line should sit just below the 50% cut, around 60-65%)
    head_lines_n = len(wrap(d, headline.upper(), F_HEAD, W - 200))
    sub_lines_n = len(wrap(d, sub, F_SUB, W - 200))
    block_h = (72 if kicker else 0) + head_lines_n * 108 + 20 + sub_lines_n * 60
    yp = int(H * 0.62 - block_h / 2)
    if kicker:
        d.text((100, yp), kicker, font=F_KICK, fill=AMBER)
        yp += 40 + 32
    for ln in wrap(d, headline.upper(), F_HEAD, W - 200):
        d.text((100, yp), ln, font=F_HEAD, fill=(252, 252, 250))
        yp += 108
    yp += 20
    for ln in wrap(d, sub, F_SUB, W - 200):
        d.text((100, yp), ln, font=F_SUB, fill=(208, 208, 210))
        yp += 60
    img.save(out)
    return out


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"cmd failed: {' '.join(cmd[:8])}...\n{r.stderr[-300:]}")


def main():
    words = json.load(open(WORDS_CACHE))
    total = float(subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                                  "-of", "csv=p=0", VO], capture_output=True, text=True).stdout.strip())
    times, idx = [], 0
    for _, _, anchor, *_ in CARDS:
        if anchor is None:
            times.append(0.0)
            continue
        found = None
        for j in range(idx, len(words)):
            if words[j]["text"].strip(".,?!:;\"'").lower().startswith(anchor):
                found = words[j]["start"]
                idx = j + 1
                break
        if found is None:
            raise RuntimeError(f"anchor '{anchor}' not found")
        times.append(max(0.0, found - 0.12))
    times.append(total)

    segs = []
    for i, (slug, backdrop, _, kicker, headline, sub) in enumerate(CARDS):
        dur = times[i + 1] - times[i]
        card = style_a_card(slug, backdrop, kicker, headline, sub)
        seg = f"{SEG_DIR}/{slug}.mp4"
        segs.append(seg)
        if os.path.exists(seg) and os.path.getsize(seg) > 1000:
            continue
        frames = max(1, int(dur * FPS))
        zp = RECIPES[i % len(RECIPES)].replace("{F}", str(frames))
        run(["ffmpeg", "-y", "-loop", "1", "-t", f"{dur:.3f}", "-r", str(FPS), "-i", card,
             "-filter_complex",
             f"[0:v]scale=2160:3840,zoompan={zp}:d=1:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p[v]",
             "-map", "[v]", "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-an", seg])
        print(f"[seg] {slug} ({dur:.1f}s)", flush=True)

    lst = f"{SEG_DIR}/concat.txt"
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    ln = subprocess.run(["ffmpeg", "-i", VO, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
                         "-f", "null", "-"], capture_output=True, text=True)
    stats = json.loads(ln.stderr[ln.stderr.rfind("{"):ln.stderr.rfind("}") + 1])
    gain = -16.0 - float(stats["input_i"])
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", VO,
         "-map", "0:v", "-map", "1:a",
         "-af", f"volume={gain:+.2f}dB,alimiter=limit=0.794:level=disabled:asc=1",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", OUT])
    print(f"[final] {OUT} ({total:.1f}s, gain {gain:+.1f}dB)", flush=True)


if __name__ == "__main__":
    main()
