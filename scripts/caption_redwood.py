"""REDWOOD — internal clone of the pink-karaoke caption style (reverse-engineered from
ad-1926019294732556.mp4, 2026-07-15). ALL-CAPS Anton, white fill + black stroke + soft shadow,
ONE keyword per card boxed in hot pink (rounded rect), single centered line ~55% of frame height.

Measured spec (720x1280 reference):
  - font: Anton (ultra-bold condensed), ALL-CAPS, punctuation KEPT (periods/commas render)
  - cap-height ~0.039*H -> Anton px ~0.054*H
  - white text, black stroke ~0.08*px, soft black shadow offset ~0.045*px
  - highlight: hot pink rounded box rgb(219,18,86) behind ONE word per card (some cards none),
    pad_x ~0.16*px, pad_y ~0.10*px, radius ~0.22*box_h; white text stays on top
  - 2-5 words per card, single line, center anchored at vpos ~0.55
  - subtle scale-pop on card appearance

Disclaimer is a separate layer — run scripts/burn_disclaimer.py on the output for the combo.

  .venv/bin/python scripts/caption_redwood.py <in.mp4> --out <out.mp4>
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

FONT_PATH = str(Path(__file__).resolve().parent.parent / "assets/fonts/Anton-Regular.ttf")
TEXT_RGB = (255, 255, 255)
PINK_RGB = (219, 18, 86)
REF_ASPECT = 16 / 9
FONT_RATIO = 0.0336         # WIDTH-anchored, the Hormozi guideline: px = width * 16/9 * ratio
VPOS = 0.55                 # text line CENTER as fraction of frame height
STROKE = 0.08               # black stroke width as fraction of font px
SHADOW = 0.045              # shadow offset as fraction of font px
MARGIN = 0.10               # visible pink margin beyond the stroked glyph edge (all sides)
TRACKING = 0.055            # extra letter-spacing as fraction of font px (ref has airier caps)
RADIUS = 0.22               # corner radius as fraction of box height
POP_DUR = 0.10
POP_START = 0.95
STOPWORDS = {"the","a","an","and","or","but","of","to","in","on","at","for","with","was","is",
             "are","were","be","been","i","you","he","she","it","we","they","my","your","his",
             "her","its","our","their","this","that","so","not","no","if","as","by","me","him"}


def build_cards(segments, max_words=4, min_pause=0.35):
    """Chunk Scribe words into cards. KEEP punctuation (ref shows NEEDY. / THEM. / AMAZING,)."""
    words = []
    for sg in segments:
        for w in sg.get("words", []):
            raw = (w.get("word") or w.get("text", "")).strip()
            if raw:
                words.append({"text": raw, "start": w["start"], "end": w["end"],
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


def pick_keyword(tokens):
    """Index of the ONE word to pink-box: longest content word (>=5 chars); else none (-1)."""
    best, best_len = -1, 4
    for i, t in enumerate(tokens):
        bare = "".join(ch for ch in t if ch.isalnum())
        if bare.lower() in STOPWORDS:
            continue
        if len(bare) > best_len:
            best, best_len = i, len(bare)
    return best


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def _pop(elapsed):
    if elapsed >= POP_DUR:
        return 1.0
    p = elapsed / POP_DUR
    return POP_START + (1.0 - POP_START) * (1 - (1 - p) ** 2)


def render_card(tokens, font, width, height, cy, hi_idx=None):
    """Transparent full-frame RGBA. Words drawn at EXPLICIT cursor positions (one coordinate
    system for text AND box, so the pink slab aligns exactly under the spoken word)."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    px = font.size
    stroke = max(2, int(px * STROKE))
    shadow = max(2, int(px * SHADOW))
    track = px * TRACKING
    space_adv = d.textlength(" ", font=font) + track
    def _adv(t):
        return sum(d.textlength(ch, font=font) for ch in t) + track * max(0, len(t) - 1)
    advs = [_adv(t) for t in tokens]
    total_w = sum(advs) + space_adv * (len(tokens) - 1)
    x0 = (width - total_w) / 2
    xs = []
    cur = x0
    for a in advs:
        xs.append(cur)
        cur += a + space_adv
    cap_h = int(px * 0.72)                  # Anton cap height
    baseline = cy + cap_h // 2              # caps band centered on cy

    if hi_idx is not None and 0 <= hi_idx < len(tokens):
        # box = REAL stroked ink bbox of the word + equal visible margin on all four sides
        m = int(px * MARGIN)
        tk = tokens[hi_idx]
        x = xs[hi_idx]
        x0i = y0i = 10**9; x1i = y1i = -10**9
        cx = x
        for ch in tk:
            ib = d.textbbox((cx, baseline), ch, font=font, anchor="ls", stroke_width=stroke)
            x0i, y0i = min(x0i, ib[0]), min(y0i, ib[1])
            x1i, y1i = max(x1i, ib[2]), max(y1i, ib[3])
            cx += d.textlength(ch, font=font) + track
        bx0, by0, bx1, by1 = x0i - m, y0i - m, x1i + m, y1i + m
        rad = int((by1 - by0) * RADIUS)
        d.rounded_rectangle([bx0, by0, bx1, by1], radius=rad, fill=(*PINK_RGB, 255))

    def _draw_word(t, x, **kw):
        cx = x
        for ch in t:
            d.text((cx, baseline + kw.pop("dy", 0) if False else (baseline + kw.get("dy", 0))), ch,
                   font=font, anchor="ls", **{k: v for k, v in kw.items() if k != "dy"})
            cx += d.textlength(ch, font=font) + track
    for t, x in zip(tokens, xs):
        _draw_word(t, x + shadow, dy=shadow, fill=(0, 0, 0, 160))
    for t, x in zip(tokens, xs):
        _draw_word(t, x, fill=(*TEXT_RGB, 255), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return img


def _scale_about(img, factor, cx, cy):
    if abs(factor - 1.0) < 0.005:
        return img
    w, h = img.size
    nw, nh = max(1, int(w * factor)), max(1, int(h * factor))
    s = img.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(s, (int(cx - nw * (cx / w)), int(cy - nh * (cy / h))))
    return out


def burn(video, cards, work_dir, out, font_ratio, vpos, end=None):
    width, height = probe_size(video)
    fps = probe_fps(video)
    dur = probe_duration(video) if end is None else min(end, probe_duration(video))
    px = max(16, int(width * REF_ASPECT * font_ratio))   # width-anchored (Hormozi guideline)
    base_font = ImageFont.truetype(FONT_PATH, px)
    cy = int(vpos * height)
    print(f"      redwood: Anton {px}px  vpos={vpos:.3f}  cards={len(cards)}  fps={fps:.2f}", flush=True)

    disp_end = [cards[i + 1]["start"] for i in range(len(cards) - 1)] + [cards[-1]["end"] + 0.3]
    cd = []
    meas = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    for ci, card in enumerate(cards):
        tokens = [w["text"].upper() for w in card["words"]]
        cf = base_font
        while meas.textlength(" ".join(tokens), font=cf) > width * 0.92 and cf.size > 16:
            cf = ImageFont.truetype(FONT_PATH, cf.size - 2)
        variants = [render_card(tokens, cf, width, height, cy, hi_idx=i) for i in range(len(tokens))]
        cd.append({"d0": card["start"], "d1": disp_end[ci], "words": card["words"],
                   "variants": variants})

    frames_dir = work_dir / "cap"
    frames_dir.mkdir(parents=True, exist_ok=True)
    blank = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    nframes = int(dur * fps) + 2
    prev_key = prev_path = None
    for f in range(nframes):
        t = f / fps
        active = next((c for c in cd if c["d0"] <= t < c["d1"]), None)
        scale, hi = 1.0, 0
        if active is not None:
            scale = _pop(t - active["d0"])
            hi = 0
            for wi, w in enumerate(active["words"]):
                if t >= w["start"]:
                    hi = wi          # box rides the last word whose start has passed (holds between words)
        key = ("blank",) if active is None else (id(active), hi, round(scale, 2))
        path = frames_dir / f"{f:05d}.png"
        if key == prev_key and prev_path is not None:
            shutil.copy(prev_path, path)
        else:
            if active is None:
                img = blank
            elif scale != 1.0:
                img = _scale_about(active["variants"][hi], scale, width // 2, cy)
            else:
                img = active["variants"][hi]
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
    ap.add_argument("--font-ratio", type=float, default=FONT_RATIO)
    ap.add_argument("--vertical-pos", type=float, default=VPOS)
    ap.add_argument("--max-words", type=int, default=4)
    ap.add_argument("--min-pause", type=float, default=0.35)
    ap.add_argument("--biased", default="Chowchilla:3.0,CCWF:2.0,CIW:2.0,Mija:2.0")
    ap.add_argument("--end", type=float, default=None)
    ap.add_argument("--preview", type=float, default=None,
                    help="render ONE composited frame at time T (secs) per candidate vpos, no full render")
    ap.add_argument("--preview-vpos", default="0.55,0.68,0.80",
                    help="comma list of vpos candidates for --preview")
    args = ap.parse_args()

    video = Path(args.video)
    out = Path(args.out) if args.out else video.with_name(video.stem + "_redwood.mp4")
    work = video.with_name(video.stem + "_redwoodwork")
    work.mkdir(exist_ok=True)
    biased = [b.strip() for b in args.biased.split(",") if b.strip()] if args.biased else None

    if args.preview is not None:
        # single-frame previews at candidate heights: grab frame, draw a sample card, save PNGs
        import tempfile
        width, height = probe_size(video)
        t = args.preview
        frame_png = work / "preview_src.png"
        run(["ffmpeg", "-y", "-ss", str(t), "-i", str(video), "-frames:v", "1", str(frame_png)])
        base = Image.open(frame_png).convert("RGBA")
        px = max(16, int(width * REF_ASPECT * args.font_ratio))
        f = ImageFont.truetype(FONT_PATH, px)
        outs = []
        for v in [float(x) for x in args.preview_vpos.split(",") if x.strip()]:
            cy = int(v * height)
            card = render_card(["SAMPLE", "CAPTION", "HEIGHT."], f, width, height, cy)
            comp = base.copy(); comp.alpha_composite(card)
            op = video.with_name(f"{video.stem}_vpos{v:.2f}.png")
            comp.convert("RGB").save(op, quality=92)
            outs.append(str(op))
        print("PREVIEWS: " + " ".join(outs), flush=True)
        return

    print("[1/2] Scribe transcribe", flush=True)
    result = scribe_transcribe(video, biased)
    cards = build_cards(result.get("segments", []), max_words=args.max_words, min_pause=args.min_pause)
    print(f"      {len(cards)} cards", flush=True)
    print("[2/2] render Redwood captions", flush=True)
    burn(video, cards, work, out, args.font_ratio, args.vertical_pos, end=args.end)
    print(f"DONE -> {out}", flush=True)


if __name__ == "__main__":
    main()
