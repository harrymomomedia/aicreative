"""Internal clone of Submagic's "Nick" caption template (reverse-engineered frame-by-frame from
story_C_aftermath_final_submagic_nick.mp4, 2026-06-04). Unlike the Submagic API, this uses OUR
verbatim transcript (Scribe) and gives full position/size control.

The Nick look (measured via diff-vs-master):
  - sentence-case (preserve original case — NOT all-caps)
  - white bold sans-serif (Helvetica Neue Bold) on a SEMI-TRANSPARENT DARK ROUNDED BOX
      box fill ~rgb(45,45,42) @ ~0.58 opacity, corner radius ~0.18*box_h
  - ~2 words per card, single centered line, lower-third (vertical center ~0.754 of frame H)
  - glyph cap-height ~0.031*H (font px ~0.044*H); box height ~0.06*H
  - subtle scale-pop on card appearance (~0.94 -> 1.0 over ~0.12s)
  - NO color accent, NO emoji (that's the Hormozi-3 look — use caption_hormozi3.py for that)

Disclaimer is a separate layer — run scripts/burn_disclaimer.py on the output for the combo
(same as the Submagic flow).

  .venv/bin/python scripts/caption_nick.py <in.mp4> --out <out.mp4>
  .venv/bin/python scripts/caption_nick.py <in.mp4> --out <out.mp4> --font arial --biased ""
"""
import argparse
import shutil
import subprocess
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image, ImageFont, ImageDraw
from caption_hormozi3 import scribe_transcribe, probe_fps, probe_duration
from caption_styled import probe_size


def build_cards_nick(segments, max_words=2, min_pause=0.35):
    """Chunk raw Scribe words into ~max_words cards, PRESERVING original case (sentence-case is the
    Nick look — NOT all-caps like Hormozi 3)."""
    words = []
    for sg in segments:
        for w in sg.get("words", []):
            raw = (w.get("word") or w.get("text", "")).strip()
            # strip sentence punctuation (verified vs the real Submagic Nick export 2026-06-10:
            # it drops ALL .,!?;:" even at sentence ends — keeps internal apostrophes) but REMEMBER
            # sentence-final punctuation so cards never straddle a sentence boundary.
            txt = raw.strip('.,!?;:"')
            if txt:
                words.append({"text": txt, "start": w["start"], "end": w["end"],
                              "eos": raw.rstrip('"').endswith((".", "?", "!"))})
    cards, cur = [], []
    for w in words:
        if cur and (len(cur) >= max_words or w["start"] - cur[-1]["end"] > min_pause
                    or cur[-1].get("eos")):
            cards.append(cur); cur = []
        cur.append(w)
    if cur:
        cards.append(cur)
    return [{"words": c, "start": c[0]["start"], "end": c[-1]["end"]} for c in cards]

# ---- measured Nick parameters ----
FONTS = {
    "helvetica": ("/System/Library/Fonts/HelveticaNeue.ttc", 1),   # Helvetica Neue Bold
    "arial":     ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", None),
}
TEXT_RGB = (248, 248, 247)
BOX_RGB = (45, 45, 42)
BOX_OPACITY = 0.58
FONT_RATIO = 0.044         # font px / frame height  (cap-height ~0.031*H)
VPOS = 0.754               # box CENTER as fraction of frame height
PAD_X = 0.32               # horizontal box padding as fraction of font px
PAD_Y = 0.14               # vertical box padding as fraction of font px
RADIUS = 0.20              # corner radius as fraction of box height
POP_DUR = 0.12             # scale-pop on appearance
POP_START = 0.94


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def _font(name, px):
    path, idx = FONTS[name]
    return ImageFont.truetype(path, px, index=idx) if idx is not None else ImageFont.truetype(path, px)


def _pop(elapsed):
    if elapsed >= POP_DUR:
        return 1.0
    p = elapsed / POP_DUR
    return POP_START + (1.0 - POP_START) * (1 - (1 - p) ** 2)   # ease-out


def render_card(text, font, width, height, cy):
    """Full-frame transparent RGBA with the dark rounded box + white centered text."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ascent, descent = font.getmetrics()
    tw = d.textlength(text, font=font)
    px = font.size
    pad_x, pad_y = int(px * PAD_X), int(px * PAD_Y)
    box_w = int(tw) + 2 * pad_x
    box_h = ascent + descent + 2 * pad_y
    bx0 = (width - box_w) // 2
    by0 = cy - box_h // 2
    rad = int(box_h * RADIUS)
    d.rounded_rectangle([bx0, by0, bx0 + box_w, by0 + box_h], radius=rad,
                        fill=(*BOX_RGB, int(255 * BOX_OPACITY)))
    # text centered in the box (anchor mm = middle/middle of the text bbox)
    d.text((width // 2, by0 + box_h // 2), text, font=font, fill=(*TEXT_RGB, 255), anchor="mm")
    return img, (bx0, by0, box_w, box_h)


def _scale_about(img, factor, cx, cy):
    """Scale `img` by `factor` keeping the point (cx, cy) fixed."""
    if abs(factor - 1.0) < 0.005:
        return img
    w, h = img.size
    nw, nh = max(1, int(w * factor)), max(1, int(h * factor))
    s = img.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(s, (int(cx - nw * (cx / w)), int(cy - nh * (cy / h))))
    return out


def burn(video, cards, work_dir, out, font_name, font_ratio, vpos, end=None):
    width, height = probe_size(video)
    fps = probe_fps(video)
    dur = probe_duration(video) if end is None else min(end, probe_duration(video))
    px = max(12, int(font_ratio * height))
    font = _font(font_name, px)
    cy = int(vpos * height)
    print(f"      nick: font={font_name} {px}px  vpos={vpos:.3f}  cards={len(cards)}  fps={fps:.2f}", flush=True)

    # pre-render each card's static image once
    disp_end = [cards[i + 1]["start"] for i in range(len(cards) - 1)] + [cards[-1]["end"] + 0.3]
    cd = []
    for ci, card in enumerate(cards):
        text = " ".join((w.get("word") or w.get("text", "")).strip() for w in card["words"]).strip()
        # auto-shrink if a card would overflow the frame width
        cf = font
        while ImageDraw.Draw(Image.new("RGBA", (4, 4))).textlength(text, font=cf) > width * 0.90 and cf.size > 14:
            cf = _font(font_name, cf.size - 2)
        img, _ = render_card(text, cf, width, height, cy)
        cd.append({"d0": card["start"], "d1": disp_end[ci], "img": img})

    frames_dir = work_dir / "cap"
    frames_dir.mkdir(parents=True, exist_ok=True)
    blank = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    nframes = int(dur * fps) + 2
    prev_key = prev_path = None
    for f in range(nframes):
        t = f / fps
        active = next((c for c in cd if c["d0"] <= t < c["d1"]), None)
        scale = 1.0
        if active is not None:
            scale = _pop(t - active["d0"])
        key = ("blank",) if active is None else (id(active), round(scale, 2))
        path = frames_dir / f"{f:05d}.png"
        if key == prev_key and prev_path is not None:
            shutil.copy(prev_path, path)
        else:
            if active is None:
                img = blank
            elif scale != 1.0:
                img = _scale_about(active["img"], scale, width // 2, cy)
            else:
                img = active["img"]
            img.save(path, compress_level=1)
            prev_key, prev_path = key, path

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
    ap.add_argument("--font", choices=list(FONTS), default="helvetica")
    ap.add_argument("--font-ratio", type=float, default=FONT_RATIO)
    ap.add_argument("--vertical-pos", type=float, default=VPOS)
    ap.add_argument("--max-words", type=int, default=2)
    ap.add_argument("--min-pause", type=float, default=0.35)
    ap.add_argument("--biased", default="Chowchilla:3.0,CCWF:2.0,Chino:2.0")
    ap.add_argument("--end", type=float, default=None)
    args = ap.parse_args()

    video = Path(args.video)
    out = Path(args.out) if args.out else video.with_name(video.stem + "_nick.mp4")
    work = video.with_name(video.stem + "_nickwork")
    work.mkdir(exist_ok=True)
    biased = [b.strip() for b in args.biased.split(",") if b.strip()] if args.biased else None

    print("[1/2] Scribe transcribe", flush=True)
    result = scribe_transcribe(video, biased)
    cards = build_cards_nick(result.get("segments", []), max_words=args.max_words, min_pause=args.min_pause)
    print(f"      {len(cards)} cards", flush=True)
    print("[2/2] render Nick captions", flush=True)
    burn(video, cards, work, out, args.font, args.font_ratio, args.vertical_pos, end=args.end)
    print(f"DONE -> {out}", flush=True)


if __name__ == "__main__":
    main()
