"""Upscale picked podcast hosts to true 4K (2160x3840), IDENTITY-PRESERVING via Real-ESRGAN.
(gpt-image-2 i2i was tried first and REGENERATED a different person — wrong tool. Real-ESRGAN is
pixel super-resolution: same exact face, more pixels.)

Real-ESRGAN GPU caps input at ~2.09M px, so the 1152x2048 source is downscaled to 1080x1920 first,
then 2x SR -> 2160x3840.

Usage: .venv/bin/python scripts/jdc_pod_upscale_4k.py real_11 real_14 real_15
"""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import replicate_client as rc

OUT = Path("outputs/jdc_podcast_personas")


def go(slug, face_enhance=True):
    src = OUT / f"{slug}.png"
    if not src.exists():
        return slug, "MISSING", str(src)
    small = f"/tmp/{slug}_in.png"
    up = f"/tmp/{slug}_up.png"
    dst = OUT / f"{slug}_4k.png"
    subprocess.run(["ffmpeg", "-y", "-i", str(src), "-vf", "scale=1080:1920", small], capture_output=True)
    url = rc.upscale_image(small, scale=2, face_enhance=face_enhance)
    rc.download(url, up)
    subprocess.run(["ffmpeg", "-y", "-i", up, "-vf", "scale=2160:3840", str(dst)], capture_output=True)
    return slug, "success", str(dst)


def main():
    slugs = sys.argv[1:] or ["real_11", "real_14", "real_15"]
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(go, s): s for s in slugs}
        for f in as_completed(futs):
            slug, status, info = f.result()
            print(f"[{slug}] {status}: {info}", flush=True)


if __name__ == "__main__":
    main()
