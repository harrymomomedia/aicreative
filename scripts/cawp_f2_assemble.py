"""F2 'What it actually asks' — assemble question-explainer video.
Faceless: typographic question cards (NO form UI, no buttons/cursor — per
feedback_no_form_click_coaching) hard-cut on Scribe word timestamps over the VO.
Output: outputs/cawp_f2_form/f2_form_explainer.mp4 (1080x1920)."""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image, ImageDraw, ImageFont

from elevenlabs_client import scribe

BASE = "outputs/cawp_f2_form"
VO = f"{BASE}/vo_full_hispanic_f_53.mp3"
WORDS_CACHE = f"{BASE}/vo_words.json"
CARD_DIR = f"{BASE}/cards"
OUT = f"{BASE}/f2_form_explainer.mp4"
os.makedirs(CARD_DIR, exist_ok=True)

W, H = 1080, 1920
PAPER = (252, 252, 251)
INK = (22, 22, 26)
NAVY = (31, 58, 95)
GREY = (108, 108, 112)

FONT_DIRS = ["/System/Library/Fonts/Supplemental/", "/System/Library/Fonts/", "/Library/Fonts/"]


def load_font(names, size):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


F_KICK = load_font(["Arial Bold.ttf"], 40)
F_HEAD = load_font(["Arial Bold.ttf"], 100)
F_SUB = load_font(["Arial.ttf"], 46)

# (slug, anchor_word or None=t0, kicker, headline, sub)
CARDS = [
    ("c0_title", None, "THE FORM", "What it actually asks", "Chowchilla · CIW · California women's prisons"),
    ("c1_facility", "facility", "QUESTION 1 OF 4", "Which facility were you at?", "Chowchilla · CIW · there's a list"),
    ("c2_when", "around", "QUESTION 2 OF 4", "When were you there?", "No exact dates. Just the years is fine."),
    ("c3_who", "who", "QUESTION 3 OF 4", "Who was it?", "A guard · medical staff · another worker"),
    ("c4_what", "part", "QUESTION 4 OF 4", "What happened?", "In your own words. As much or as little as you want."),
    ("c5_thatsit", "everything", "THAT'S IT", "That's everything it asks.", "No police report. No court records."),
    ("c6_private", "answers", "PRIVATE", "Only the law firm sees your answers.", "If a lawyer calls, that's confidential too."),
    ("c7_qualify", "qualify", "", "You may qualify for significant potential compensation.", "For the sexual abuse that happened inside."),
    ("c8_free", "free", "NO RISK", "Free to check.", "A couple minutes. You only pay if you win."),
    ("c9_cta", "link", "NOW", "The link is under this video.", "Go see if you qualify."),
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


def render_card(slug, kicker, headline, sub):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=NAVY)
    max_w = W - 2 * 110
    head_lines = wrap(d, headline, F_HEAD, max_w)
    sub_lines = wrap(d, sub, F_SUB, max_w)
    block_h = (52 if kicker else 0) + 36 + len(head_lines) * 118 + 40 + len(sub_lines) * 62
    y = (H - block_h) // 2 - 60
    if kicker:
        kw = d.textlength(kicker, font=F_KICK)
        d.text(((W - kw) / 2, y), kicker, font=F_KICK, fill=NAVY)
        y += 52 + 36
    for ln in head_lines:
        lw = d.textlength(ln, font=F_HEAD)
        d.text(((W - lw) / 2, y), ln, font=F_HEAD, fill=INK)
        y += 118
    y += 40
    for ln in sub_lines:
        lw = d.textlength(ln, font=F_SUB)
        d.text(((W - lw) / 2, y), ln, font=F_SUB, fill=GREY)
        y += 62
    p = os.path.join(CARD_DIR, f"{slug}.png")
    img.save(p)
    return p


def get_words():
    if os.path.exists(WORDS_CACHE):
        return json.load(open(WORDS_CACHE))
    t = scribe(VO, biased_keywords=["Chowchilla", "CIW"], language_code="en")
    words = [w for w in t.get("words", []) if w.get("type", "word") == "word"]
    json.dump(words, open(WORDS_CACHE, "w"))
    return words


def main():
    words = get_words()
    dur_probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", VO],
        capture_output=True, text=True)
    total = float(dur_probe.stdout.strip())

    # sequential forward anchor search
    times, idx = [], 0
    for slug, anchor, *_ in CARDS:
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
            raise RuntimeError(f"anchor '{anchor}' not found after index {idx}")
        times.append(max(0.0, found - 0.12))
    times.append(total)

    paths = [render_card(s, k, h, sub) for s, _, k, h, sub in CARDS]
    durs = [times[i + 1] - times[i] for i in range(len(CARDS))]
    for (slug, *_), t0, dd in zip(CARDS, times, durs):
        print(f"  {slug}: {t0:6.2f}s  ({dd:.2f}s)")

    # measure VO loudness -> static gain to -16 LUFS + limiter
    ln = subprocess.run(
        ["ffmpeg", "-i", VO, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    stats = json.loads(ln.stderr[ln.stderr.rfind("{"):ln.stderr.rfind("}") + 1])
    gain = -16.0 - float(stats["input_i"])

    cmd = ["ffmpeg", "-y"]
    for p, dd in zip(paths, durs):
        cmd += ["-loop", "1", "-t", f"{dd:.3f}", "-i", p]
    cmd += ["-i", VO]
    n = len(paths)
    fc = "".join(f"[{i}:v]scale={W}:{H},setsar=1[v{i}];" for i in range(n))
    fc += "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v]"
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", f"{n}:a",
            "-af", f"volume={gain:.2f}dB,alimiter=limit=0.794:level=disabled:asc=1",
            "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-r", "30",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", OUT]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"[ok] {OUT}  ({total:.1f}s, gain {gain:+.1f}dB)")


if __name__ == "__main__":
    main()
