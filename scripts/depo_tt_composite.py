"""Depo_tt composite — scan/scar backdrop + big MENINGIOMA word + persona PIP (bottom-right).

Layers (720x1280 canvas):
  1. backdrop still -> cover + slow push-in zoom (documentary "the evidence")
  2. big bold MENINGIOMA word (PIL overlay — this ffmpeg has NO drawtext), TOP band so it
     clears a subject backdrop (survivor's scar), dark scrim for legibility
  3. persona matte (VEED vp9-alpha webm) scaled to height 720, PIP bottom-right (CLAUDE.md PIP)
  4. audio from the assembled talking-head _final.mp4

  python scripts/depo_tt_composite.py <backdrop.png> <matte.webm> <audio_final.mp4> <out.mp4> [WORD] [top|bottom]
Then caption with Hormozi at --vertical-pos 0.85 (PIP override).
"""
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
FONT = "assets/fonts/Montserrat-Black.ttf"


def dur_of(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip())


def word_overlay(word, pos, out_png):
    """Transparent 720x1280 PNG with a dark scrim band + centered bold word."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype(FONT, 96)
    bb = d.textbbox((0, 0), word, font=fnt)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    band_y = 40 if pos == "top" else H - 300
    band_h = th + 96
    # scrim band for legibility over a photo backdrop
    scrim = Image.new("RGBA", (W, band_h), (0, 0, 0, 150))
    img.paste(scrim, (0, band_y), scrim)
    tx = (W - tw) // 2 - bb[0]
    ty = band_y + (band_h - th) // 2 - bb[1]
    d.text((tx, ty), word, font=fnt, fill=(255, 255, 255, 255),
           stroke_width=3, stroke_fill=(0, 0, 0, 220))
    img.save(out_png)
    return out_png


def main():
    backdrop, matte, audio, out = sys.argv[1:5]
    word = sys.argv[5] if len(sys.argv) > 5 else "MENINGIOMA"
    pos = sys.argv[6] if len(sys.argv) > 6 else "top"
    dur = dur_of(audio)
    frames = int(dur * 24) + 1
    wlay = str(Path(out).with_name("_wordlay.png"))
    word_overlay(word, pos, wlay)

    bg = (f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
          f"zoompan=z='min(zoom+0.00035,1.14)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
          f"s={W}x{H}:fps=24,setsar=1[bg];")
    word_ov = "[bg][2:v]overlay=0:0[bgw];"
    pip = "[1:v]scale=-1:720,setsar=1[pip];"
    comp = "[bgw][pip]overlay=x=W-w-24:y=H-h-16:shortest=1,format=yuv420p[v]"

    cmd = ["ffmpeg", "-y",
           "-loop", "1", "-framerate", "24", "-t", f"{dur:.2f}", "-i", backdrop,
           "-c:v", "libvpx-vp9", "-i", matte,     # vp9 decoder BEFORE the webm preserves alpha
           "-i", wlay,
           "-i", audio,
           "-filter_complex", bg + word_ov + pip + comp,
           "-map", "[v]", "-map", "3:a", "-t", f"{dur:.2f}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG FAILED:\n" + r.stderr[-1200:]); sys.exit(1)
    print(f"composite -> {out}  ({dur:.1f}s)")


if __name__ == "__main__":
    main()
