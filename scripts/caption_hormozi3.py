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

# keyword -> emoji. Prefer SINGLE-codepoint emojis (Noto has animated GIFs for these;
# ZWJ sequences / flags are not animated). first match per card wins.
KEYWORD_EMOJI = {
    "mama": "❤️", "mom": "❤️", "mother": "❤️", "daughter": "❤️", "sister": "❤️", "love": "❤️",
    "california": "🔒", "prison": "🔒", "prisons": "🔒", "locked": "🔒", "jail": "🔒",
    "guards": "🚨", "guard": "🚨", "police": "🚨",
    "years": "⏳", "year": "⏳", "late": "⏳", "time": "⏳", "minutes": "⏱️", "minute": "⏱️",
    "wrong": "❌", "never": "🚫", "nobody": "🚫", "nothing": "🚫", "don't": "🚫",
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
    "remember": "💭", "thought": "💭", "knew": "💭", "think": "💭",
    "fire": "🔥", "amazing": "🔥", "fight": "🔥",
}
NOTO_GIF = "https://fonts.gstatic.com/s/e/notoemoji/latest/{code}/512.gif"
TWEMOJI_PNG = "https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.0.3/assets/72x72/{tcode}.png"


def _codes(e):
    cps = [c for c in e if c != "️"]  # drop VS16
    return "_".join(f"{ord(c):x}" for c in cps), "-".join(f"{ord(c):x}" for c in cps)


def fetch_emoji(e):
    """Return (path, is_animated). Tries Noto animated GIF first, falls back to Twemoji PNG."""
    ncode, tcode = _codes(e)
    gif = EMOJI_DIR / f"{ncode}.gif"
    if gif.exists() and gif.stat().st_size > 2000:
        return gif, True
    try:
        urllib.request.urlretrieve(NOTO_GIF.format(code=ncode), gif)
        if gif.stat().st_size > 2000:
            return gif, True
        gif.unlink(missing_ok=True)
    except Exception:
        pass
    png = EMOJI_DIR / f"{tcode}.png"
    if png.exists() and png.stat().st_size > 200:
        return png, False
    try:
        urllib.request.urlretrieve(TWEMOJI_PNG.format(tcode=tcode), png)
        if png.stat().st_size > 200:
            return png, False
    except Exception as ex:
        print(f"      [emoji] {e} unavailable: {ex}", flush=True)
    return None, False


def pick_emoji(words):
    for w in words:
        key = "".join(c for c in w["text"].lower() if c.isalpha() or c == "'")
        if key in KEYWORD_EMOJI:
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
    fontsize = max(16, int(height * fontsize_ratio))  # ~FIXED size (Submagic ref ~0.035)
    floor = max(16, int(height * 0.028))

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
            "line_starts": line_starts, "y0": y0, "text_h": text_h,
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
    from elevenlabs_client import scribe_whisper_compat
    return scribe_whisper_compat(str(video), biased_keywords=biased, language_code="en")


TEXT_POP_DUR = 0.12      # text scale-pop on card appearance (measured: 96->105->100% over ~0.12s)
EMOJI_ENTER_DUR = 0.40   # emoji entrance (slide-across needs time to read)
EMOJI_PRESETS = ["slide_left", "slide_right", "slide_up", "pop"]  # favor the across-slide


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


def _emoji_xform(preset, elapsed, es, width):
    """Entrance motion, holding after EMOJI_ENTER_DUR.
      slide_left/right : emoji SLIDES ACROSS the subtitle (travels ~the caption width) into
                         its center resting spot — the signature Hormozi emoji move.
      slide_up         : rises up from below into place.
      pop              : quick scale 0->1.
    Internal Noto-GIF animation plays on top throughout."""
    if elapsed >= EMOJI_ENTER_DUR:
        return 0, 0, 1.0
    p = _smooth(elapsed / EMOJI_ENTER_DUR)
    cross = int(width * 0.42)   # slide-across distance ~ subtitle width
    if preset == "slide_left":
        return int((1 - p) * -cross), 0, 1.0    # from left edge -> center
    if preset == "slide_right":
        return int((1 - p) * cross), 0, 1.0      # from right edge -> center
    if preset == "slide_up":
        return 0, int((1 - p) * es * 1.1), 1.0
    return 0, 0, max(0.15, p)  # "pop": scale 0->1


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
    from PIL import Image
    width, height = probe_size(video)
    fps = probe_fps(video)
    dur = probe_duration(video)
    if vertical_pos is None:
        vertical_pos = max(0.68, auto_vertical_pos(width, height) - 0.02)
    cy = int(vertical_pos * height)
    print(f"      vertical_pos={vertical_pos:.3f}  max_font={fontsize_ratio}  max_lines={max_lines}  fps={fps:.2f}", flush=True)

    disp_end = [cards[i + 1]["start"] for i in range(len(cards) - 1)] + [cards[-1]["end"] + 0.4]
    emoji_cache = {}
    cd = []
    emoji_idx = 0
    for ci, card in enumerate(cards):
        accent = ACCENTS[ci % len(ACCENTS)]
        lay = compute_layout(card["words"], width, height, fontsize_ratio, vertical_pos, max_lines)
        cap = int(lay["fontsize"] * 0.72)
        d0, d1 = card["start"], disp_end[ci]
        bounds = [d0] + [lay["line_starts"][li] for li in range(1, lay["nlines"])] + [d1]
        line_imgs = [render_text_image(lay, li, accent, width, height) for li in range(lay["nlines"])]
        emoji = pick_emoji(card["words"]) if use_emoji else None
        frames = durs = None; ex = ey = es = 0; preset = "pop"
        if emoji:
            path, is_anim = fetch_emoji(emoji)
            if path:
                es = int(cap * 1.6); ex = (width - es) // 2; ey = lay["emoji_y"]
                key = (str(path), es)
                if key not in emoji_cache:
                    emoji_cache[key] = load_emoji_frames(path, is_anim, es)
                frames, durs = emoji_cache[key]
                preset = EMOJI_PRESETS[emoji_idx % len(EMOJI_PRESETS)]; emoji_idx += 1
        cd.append({"d0": d0, "d1": d1, "bounds": bounds, "lines": line_imgs, "es": es,
                   "ex": ex, "ey": ey, "frames": frames, "durs": durs, "preset": preset})

    # disclaimer overlay (bottom of frame, hard-cut window) — rendered once, composited under captions
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
        if active is None:
            key = ("disc",) if disc_on else ("blank",)
            efi = None
        else:
            el = t - active["d0"]
            li = max((i for i in range(len(active["bounds"]) - 1) if active["bounds"][i] <= t), default=0)
            tscale = _text_scale(el)
            efi = None; escale = 1.0; edx = edy = 0
            if active["frames"]:
                if len(active["frames"]) == 1:
                    efi = 0
                else:
                    tot = sum(active["durs"]); tt = (el * 1000.0) % tot; acc = 0
                    for k, dms in enumerate(active["durs"]):
                        acc += dms
                        if tt < acc:
                            efi = k; break
                    if efi is None:
                        efi = len(active["frames"]) - 1
                edx, edy, escale = _emoji_xform(active["preset"], el, active["es"], width)
            key = (id(active), li, efi, round(tscale, 2), round(escale, 2), edx, edy, disc_on)
        path = frames_dir / f"{f:05d}.png"
        if key == prev_key and prev_path is not None:
            shutil.copy(prev_path, path)
        else:
            if active is None:
                (disc_img if disc_on else blank).save(path, compress_level=1)
            else:
                img = _scale_about(active["lines"][li], tscale, width // 2, cy).copy() \
                    if tscale != 1.0 else active["lines"][li].copy()
                if active["frames"] is not None and efi is not None:
                    em = active["frames"][efi]
                    if escale < 0.999:
                        ns = max(2, int(active["es"] * escale))
                        em = em.resize((ns, ns), Image.LANCZOS)
                        ox = active["ex"] + (active["es"] - ns) // 2 + edx
                        oy = active["ey"] + (active["es"] - ns) // 2 + edy
                    else:
                        ox, oy = active["ex"] + edx, active["ey"] + edy
                    img.alpha_composite(em, (ox, oy))
                if disc_on:
                    img = Image.alpha_composite(disc_img, img)  # disclaimer under captions
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
