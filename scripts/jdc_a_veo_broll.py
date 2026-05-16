"""Generate 3 random Veo 3 B-roll clips via Poyo for Illinois JDC ad.

Text-to-video, no reference images. 8s each, 9:16 720p.
Output: outputs/illinois_jdc_urban_peer/veo_broll_{name}.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poyo_client import generate_veo, download

OUT_DIR = Path("outputs/illinois_jdc_urban_peer")

PROMPTS = {
    "v1_corridor": (
        "Slow dolly push-in down an empty institutional corridor at night, single fluorescent overhead "
        "light flickering, painted concrete-block walls, heavy metal doors lining both sides, polished "
        "checkered linoleum floor reflecting the cold blue-fluorescent light. Deep one-point perspective. "
        "Camera locked low, slow forward motion. Ambient room tone + faint distant clang. "
        "ABSOLUTELY NO on-screen text, no captions, no subtitles, no watermarks, no logos."
    ),
    "v7_gavel": (
        "Extreme close-up cinematic side-angle of a heavy polished wooden judge's gavel held in a hand, "
        "striking down hard onto a wooden sound block on a courtroom bench. Slow-motion at 240fps — the "
        "gavel impacts, vibrates briefly, and lifts away. Sharp wooden crack on impact. Warm courtroom "
        "lighting, soft tungsten key from the right, dark mahogany background. Static locked camera. "
        "ABSOLUTELY NO on-screen text, no captions, no subtitles, no watermarks, no logos."
    ),
    "v11_notification": (
        "Static top-down close-up of a modern smartphone lying face-up on a wooden desk, screen visible. "
        "A clean green text-message notification slides in from the top of the screen, showing a short "
        "message that reads exactly: \"You may qualify\". The phone screen is the only on-screen text — "
        "everything else in the frame is real-world objects. Soft warm desk-lamp light from the upper-left. "
        "Camera locked, no movement. Subtle finger appears at the edge of frame to tap the notification."
    ),
}


def gen(name, prompt):
    out = OUT_DIR / f"veo_broll_{name}.mp4"
    if out.exists():
        return name, "exists", str(out)
    print(f"[{name}] submitting...", flush=True)
    r = generate_veo(
        prompt=prompt,
        image_urls=None,
        aspect_ratio="9:16",
        resolution="720p",
        model="veo3.1-fast",
        generation_type=None,
    )
    if r["status"] != "success" or not r["urls"]:
        return name, "failed", str(r.get("raw"))[:300]
    download(r["urls"][0], str(out))
    return name, "success", str(out)


def main():
    with ThreadPoolExecutor(max_workers=3) as ex:
        futures = {ex.submit(gen, n, p): n for n, p in PROMPTS.items()}
        for f in as_completed(futures):
            n = futures[f]
            try:
                _, status, info = f.result()
                print(f"[{n}] {status}: {info}", flush=True)
            except Exception as e:
                print(f"[{n}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
