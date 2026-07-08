"""Depo_tt composite — scan backdrop + big MENINGIOMA word + persona PIP (bottom-right).

Layers (720x1280 canvas):
  1. MRI/scan still -> cover + slow push-in zoom (documentary "the evidence")
  2. big bold "MENINGIOMA" word, upper third, dark box for legibility over the busy scan
  3. persona matte (VEED vp9-alpha webm) scaled to height 720, PIP bottom-right (CLAUDE.md PIP)
  4. audio from the assembled talking-head _final.mp4

  python scripts/depo_tt_composite.py <scan.png> <matte.webm> <audio_final.mp4> <out.mp4> [WORD]
Then caption with Hormozi at --vertical-pos 0.85 (PIP override).
"""
import subprocess
import sys
from pathlib import Path

FONT = "assets/fonts/Montserrat-Black.ttf"


def dur_of(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip())


def main():
    scan, matte, audio, out = sys.argv[1:5]
    word = sys.argv[5] if len(sys.argv) > 5 else "MENINGIOMA"
    dur = dur_of(audio)
    frames = int(dur * 24) + 1

    # backdrop: scale up for zoom headroom, slow push-in to 720x1280, then the word
    bg = (f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
          f"zoompan=z='min(zoom+0.00035,1.14)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
          f"s=720x1280:fps=24,setsar=1[bg];")
    # dark scrim strip behind the word for legibility, then the word (upper third)
    txt = (f"[bg]drawbox=x=0:y=150:w=720:h=170:color=black@0.42:t=fill,"
           f"drawtext=fontfile={FONT}:text='{word}':fontcolor=white:fontsize=92:"
           f"x=(w-tw)/2:y=196:borderw=3:bordercolor=black@0.85[bgt];")
    # persona PIP: matte to height 720 (~56% canvas), bottom-right per CLAUDE.md PIP
    pip = "[1:v]scale=-1:720,setsar=1[pip];"
    comp = "[bgt][pip]overlay=x=W-w-24:y=H-h-16:shortest=1,format=yuv420p[v]"

    cmd = ["ffmpeg", "-y",
           "-loop", "1", "-framerate", "24", "-t", f"{dur:.2f}", "-i", scan,
           "-c:v", "libvpx-vp9", "-i", matte,          # vp9 decoder BEFORE the webm preserves alpha
           "-i", audio,
           "-filter_complex", bg + txt + pip + comp,
           "-map", "[v]", "-map", "2:a", "-t", f"{dur:.2f}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG FAILED:\n" + r.stderr[-1200:]); sys.exit(1)
    print(f"composite -> {out}  ({dur:.1f}s)")


if __name__ == "__main__":
    main()
