#!/usr/bin/env python3
"""CAWP PIP composite: bg-removed persona talking head over ROTATING static vertical
prison backdrops with a slow documentary zoom + subtle PIP drift.
Nick captions are a SEPARATE pass afterward.

Usage:
  cawp_pip_composite.py <LETTER> <slug1,slug2,...> [--interval 5] [--side right|left]
                        [--persona-h 700] [--out-suffix _pip]

  persona alpha : outputs/chowchilla_podcast/<L>_full_alpha.webm  (VEED/fal, vp9 alpha)
  audio         : outputs/chowchilla_podcast/<L>_full.mp4
  backdrops     : outputs/cawp_broll_wp/vert/<slug>.png           (9:16 2K)
  out           : outputs/chowchilla_podcast/<L><out-suffix>.mp4  (720x1280)

Backdrop hard-cuts every --interval seconds, cycling the slug list. Each segment gets a
varied docu-zoom recipe (push-in / pull-back / left-bias / right-bias) so it never looks
templated. Persona is anchored to --side (opposite the backdrop subjects so she never
blocks them) and drifts subtly via sin() so she is not dead-still.
Caption pass uses --vertical-pos 0.85 (PIP override).
"""
import math
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POD  = os.path.join(ROOT, "outputs", "chowchilla_podcast")
VERT = os.path.join(ROOT, "outputs", "cawp_broll_wp", "vert")
FPS  = 30

# per-segment docu-zoom recipes (varied so rotation doesn't feel templated)
def zoom_expr(kind, frames):
    if kind == 0:   # slow push-in center
        return ("min(zoom+0.00040,1.14)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)")
    if kind == 1:   # slow pull-back center
        return ("if(eq(on,0),1.14,max(zoom-0.00040,1.0))", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)")
    if kind == 2:   # push-in, drift toward LEFT third (subject bias)
        return ("min(zoom+0.00038,1.14)", "iw/3-(iw/zoom/3)", "ih/2-(ih/zoom/2)")
    # kind == 3: push-in, drift toward RIGHT third
    return ("min(zoom+0.00038,1.14)", "(2*iw/3)-(iw/zoom/2)", "ih/2-(ih/zoom/2)")


def probe_dur(path):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path]).decode().strip())


def resolve_slug(slug):
    """Accept a short prefix (v10) or full slug (v10_escort_grip)."""
    p = os.path.join(VERT, f"{slug}.png")
    if os.path.exists(p):
        return slug
    for f in os.listdir(VERT):
        if f.endswith(".png") and (f == f"{slug}.png" or f.startswith(f"{slug}_")):
            return f[:-4]
    raise FileNotFoundError(slug)


def main():
    L = sys.argv[1]
    slugs = [resolve_slug(s.strip()) for s in sys.argv[2].split(",") if s.strip()]
    interval = float(sys.argv[sys.argv.index("--interval") + 1]) if "--interval" in sys.argv else 5.0
    side = sys.argv[sys.argv.index("--side") + 1] if "--side" in sys.argv else "right"
    persona_h = int(sys.argv[sys.argv.index("--persona-h") + 1]) if "--persona-h" in sys.argv else 700
    suffix = sys.argv[sys.argv.index("--out-suffix") + 1] if "--out-suffix" in sys.argv else "_pip"

    alpha = os.path.join(POD, f"{L}_full_alpha.webm")
    audio = os.path.join(POD, f"{L}_full.mp4")
    out   = os.path.join(POD, f"{L}{suffix}.mp4")
    for p in (alpha, audio):
        assert os.path.exists(p), p

    dur = probe_dur(audio)
    total_frames = int(round(dur * FPS))

    # segment plan: cut every `interval` s, cycle the slug list
    n_seg = max(1, math.ceil(dur / interval))
    segs = []          # (slug, frames)
    used = 0
    for i in range(n_seg):
        f = int(round(min(interval, dur - used / FPS * 1) * FPS)) if False else 0
        # frames for this segment
        start_f = int(round(i * interval * FPS))
        end_f = int(round(min((i + 1) * interval, dur) * FPS))
        segs.append((slugs[i % len(slugs)], max(1, end_f - start_f)))
    # fix rounding so segment frames sum to total_frames
    diff = total_frames - sum(f for _, f in segs)
    if diff != 0:
        s0, f0 = segs[-1]
        segs[-1] = (s0, max(1, f0 + diff))

    inputs = []
    for slug, _ in segs:
        inputs += ["-loop", "1", "-t", f"{(2):.0f}", "-i", os.path.join(VERT, f"{slug}.png")]
    n_img = len(segs)
    inputs += ["-c:v", "libvpx-vp9", "-i", alpha]      # index n_img = persona alpha
    inputs += ["-i", audio]                             # index n_img+1 = audio

    fc = []
    for i, (slug, frames) in enumerate(segs):
        zk = i % 4
        z, x, y = zoom_expr(zk, frames)
        fc.append(
            f"[{i}:v]scale=1440:2560,setsar=1,"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s=720x1280:fps={FPS},"
            f"trim=end_frame={frames},setpts=PTS-STARTPTS,format=yuv420p[bg{i}]"
        )
    fc.append("".join(f"[bg{i}]" for i in range(n_seg)) + f"concat=n={n_seg}:v=1:a=0[bg]")
    fc.append(f"[{n_img}:v]scale=-1:{persona_h},setsar=1[fg]")

    # subtle drift; anchor to side, keep fully in frame
    if side == "left":
        xbase = "8"
    else:
        xbase = "W-w-8"
    x_ov = f"{xbase}+14*sin(2*PI*t/7)"
    y_ov = "H-h+10*sin(2*PI*t/5)"
    fc.append(f"[bg][fg]overlay=x='{x_ov}':y='{y_ov}':shortest=1,format=yuv420p[v]")

    cmd = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error"] + inputs + [
        "-filter_complex", ";".join(fc),
        "-map", "[v]", "-map", f"{n_img+1}:a", "-t", f"{dur:.3f}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", out,
    ]
    subprocess.run(cmd, check=True)
    print("OK", out, "| segs:", ", ".join(s for s, _ in segs))


if __name__ == "__main__":
    main()
