"""Generate 2 documentary-style moving B-roll clips via OpenRouter Seedance.

Theme: chaotic institutional documentary realism — multiple guards + teens in motion,
handheld camera, desaturated palette, no explicit violence (would fail moderation).
Adapted for male juvenile detention to match IL JDC ad context.

Cost: ~$0.27 × 2 = ~$0.54 total.
"""
import os
import sys
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from openrouter_client import generate_video

OUT_DIR = Path("outputs/illinois_jdc_urban_peer")
KEY = os.getenv("OPENROUTER_API_KEY") or open(".env").read().split("OPENROUTER_API_KEY=")[1].split("\n")[0]

PROMPTS = {
    "doc1_intake_chaos": (
        "Wide handheld documentary tracking shot inside a busy juvenile detention intake "
        "processing room. Multiple teenage boys in faded orange jumpsuits — Latino and "
        "African-American — are being processed by 3 to 4 uniformed adult guards. One guard "
        "fingerprints a teen at a steel counter. Another guard firmly grips a teen's upper "
        "arm, walking him toward a holding bench bolted to the wall. A third guard at a "
        "podium stamps paperwork. A fourth stands watch at the doorway, baton on his belt. "
        "Chaotic but controlled atmosphere — multiple bodies in motion, overlapping activity. "
        "Background: scuffed beige cinderblock walls, harsh overhead fluorescent lights "
        "casting cold shadows, polished checkered linoleum floor, faded posters on walls. "
        "Camera handheld with natural shake, weaving between figures, capturing the "
        "dehumanizing process. Gritty documentary realism, desaturated color palette, "
        "institutional greys, muted oranges, harsh whites. Tense, oppressive, claustrophobic "
        "atmosphere. ABSOLUTELY NO on-screen text, no captions, no subtitles, no watermarks."
    ),
    "doc2_lockdown_sweep": (
        "Wide low-angle handheld documentary tracking shot following 4 uniformed adult guards "
        "rushing down a long fluorescent-lit institutional corridor toward an off-screen "
        "incident. Heavy black boots pounding polished checkered linoleum tile, batons "
        "visible on belts, walkie-talkies crackling, urgent purposeful motion. Camera moves "
        "with them, handheld with intentional shake, pulled back about 4 meters showing the "
        "deep one-point perspective of the corridor stretching ahead. Background: painted "
        "cinderblock walls, heavy metal cell doors lining both sides, cold blue-grey "
        "fluorescent overhead lighting, faded yellow safety stripes on the floor. "
        "Mid-evening institutional lighting. Mix of Latino and African-American guards. "
        "Power-and-authority atmosphere — no actual incident visible, just the response in "
        "motion. Gritty documentary realism, desaturated palette, institutional greys, "
        "navy uniforms, high contrast deep shadows. ABSOLUTELY NO on-screen text, no captions, "
        "no subtitles, no watermarks."
    ),
}


def gen(slug, prompt):
    out = OUT_DIR / f"broll_doc_{slug}.mp4"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] submitting...", flush=True)
    r = generate_video(
        prompt=prompt,
        model="bytedance/seedance-2.0-fast",
        aspect_ratio="9:16",
        resolution="480p",
        duration=5,
        generate_audio=False,
    )
    if r["status"] != "success" or not r["urls"]:
        return slug, "failed", str(r.get("raw"))[:400]
    r2 = requests.get(r["urls"][0], stream=True, headers={"Authorization": f"Bearer {KEY}"})
    r2.raise_for_status()
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as f:
        for chunk in r2.iter_content(1 << 16):
            f.write(chunk)
    return slug, "success", str(out)


def main():
    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = {ex.submit(gen, s, p): s for s, p in PROMPTS.items()}
        for f in as_completed(futures):
            s = futures[f]
            try:
                _, status, info = f.result()
                print(f"[{s}] {status}: {info}", flush=True)
            except Exception as e:
                print(f"[{s}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
