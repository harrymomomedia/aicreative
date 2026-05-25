#!/usr/bin/env python3
"""Burn Submagic-style "Hormozi 3" captions (general — works on any video/text).

Verified frame-by-frame from a real Submagic Hormozi 3 export (2026-05-21):
  FONT      Montserrat Black (900), ALL CAPS  (assets/fonts/Montserrat-Black.ttf)
  SIZE      font_ratio ~0.035 of frame height (a line of ~2-3 words ~40% of width)
  POSITION  lower-third, text-block center ~0.70
  STROKE    black outline ~0.06*fontsize ; subtle shadow ; NO glow
  COLOR     default WHITE ; active LINE = card accent (rotates per card y->g->r)
  TEXT ANIM hard cut-in, captions stay ON continuously (no per-word flashing)
  EMOJI     ANIMATED (Noto animated emoji GIF, looping) centered below keyword cards;
            falls back to a static Twemoji PNG if no animated version exists

Pipeline: Scribe word timestamps -> cards -> per-active-line PNG (tiled to fill the whole
card, no gaps) + looping animated-emoji GIF overlay -> ffmpeg overlay chain.

Usage:
  .venv/bin/python scripts/caption_hormozi3.py <in.mp4> [--out out.mp4]
      [--font-ratio 0.035] [--vertical-pos 0.70] [--max-words 3] [--no-emoji] [--end N]
"""
import argparse
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from scripts.caption_styled import (extract_audio, probe_size, chunk_words, auto_vertical_pos, run,
                                     render_disclaimer, find_font, DEFAULT_DISCLAIMER)

FONT = str(ROOT / "assets/fonts/Montserrat-Black.ttf")
EMOJI_DIR = ROOT / "assets/emoji"
EMOJI_DIR.mkdir(parents=True, exist_ok=True)

ACCENTS = [(252, 251, 20), (42, 248, 43), (238, 25, 22)]  # per-card: yellow, green, red
WHITE = (255, 255, 255)

# Font is sized relative to WIDTH, NOT height — a phone shows the SAME horizontal width whether the
# video is 9:16 or 4:5 or 1:1, so the caption must be the SAME physical size across aspects (sizing
# to height made 4:5 captions ~70% the size of 9:16's despite identical 720px width). font_ratio
# keeps its historical 9:16 meaning: there height = width*16/9, so height*ratio == width*(16/9)*ratio.
# Computing from width with that 16/9 reference leaves 9:16 byte-identical and makes 4:5/1:1 match it.
REF_ASPECT = 16 / 9
def _font_px(width, ratio):
    return max(16, int(width * REF_ASPECT * ratio))

# keyword -> emoji (Apple Color Emoji has every glyph incl. ZWJ families / flags).
# first match per card wins. Matches Submagic's semantic picks.
KEYWORD_EMOJI = {
    "mama": "❤️", "mom": "❤️", "mother": "❤️", "daughter": "❤️", "sister": "❤️", "love": "❤️",
    "california": "🔒", "prison": "🔒", "prisons": "🔒", "locked": "🔒", "jail": "🔒",
    "guards": "🚨", "guard": "🚨", "police": "🚨",
    "years": "⏳", "year": "⏳", "late": "⏳", "time": "⏳", "minutes": "⏱️", "minute": "⏱️",
    "wrong": "❌", "never": "🚫", "nobody": "🚫", "nothing": "🤷", "don't": "🚫",
    "compensation": "💰", "money": "💰", "owed": "💰", "paid": "💰", "cash": "💰",
    "abuse": "💔", "sexual": "💔", "hurt": "💔", "pain": "💔", "broken": "💔",
    "confidential": "🤫", "private": "🤫", "quiet": "🤫", "secret": "🤫",
    "button": "👇", "tap": "👇", "press": "👇", "click": "👇",
    "qualify": "✅", "yes": "✅", "real": "✅", "true": "✅",
    "case": "⚖️", "lawyer": "⚖️", "attorney": "⚖️", "legal": "⚖️", "court": "⚖️",
    "phone": "📱", "screen": "📱", "text": "📱", "called": "📞", "call": "📞",
    "story": "📰", "article": "📰", "news": "📰", "read": "📖", "form": "📝",
    "church": "🙏", "sunday": "🙏", "god": "🙏", "pray": "🙏", "blessed": "🙏",
    "cry": "😢", "tears": "😢", "sad": "😢", "crying": "😭",
    "shocked": "😱", "crazy": "😱", "scared": "😱",
    "remember": "💭", "thought": "💭", "knew": "💭", "think": "💭", "thinking": "💭",
    "figured": "💭", "figure": "💭", "wondered": "💭",
    "fire": "🔥", "amazing": "🔥", "fight": "🔥",
    # --- expanded coverage so more cards get an emoji (legal-ad vocabulary) ---
    "ago": "⏳", "spent": "⏳", "long": "⏳",
    "thirty": "⏱️", "seconds": "⏱️", "second": "⏱️", "couple": "✌️", "two": "✌️",
    "today": "📅", "days": "📅", "day": "📅",
    "us": "👥", "ours": "👥", "everybody": "👥", "strangers": "👤", "soul": "🙏",
    "hey": "👋", "hi": "👋", "hello": "👋",
    "told": "🗣️", "tell": "🗣️", "telling": "🗣️", "say": "🗣️", "said": "🗣️", "voice": "🗣️", "loud": "🔊",
    "listen": "👂", "hear": "👂", "heard": "👂",
    "lied": "🤥", "lie": "🤥", "lying": "🤥",
    "found": "🔍", "find": "🔍", "look": "👀", "looking": "👀",
    "written": "✍️", "wrote": "✍️", "write": "✍️", "filled": "📝", "fill": "📝",
    "door": "🚪", "closed": "🚪", "inside": "🔒",
    "table": "🍽️", "plate": "🍽️",
    "buried": "🕳️", "bury": "🕳️", "hide": "🙈", "hid": "🙈",
    "sitting": "🪑", "sit": "🪑",
    "lawyers": "⚖️", "complete": "✅", "completely": "✅", "done": "✅", "over": "✅",
    "happened": "❓", "happen": "❓",
    "stays": "🤫",
    # --- IL JDC abuse-survivor campaign vocabulary (morphological variants + topic words) ---
    "abused": "💔", "abusing": "💔", "sexually": "💔", "assault": "💔", "assaulted": "💔",
    "compensated": "💰", "compensate": "💰", "paying": "💰", "pay": "💰", "pays": "💰",
    "survivor": "💪", "survivors": "💪", "changing": "🔄", "change": "🔄", "changed": "🔄",
    "free": "🆓", "check": "🔍", "checking": "🔍", "link": "🔗",
    "juvenile": "🔒", "juvie": "🔒", "hall": "🔒", "detention": "🔒", "facility": "🔒",
    "staff": "🚨", "member": "🚨", "warden": "🚨", "officer": "🚨",
    "crime": "🚔", "criminal": "🚔", "illinois": "📍", "away": "🏃",
    "child": "🧒", "kid": "🧒", "children": "🧒", "kids": "🧒",
    "quietly": "🤫", "now": "⚡",
}

# Emoji art sources:
#  - PRIMARY: Google Noto ANIMATED emoji GIFs — internally animated (flag waves, money jingles),
#    matching what Submagic actually uses. Google art (close-in-spirit to Apple, not identical).
#  - fallback: Apple Color Emoji static (macOS, exact-Apple look but NO internal animation), then Twemoji.
NOTO_GIF = "https://fonts.gstatic.com/s/e/notoemoji/latest/{code}/512.gif"
APPLE_EMOJI_FONT = "/System/Library/Fonts/Apple Color Emoji.ttc"
TWEMOJI_PNG = "https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.0.3/assets/72x72/{tcode}.png"
_apple_font = None


def _apple_static(emoji, size):
    from PIL import Image, ImageDraw, ImageFont
    import os
    global _apple_font
    if os.path.exists(APPLE_EMOJI_FONT):
        try:
            if _apple_font is None:
                _apple_font = ImageFont.truetype(APPLE_EMOJI_FONT, 160)
            canvas = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
            ImageDraw.Draw(canvas).text((30, 12), emoji, font=_apple_font, embedded_color=True)
            bbox = canvas.getbbox()
            if bbox:
                g = canvas.crop(bbox); w, h = g.size; s = max(w, h)
                sq = Image.new("RGBA", (s, s), (0, 0, 0, 0)); sq.alpha_composite(g, ((s - w) // 2, (s - h) // 2))
                return sq.resize((size, size), Image.LANCZOS)
        except Exception:
            pass
    tcode = "-".join(f"{ord(c):x}" for c in emoji if c != "️")
    png = EMOJI_DIR / f"{tcode}.png"
    if not (png.exists() and png.stat().st_size > 200):
        try:
            urllib.request.urlretrieve(TWEMOJI_PNG.format(tcode=tcode), png)
        except Exception:
            return None
    try:
        return Image.open(png).convert("RGBA").resize((size, size), Image.LANCZOS)
    except Exception:
        return None


# Glyphs whose Noto ANIMATED GIF starts in a state that misrepresents the meaning during a
# short (~1s) card — e.g. 💔 begins as a WHOLE heart and only breaks apart late in the loop, so
# on a brief subtitle it reads as ❤️ (romantic — tonally wrong on an abuse line). Force these to
# the static Apple glyph (which shows the broken state immediately).
FORCE_STATIC = {"💔"}


def render_emoji_frames(emoji, size):
    """Return (frames, durations_ms). PREFER the animated Noto GIF when one exists (animated
    beats static); fall back to static Apple Color Emoji (exact Apple look), then Twemoji.
    Glyphs in FORCE_STATIC always use the static Apple art (their animation misleads on short cards)."""
    from PIL import Image
    if emoji in FORCE_STATIC:
        g = _apple_static(emoji, size)
        if g is not None:
            return [g], [60]
    ncode = "_".join(f"{ord(c):x}" for c in emoji if c != "️")
    gif = EMOJI_DIR / f"{ncode}.gif"
    miss = EMOJI_DIR / f"{ncode}.nogif"   # remember 404s so we don't refetch every run
    if not (gif.exists() and gif.stat().st_size > 2000) and not miss.exists():
        try:
            urllib.request.urlretrieve(NOTO_GIF.format(code=ncode), gif)
            if not (gif.exists() and gif.stat().st_size > 2000):
                gif.unlink(missing_ok=True); miss.touch()
        except Exception:
            miss.touch()
    if gif.exists() and gif.stat().st_size > 2000:
        try:
            im = Image.open(gif); frames, durs = [], []
            while True:
                frames.append(im.convert("RGBA").resize((size, size), Image.LANCZOS))
                durs.append(im.info.get("duration", 60) or 60)
                im.seek(im.tell() + 1)
        except EOFError:
            pass
        if frames:
            return frames, durs
    # fallback: static Apple Color Emoji (preferred look for non-animated glyphs)
    a = _apple_static(emoji, size)
    return ([a], [1000]) if a is not None else (None, None)


def pick_emoji(words, exclude=None):
    """First keyword→emoji match in the card. If that glyph == `exclude` (the previously placed
    emoji), keep scanning for a DIFFERENT keyword's emoji in the same card; return None if the only
    match repeats `exclude` — so the same emoji never shows back-to-back (distracting)."""
    for w in words:
        key = "".join(c for c in w["text"].lower() if c.isalpha() or c == "'")
        if key in KEYWORD_EMOJI and KEYWORD_EMOJI[key] != exclude:
            return KEYWORD_EMOJI[key]
    return None


def compute_layout(words, width, height, fontsize_ratio, vertical_pos, max_lines):
    """Submagic-style FIT-TO-WIDTH sizing: start at the max font (fontsize_ratio) and shrink
    ONLY until the card wraps to <= max_lines AND the widest line fits target width. Short
    cards stay big; long cards shrink. fontsize_ratio is the MAX/starting size, not fixed."""
    from PIL import ImageFont, ImageDraw, Image
    draw = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    max_w = int(width * 0.60)     # width safety (long single words break here)
    words_per_line = 2            # Submagic stacks ~2 words/line → uniform, tight look
    box_h = int(height * 0.30)    # height guard (rarely binds); long cards wrap to 3 lines
    fontsize = _font_px(width, fontsize_ratio)  # WIDTH-relative → same physical size across aspects
    floor = _font_px(width, 0.028)

    def meas(t, f, ol):
        b = draw.textbbox((0, 0), t, font=f, stroke_width=ol)
        return b[2] - b[0], b[3] - b[1]

    for _ in range(22):
        font = ImageFont.truetype(FONT, fontsize)
        outline = max(2, int(fontsize * 0.06))
        space_w, _ = meas(" ", font, outline)
        lines, cur, cur_w = [], [], 0
        for w in words:
            ww, hh = meas(w["text"], font, outline)
            trial = cur_w + (space_w if cur else 0) + ww
            if cur and (trial > max_w or len(cur) >= words_per_line):
                lines.append(cur); cur = [dict(w, _w=ww, _h=hh)]; cur_w = ww
            else:
                cur.append(dict(w, _w=ww, _h=hh)); cur_w = trial
        if cur:
            lines.append(cur)
        widest = max((sum(m["_w"] for m in ln) + space_w * (len(ln) - 1)) for ln in lines)
        total_h = len(lines) * int(fontsize * 1.16) + (len(lines) - 1) * int(fontsize * 0.10)
        if (len(lines) <= max_lines and widest <= max_w and total_h <= box_h) or fontsize <= floor:
            break
        fontsize = int(fontsize * 0.93)

    line_h = int(fontsize * 1.16)
    line_gap = int(fontsize * 0.10)
    n = len(lines)
    text_h = n * line_h + (n - 1) * line_gap
    y0 = int(height * vertical_pos) - text_h // 2
    placed, cur_y = [], y0
    for line in lines:
        line_w = sum(m["_w"] for m in line) + space_w * (len(line) - 1)
        x = (width - line_w) // 2
        row = [(m["text"], x + sum(line[j]["_w"] + space_w for j in range(i)), cur_y) for i, m in enumerate(line)]
        placed.append(row)
        cur_y += line_h + line_gap
    line_starts = [line[0]["start"] for line in lines]
    return {"fontsize": fontsize, "outline": outline, "placed": placed,
            "line_starts": line_starts, "y0": y0, "text_h": text_h, "text_w": widest,
            "emoji_y": y0 + text_h + int(fontsize * 0.14), "nlines": n}


def render_text_image(layout, active_line, accent, width, height):
    """Return a full-frame RGBA PIL image with the card's text (active line accent, rest white)."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    fontsize = layout["fontsize"]
    font = ImageFont.truetype(FONT, fontsize)
    outline = layout["outline"]
    txt = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    td = ImageDraw.Draw(txt)
    for li, row in enumerate(layout["placed"]):
        fill = (accent if li == active_line else WHITE) + (255,)
        for (text, x, y) in row:
            td.text((x, y), text, font=font, fill=fill, stroke_width=outline, stroke_fill=(0, 0, 0, 255))
    blur = max(1, int(fontsize * 0.03)); off = max(1, int(fontsize * 0.04))
    sil = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sil.paste((0, 0, 0, 255), mask=txt.split()[3])
    sil = sil.filter(ImageFilter.GaussianBlur(blur))
    sh = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sh.paste(sil, (off, off), sil)
    sh.putalpha(sh.split()[3].point(lambda a: int(a * 0.45)))
    return Image.alpha_composite(sh, txt)


def load_emoji_frames(path, is_anim, es):
    """Return (frames, durations_ms). Animated GIF -> all frames; static PNG -> single frame."""
    from PIL import Image
    im = Image.open(path)
    frames, durs = [], []
    if is_anim:
        try:
            while True:
                frames.append(im.convert("RGBA").resize((es, es), Image.LANCZOS))
                durs.append(im.info.get("duration", 60) or 60)
                im.seek(im.tell() + 1)
        except EOFError:
            pass
    if not frames:
        frames = [im.convert("RGBA").resize((es, es), Image.LANCZOS)]
        durs = [1000]
    return frames, durs


def probe_fps(video):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=r_frame_rate", "-of", "default=noprint_wrappers=1:nokey=1", str(video)])
    num, den = r.stdout.strip().split("/")
    return float(num) / float(den)


def probe_duration(video):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(video)])
    return float(r.stdout.strip())


def scribe_transcribe(video, biased):
    import os
    from dotenv import load_dotenv
    load_dotenv()  # ensure .env keys are in os.environ before getenv checks
    if os.getenv("ELEVENLABS_API_KEY"):
        from elevenlabs_client import scribe_whisper_compat
        return scribe_whisper_compat(str(video), biased_keywords=biased, language_code="en")
    elif os.getenv("FAL_KEY"):
        from fal_client import scribe_whisper_compat as fal_scribe
        return fal_scribe(str(video), biased_keywords=biased, language_code="en")
    else:
        raise RuntimeError("Neither ELEVENLABS_API_KEY nor FAL_KEY set in .env")


TEXT_POP_DUR = 0.12      # text scale-pop on card appearance (measured: 96->105->100% over ~0.12s)
SLIDE_ENTER_DUR = 0.30   # slide traverse duration (FIXED — same speed every time, NOT card-relative).
                         # Ease-in-out over this, then HOLD at the destination for the rest of the card.
EMOJI_MIN_GAP = 0.4      # min sec between emoji placements (low throttle → more emojis; most keyword cards show one)
# (EMOJI_PRESETS + the slide/parked geometry live next to _emoji_offsets below)
# NOTE: the emoji is BOUND TO ITS TEXT CARD — it disappears the instant the caption advances to the
# next card (no cross-card linger). Submagic ties the emoji to the text segment; when the text moves
# on, the emoji goes. The fix for "disappears too quickly" was a FASTER entrance, not a longer linger.


def _smooth(p):
    p = max(0.0, min(1.0, p))
    return p * p * (3 - 2 * p)


def _text_scale(elapsed):
    """Subtle pop matching the reference: 96% -> 105% peak (~+0.04s) -> 100% (~0.12s)."""
    if elapsed >= TEXT_POP_DUR:
        return 1.0
    p = elapsed / TEXT_POP_DUR
    if p < 0.35:
        return 0.96 + (1.05 - 0.96) * (p / 0.35)          # 0.96 -> 1.05 (quick overshoot)
    return 1.05 + (1.0 - 1.05) * ((p - 0.35) / 0.65)      # 1.05 -> 1.0 (settle)


def _ease_out(p):
    """Smooth deceleration (not rigid)."""
    p = max(0.0, min(1.0, p))
    return 1 - (1 - p) ** 3


# Emoji motion — a SET of directional slides + one static, ALL sharing the SAME distance + speed
# mechanics (verified against the reference + user-approved directions from the arrow diagram):
#  - Each preset slides in a compass direction (the arrows): left/right, up/down, the 4 diagonals,
#    plus a STATIC that just stays put. Direction rotates per emoji for variety.
#  - HORIZONTAL travel = fixed "INSIDE" word-width (centered, ±h). VERTICAL travel is CAPPED to <1
#    line (v) so the emoji ALWAYS stays close to the text — never more than ~1 line away, and
#    sdy/rdy are >=0 so it never rises INTO the text (no blocking). "up" rests just below the text;
#    "down" rests ~1 line below.
#  - Motion is EASE-IN-OUT (accelerate then decelerate, like a car) over a FIXED duration
#    (SLIDE_ENTER_DUR — same speed every time, NOT card-relative), then HOLDS at the destination.
EMOJI_PRESETS = ["right", "up_right", "up", "up_left", "left", "down", "static", "down_right", "down_left"]


def _emoji_offsets(preset, h, v):
    """Direction preset -> (sdx, sdy, rdx, rdy) px offsets from the base (centered, just below text).
    h = horizontal half-travel (INSIDE width / 2); v = vertical travel (<1 line). sdy/rdy >= 0 so the
    emoji stays at/below the base and never rises into the text. Travel is ease-in-out then HELD."""
    P = {
        "right":      (-h, 0,  h, 0),     # left -> right (stays just below text)
        "left":       ( h, 0, -h, 0),     # right -> left
        "up":         ( 0, v,  0, 0),     # from ~1 line below, UP to just below text
        "down":       ( 0, 0,  0, v),     # from just below text, DOWN ~1 line
        "up_right":   (-h, v,  h, 0),     # shallow diagonal up-right (stays close to text)
        "up_left":    ( h, v, -h, 0),     # shallow diagonal up-left
        "down_right": (-h, 0,  h, v),     # shallow diagonal down-right
        "down_left":  ( h, 0, -h, v),     # shallow diagonal down-left
        "static":     ( 0, 0,  0, 0),     # no movement — just stays there
    }
    return P.get(preset, P["static"])


def _emoji_xform(elapsed, dur, sdx, sdy, rdx, rdy):
    """EASE-IN-OUT (accel then decel, like a car) over fixed `dur`, then HOLD at the destination.
    Same fixed-speed movement for every emoji (dur is constant, not card-relative)."""
    p = _smooth(elapsed / max(0.05, dur))         # smoothstep; _smooth clamps p to [0,1] then holds
    return int(sdx + (rdx - sdx) * p), int(sdy + (rdy - sdy) * p)


def _scale_about(img, factor, cx, cy):
    from PIL import Image
    if abs(factor - 1.0) < 0.01:
        return img
    W, H = img.size
    r = img.resize((max(1, int(W * factor)), max(1, int(H * factor))), Image.LANCZOS)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(r, (int(cx - cx * factor), int(cy - cy * factor)))
    return out


def find_boring_window(video, length=6.0, edge=4.0):
    """Return (start, end) of the calmest (lowest-motion) `length`-second window — the
    'most boring part' — avoiding the first/last `edge` seconds (hook / CTA)."""
    import tempfile
    import numpy as np
    from PIL import Image
    dur = probe_duration(video)
    if dur <= length + 2 * edge:
        s = max(0.0, (dur - length) / 2)
        return s, s + length
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        run(["ffmpeg", "-y", "-i", str(video), "-vf", "fps=2,scale=160:-1", "-q:v", "3", str(td / "f%04d.jpg")])
        files = sorted(td.glob("f*.jpg"))
        arrs = [np.asarray(Image.open(f).convert("L"), dtype=np.int16) for f in files]
    motion = [0.0] + [float(np.abs(arrs[i] - arrs[i - 1]).mean()) for i in range(1, len(arrs))]
    fps_s = 2
    win = int(length * fps_s)
    lo = int(edge * fps_s)
    hi = max(lo + 1, len(motion) - win - int(edge * fps_s))
    best = None
    for s in range(lo, hi):
        score = sum(motion[s:s + win])
        if best is None or score < best[0]:
            best = (score, s)
    start = best[1] / fps_s
    return start, start + length


def burn(video, cards, work_dir, out, fontsize_ratio, vertical_pos, use_emoji, max_lines=3,
         disc_text=None, disc_start=0.0, disc_end=0.0):
    """Pre-composite the whole caption track (text + animated emoji w/ motion) to a PNG
    sequence, then overlay it in ONE ffmpeg pass (fast regardless of card count)."""
    import shutil
    from PIL import Image, ImageFont, ImageDraw
    width, height = probe_size(video)
    fps = probe_fps(video)
    dur = probe_duration(video)
    # FIXED slide distance for EVERY emoji = width of the word "INSIDE" (I->E) at the standard font
    # size — same distance every time, NOT relative to the subtitle/word lengths. slide_half is half
    # of that (the traverse is centered on the middle: -half -> +half).
    _std_fs = _font_px(width, fontsize_ratio)
    _pf = ImageFont.truetype(FONT, _std_fs)
    _pb = ImageDraw.Draw(Image.new("RGBA", (10, 10))).textbbox((0, 0), "INSIDE", font=_pf,
                                                               stroke_width=max(2, int(_std_fs * 0.06)))
    slide_half = (_pb[2] - _pb[0]) / 2.0
    slide_v = int(_std_fs * 0.85)   # vertical travel for up/down/diagonal presets (<1 line → stays close to text)
    if vertical_pos is None:
        # Caption block center at ~0.70 — lower-third, well clear BELOW the chin even when she
        # leans/tilts (0.60/0.64 still caught the jaw on some clips), and high enough that the
        # caption + its 'down' emoji stay above the bottom disclaimer band (~0.88-1.0).
        vertical_pos = 0.70
    cy = int(vertical_pos * height)
    print(f"      vertical_pos={vertical_pos:.3f}  max_font={fontsize_ratio}  max_lines={max_lines}  fps={fps:.2f}", flush=True)

    disp_end = [cards[i + 1]["start"] for i in range(len(cards) - 1)] + [cards[-1]["end"] + 0.4]
    emoji_cache = {}
    cd = []          # text cards only
    emoji_raw = []   # emoji overlays (decoupled from cards, so they can linger)
    emoji_idx = 0
    last_emoji = None   # last PLACED glyph — never repeat it back-to-back
    for ci, card in enumerate(cards):
        accent = ACCENTS[ci % len(ACCENTS)]
        lay = compute_layout(card["words"], width, height, fontsize_ratio, vertical_pos, max_lines)
        cap = int(lay["fontsize"] * 0.72)
        d0, d1 = card["start"], disp_end[ci]
        bounds = [d0] + [lay["line_starts"][li] for li in range(1, lay["nlines"])] + [d1]
        line_imgs = [render_text_image(lay, li, accent, width, height) for li in range(lay["nlines"])]
        cd.append({"d0": d0, "d1": d1, "bounds": bounds, "lines": line_imgs})
        emoji = pick_emoji(card["words"], exclude=last_emoji) if use_emoji else None
        if emoji and (not emoji_raw or d0 - emoji_raw[-1]["start"] >= EMOJI_MIN_GAP):
            es = int(cap * 1.7); ex = (width - es) // 2; ey = lay["emoji_y"]
            key = (emoji, es)
            if key not in emoji_cache:
                emoji_cache[key] = render_emoji_frames(emoji, es)
            frames, durs = emoji_cache[key]
            if frames is not None:
                preset = EMOJI_PRESETS[emoji_idx % len(EMOJI_PRESETS)]; emoji_idx += 1
                sdx, sdy, rdx, rdy = _emoji_offsets(preset, slide_half, slide_v)
                # end = this card's d1 → emoji disappears the instant the text advances to the next card
                emoji_raw.append({"start": d0, "end": d1, "ex": ex, "ey": ey, "es": es,
                                  "frames": frames, "durs": durs, "glyph": emoji,
                                  "sdx": sdx, "sdy": sdy, "rdx": rdx, "rdy": rdy,
                                  "edur": SLIDE_ENTER_DUR})
                last_emoji = emoji   # block this glyph from repeating on the next placement

    print(f"      {len(emoji_raw)} emojis placed across {len(cards)} cards: "
          f"{''.join(e['glyph'] for e in emoji_raw)}", flush=True)
    disc_img = None
    if disc_text:
        dp = work_dir / "disc.png"
        render_disclaimer(disc_text, width, height, find_font(), dp, fontsize_ratio=0.013, vertical_pos=0.99)
        disc_img = Image.open(dp).convert("RGBA")
        print(f"      disclaimer ON {disc_start:.1f}-{disc_end:.1f}s (calmest window)", flush=True)

    frames_dir = work_dir / "cap"
    frames_dir.mkdir(exist_ok=True)
    blank = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    nframes = int(dur * fps) + 2
    prev_key = prev_path = None
    for f in range(nframes):
        t = f / fps
        disc_on = disc_img is not None and disc_start <= t < disc_end
        active = next((c for c in cd if c["d0"] <= t < c["d1"]), None)
        aem = next((e for e in emoji_raw if e["start"] <= t < e["end"]), None)
        li = None; tscale = 1.0
        if active is not None:
            el = t - active["d0"]
            li = max((i for i in range(len(active["bounds"]) - 1) if active["bounds"][i] <= t), default=0)
            tscale = _text_scale(el)
        efi = None; escale = 1.0; edx = edy = 0
        if aem is not None:
            eel = t - aem["start"]
            if len(aem["frames"]) == 1:
                efi = 0
            else:
                tot = sum(aem["durs"]); tt = (eel * 1000.0) % tot; acc = 0
                for k, dms in enumerate(aem["durs"]):
                    acc += dms
                    if tt < acc:
                        efi = k; break
                if efi is None:
                    efi = len(aem["frames"]) - 1
            edx, edy = _emoji_xform(eel, aem["edur"], aem["sdx"], aem["sdy"], aem["rdx"], aem["rdy"])
        if active is None and aem is None and not disc_on:
            key = ("blank",)
        else:
            key = (id(active) if active else 0, li, round(tscale, 2),
                   id(aem) if aem else 0, efi, round(escale, 2), edx, edy, disc_on)
        path = frames_dir / f"{f:05d}.png"
        if key == prev_key and prev_path is not None:
            shutil.copy(prev_path, path)
        else:
            img = disc_img.copy() if disc_on else blank.copy()
            if active is not None:
                txt = _scale_about(active["lines"][li], tscale, width // 2, cy) if tscale != 1.0 else active["lines"][li]
                img = Image.alpha_composite(img, txt)
            if aem is not None and efi is not None:
                em = aem["frames"][efi]
                if escale < 0.999:
                    ns = max(2, int(aem["es"] * escale))
                    em = em.resize((ns, ns), Image.LANCZOS)
                    ox = aem["ex"] + (aem["es"] - ns) // 2 + edx
                    oy = aem["ey"] + (aem["es"] - ns) // 2 + edy
                else:
                    ox, oy = aem["ex"] + edx, aem["ey"] + edy
                img.alpha_composite(em, (ox, oy))
            img.save(path, compress_level=1)
            prev_key = key; prev_path = path

    cmd = ["ffmpeg", "-y", "-i", str(video), "-framerate", f"{fps:.5f}", "-i", str(frames_dir / "%05d.png"),
           "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto[out]", "-map", "[out]", "-map", "0:a",
           "-c:a", "copy", "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-pix_fmt", "yuv420p", str(out)]
    r = run(cmd)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg overlay failed:\n{r.stderr[-3000:]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", default=None)
    ap.add_argument("--font-ratio", type=float, default=0.0336,
                    help="Font as fraction of frame height. 0.0336 matches Submagic ref (a ~2-word line is ~42%% of width). Shrinks only if a line/card overflows.")
    ap.add_argument("--vertical-pos", type=float, default=None)
    ap.add_argument("--max-words", type=int, default=3)
    ap.add_argument("--max-lines", type=int, default=3)
    ap.add_argument("--no-emoji", action="store_true")
    ap.add_argument("--biased", default="Chowchilla:3.0,CCWF:2.0",
                    help="comma-sep Scribe biased keywords (proper nouns). Empty for generic text.")
    ap.add_argument("--disclaimer", action="store_true",
                    help="overlay the legal disclaimer at the bottom during the calmest (most boring) window.")
    ap.add_argument("--disclaimer-text", default=DEFAULT_DISCLAIMER)
    ap.add_argument("--disclaimer-secs", type=float, default=6.0, help="how long the disclaimer stays up.")
    ap.add_argument("--disclaimer-start", type=float, default=None,
                    help="force disclaimer start (sec). Default: auto-detect calmest window.")
    ap.add_argument("--end", type=float, default=None)
    args = ap.parse_args()

    video = Path(args.video).resolve()
    if not video.exists():
        sys.exit(f"not found: {video}")
    out = Path(args.out).resolve() if args.out else video.with_name(video.stem + "_hormozi3.mp4")
    width, height = probe_size(video)
    print(f"video: {video.name}  {width}x{height}", flush=True)
    biased = [b.strip() for b in args.biased.split(",") if b.strip()]

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        print("[1/4] extract audio", flush=True)
        extract_audio(video, td / "a.wav")
        print("[2/4] Scribe transcribe", flush=True)
        result = scribe_transcribe(video, biased)
        # drop conversational filler tokens so they never get captioned ("yeah", "mm-hmm", "uh"...)
        import re as _re
        _FILLERS = {"mmhmm", "mhm", "mmm", "hmm", "uh", "um", "umm", "uhh", "uhhuh", "yeah", "yea"}
        for _seg in result.get("segments", []):
            _seg["words"] = [w for w in _seg.get("words", [])
                             if _re.sub(r"[^a-z]", "", w.get("word", "").lower()) not in _FILLERS]
        print("[3/4] chunking", flush=True)
        cards = chunk_words(result["segments"], max_words=args.max_words)
        if args.end is not None:
            cards = [c for c in cards if c["start"] < args.end]
        print(f"      {len(cards)} cards, {sum(len(c['words']) for c in cards)} words", flush=True)
        disc_text = disc_start = disc_end = None
        if args.disclaimer:
            if args.disclaimer_start is not None:
                disc_start = args.disclaimer_start
            else:
                disc_start, _ = find_boring_window(video, length=args.disclaimer_secs)
            disc_end = disc_start + args.disclaimer_secs
            disc_text = args.disclaimer_text
        print("[4/4] render + burn", flush=True)
        burn(video, cards, td, out, args.font_ratio, args.vertical_pos,
             use_emoji=not args.no_emoji, max_lines=args.max_lines,
             disc_text=disc_text, disc_start=disc_start or 0.0, disc_end=disc_end or 0.0)
    print(f"\nDONE → {out}", flush=True)


if __name__ == "__main__":
    main()
