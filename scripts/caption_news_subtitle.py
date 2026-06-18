#!/usr/bin/env python3
"""Burn compact broadcast-style subtitles above a lower-third news bar.

This is intentionally calmer than creator captions: no emoji, no pop, no
per-word highlight. It uses ElevenLabs Scribe timestamps and renders compact
BBC-like white Helvetica text inside a centered black rectangular block.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from caption_hormozi3 import scribe_transcribe, probe_fps, probe_duration
from caption_styled import probe_size


FONT_PATH = "/System/Library/Fonts/HelveticaNeue.ttc"
FONT_INDEX = 1  # Helvetica Neue Bold
TEXT_RGB = (255, 255, 255)
BOX_RGB = (0, 0, 0)
BBC_BOX_OPACITY = 0.90


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def clean_word(w):
    text = (w.get("word") or w.get("text") or "").strip()
    return text.strip()


def build_cards(segments, max_words=7, min_pause=0.36):
    words = []
    for sg in segments:
        for w in sg.get("words", []):
            text = clean_word(w)
            if text:
                words.append({"text": text, "start": w["start"], "end": w["end"]})

    cards, cur = [], []
    for w in words:
        pause = cur and (w["start"] - cur[-1]["end"] > min_pause)
        sentence_end = cur and cur[-1]["text"].rstrip().endswith((".", "?", "!"))
        if cur and (len(cur) >= max_words or pause or sentence_end):
            cards.append(cur)
            cur = []
        cur.append(w)
    if cur:
        cards.append(cur)
    return [{"words": c, "start": c[0]["start"], "end": c[-1]["end"]} for c in cards]


def font(px, font_index=FONT_INDEX):
    return ImageFont.truetype(FONT_PATH, px, index=font_index)


def text_w(draw, text, fnt, stroke):
    b = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
    return b[2] - b[0]


def wrap_lines(text, draw, fnt, max_width, stroke):
    words = text.split()
    if not words:
        return [""]
    best = None
    for split in range(1, len(words) + 1):
        lines = [" ".join(words[:split]), " ".join(words[split:]) if split < len(words) else ""]
        lines = [ln for ln in lines if ln]
        if len(lines) > 2:
            continue
        widths = [text_w(draw, ln, fnt, stroke) for ln in lines]
        if max(widths) <= max_width:
            score = (len(lines), max(widths), abs((widths[0] if widths else 0) - (widths[-1] if widths else 0)))
            if best is None or score < best[0]:
                best = (score, lines)
    if best:
        return best[1]

    # Fallback: greedy two-line wrap, shrinking is handled by caller.
    line1, line2 = [], []
    for word in words:
        target = line1 if text_w(draw, " ".join(line1 + [word]), fnt, stroke) <= max_width else line2
        target.append(word)
    return [" ".join(line1), " ".join(line2)]


def render_card(text, width, height, fnt, cy, max_width_ratio, horizontal_pos, style, font_index=FONT_INDEX):
    if style == "bbc-box":
        # Backward-compatible alias for the old test name; the approved style is "bbc".
        style = "bbc"
    if style == "youtube":
        stroke = max(3, int(fnt.size * 0.10))
    elif style == "youtube-box":
        stroke = max(2, int(fnt.size * 0.07))
    else:
        stroke = 0
    max_width = int(width * max_width_ratio)
    probe = ImageDraw.Draw(Image.new("RGBA", (4, 4)))

    cf = fnt
    lines = wrap_lines(text, probe, cf, max_width, stroke)
    while cf.size > 22 and any(text_w(probe, ln, cf, stroke) > max_width for ln in lines):
        cf = font(cf.size - 2, font_index)
        stroke = max(2, int(cf.size * 0.075))
        lines = wrap_lines(text, probe, cf, max_width, stroke)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ascent, descent = cf.getmetrics()
    line_h = int((ascent + descent) * (0.90 if style == "bbc" else 0.84))
    pad_x = int(cf.size * (0.36 if style == "bbc" else 0.42))
    pad_y = int(cf.size * (0.16 if style == "bbc" else 0.16))
    line_widths = [text_w(d, ln, cf, stroke) for ln in lines]
    box_w = min(width - 42, max(line_widths) + pad_x * 2)
    box_h = len(lines) * line_h + pad_y * 2
    if style == "bbc-left":
        x0 = int(width * horizontal_pos)
        x0 = min(max(18, x0), width - box_w - 18)
    else:
        x0 = (width - box_w) // 2
    y0 = int(cy - box_h / 2)

    if style != "youtube":
        shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rectangle((x0 + 3, y0 + 3, x0 + box_w + 3, y0 + box_h + 3), fill=(0, 0, 0, 120))
        shadow = shadow.filter(ImageFilter.GaussianBlur(3))
        img.alpha_composite(shadow)
        opacity = 0.68 if style == "youtube-box" else BBC_BOX_OPACITY
        d.rectangle((x0, y0, x0 + box_w, y0 + box_h), fill=(*BOX_RGB, int(255 * opacity)))

    y = y0 + pad_y
    for ln in lines:
        b = d.textbbox((0, 0), ln, font=cf, stroke_width=stroke)
        if style == "bbc-left":
            x = x0 + pad_x
        else:
            tw = b[2] - b[0]
            x = (width - tw) // 2
        d.text((x, y - b[1]), ln, font=cf, fill=(*TEXT_RGB, 255),
               stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
        y += line_h
    return img


def burn(video, cards, work_dir, out, vertical_pos=0.595, font_ratio=0.034,
         max_width_ratio=0.76, horizontal_pos=0.10, style="youtube", font_index=FONT_INDEX):
    width, height = probe_size(video)
    fps = probe_fps(video)
    dur = probe_duration(video)
    fnt = font(max(24, int(height * font_ratio)), font_index)
    cy = int(height * vertical_pos)
    print(f"      news-sub: font={fnt.size}px vpos={vertical_pos:.3f} cards={len(cards)} fps={fps:.2f}", flush=True)

    disp_end = [cards[i + 1]["start"] for i in range(len(cards) - 1)] + [cards[-1]["end"] + 0.20]
    rendered = []
    for i, card in enumerate(cards):
        text = " ".join(w["text"] for w in card["words"]).strip()
        rendered.append({
            "start": card["start"],
            "end": disp_end[i],
            "img": render_card(text, width, height, fnt, cy, max_width_ratio, horizontal_pos, style, font_index),
        })

    frames_dir = work_dir / "news_sub_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    blank = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    nframes = int(dur * fps) + 2
    prev_key = prev_path = None
    for frame in range(nframes):
        t = frame / fps
        active = next((item for item in rendered if item["start"] <= t < item["end"]), None)
        key = ("blank",) if active is None else (id(active),)
        path = frames_dir / f"{frame:05d}.png"
        if key == prev_key and prev_path is not None:
            shutil.copy(prev_path, path)
        else:
            (blank if active is None else active["img"]).save(path, compress_level=1)
            prev_key, prev_path = key, path

    cmd = [
        "ffmpeg", "-y", "-i", str(video),
        "-framerate", f"{fps:.5f}", "-i", str(frames_dir / "%05d.png"),
        "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto[out]",
        "-map", "[out]", "-map", "0:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-pix_fmt", "yuv420p", "-c:a", "copy", str(out),
    ]
    r = run(cmd)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg overlay failed:\n{r.stderr[-3000:]}")


def main():
    ap = argparse.ArgumentParser(description="Burn broadcast-style subtitles above a news lower-third.")
    ap.add_argument("video")
    ap.add_argument("--out", default=None)
    ap.add_argument("--vertical-pos", type=float, default=0.595)
    ap.add_argument("--horizontal-pos", type=float, default=0.10)
    ap.add_argument("--font-ratio", type=float, default=0.034)
    ap.add_argument("--max-width-ratio", type=float, default=0.76)
    ap.add_argument("--max-words", type=int, default=7)
    ap.add_argument("--min-pause", type=float, default=0.36)
    ap.add_argument("--style", choices=["youtube", "youtube-box", "bbc", "bbc-box", "bbc-left"], default="youtube")
    ap.add_argument("--font-index", type=int, default=FONT_INDEX,
                    help="HelveticaNeue.ttc index. 0=Regular, 1=Bold, 10=Medium.")
    ap.add_argument("--biased", default="Los Padrinos:3.0,Barry J. Nidorf:3.0,Barry Nidorf:2.5,juvenile hall:2.5,L.A. County:2.5,California:2.0")
    args = ap.parse_args()

    video = Path(args.video)
    out = Path(args.out) if args.out else video.with_name(video.stem + "_newssub.mp4")
    work = video.with_name(video.stem + "_newssubwork")
    work.mkdir(exist_ok=True)
    biased = [b.strip() for b in args.biased.split(",") if b.strip()] if args.biased else None

    transcript_path = work / "scribe.json"
    if transcript_path.exists():
        print("[1/2] Scribe transcribe (cached)", flush=True)
        result = json.loads(transcript_path.read_text())
    else:
        print("[1/2] Scribe transcribe", flush=True)
        result = scribe_transcribe(video, biased)
        transcript_path.write_text(json.dumps(result, indent=2))
    cards = build_cards(result.get("segments", []), max_words=args.max_words, min_pause=args.min_pause)
    print(f"      {len(cards)} cards", flush=True)
    print("[2/2] render news subtitles", flush=True)
    burn(video, cards, work, out, args.vertical_pos, args.font_ratio,
         args.max_width_ratio, args.horizontal_pos, args.style, args.font_index)
    print(f"DONE -> {out}", flush=True)


if __name__ == "__main__":
    main()
