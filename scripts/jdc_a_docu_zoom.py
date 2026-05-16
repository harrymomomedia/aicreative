"""Apply varied docu-zoom + letterbox-with-blur preservation to 6 inmate backdrops.

Each backdrop:
- Background: scaled+blurred source filling 720x1280 (context-aware filler)
- Foreground: source preserving 2:3 aspect (no horizontal crop), animated docu-zoom
- Composite fg over bg

Varied camera moves per backdrop (push-in, pull-back, tilt, pan) to avoid templated feel.

Output: outputs/illinois_jdc_urban_peer/backdrops/zoom_<slug>.mp4
"""
import subprocess
from pathlib import Path

BG_DIR = Path("outputs/illinois_jdc_urban_peer/news_storyboard")
OUT_DIR = Path("outputs/illinois_jdc_urban_peer/backdrops")
OUT_DIR.mkdir(parents=True, exist_ok=True)

DURATION = 4
FPS = 24
FRAMES = DURATION * FPS  # 96

# Foreground area: 720x1080 (2:3 aspect, fills width of 720x1280 canvas)
# Source 1024x1536, scale to 2160x3240 (2.1x) for zoompan headroom
FG_W = 720
FG_H = 1080
SRC_SCALE_W = 2160
SRC_SCALE_H = 3240

# Each: (z, x, y, label) for foreground zoompan
ZOOM_RECIPES = {
    "inmate1_line_walk": (
        "min(zoom+0.0016,1.16)",
        "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)",
        "slow push-in center",
    ),
    "inmate3_intake_photo": (
        "min(zoom+0.0020,1.20)",
        "iw/3-(iw/zoom/3)",   # focal left (teen at height chart)
        "ih/2-(ih/zoom/2)",
        "push-in left",
    ),
    "inmate6_pat_down": (
        "min(zoom+0.0022,1.22)",
        "iw/3-(iw/zoom/3)",
        "ih/2-(ih/zoom/2)",
        "tight push-in left",
    ),
    "inmate4_cafeteria_lines": (
        "1.10",
        "iw/2-(iw/zoom/2)",
        "ih*0.15 + (ih*0.45 - ih*0.15) * on/{}".format(FRAMES),  # tilt down
        "slow tilt-down",
    ),
    "inmate5_yard_outside": (
        "if(eq(on,0),1.18,max(zoom-0.0019,1.00))",
        "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)",
        "slow pull-back",
    ),
    "inmate2_dayroom_watch": (
        "min(zoom+0.0018,1.18)",
        "(2*iw/3)-(iw/zoom/2)",  # focal right (toward guard)
        "ih/2-(ih/zoom/2)",
        "push-in right",
    ),
}


def render(slug, z, x, y, label):
    src = BG_DIR / f"inmate_{slug}.png"
    out = OUT_DIR / f"zoom_{slug}.mp4"
    # Background: scale + blur to fill 720x1280
    # Foreground: scale up 2:3 source, zoompan, output 720x1080 fg
    # Overlay fg centered vertically in 720x1280 canvas
    vf = (
        f"[0:v]scale=2560:3840,boxblur=40:8,scale=720:1280,setsar=1[bg];"
        f"[0:v]scale={SRC_SCALE_W}:{SRC_SCALE_H},"
        f"zoompan=z='{z}':x='{x}':y='{y}':d={FRAMES}:s={FG_W}x{FG_H}:fps={FPS},setsar=1[fg];"
        f"[bg][fg]overlay=x=0:y=(H-h)/2,setsar=1[v]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", str(DURATION),
        "-i", str(src),
        "-filter_complex", vf,
        "-map", "[v]", "-t", str(DURATION),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        str(out),
    ]
    print(f"  [{slug}] {label}", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  FAILED: {r.stderr[-500:]}")
    return out


def main():
    for slug, (z, x, y, label) in ZOOM_RECIPES.items():
        render(slug, z, x, y, label)
    print("\nDone.")


if __name__ == "__main__":
    main()
