"""Depo docu b-roll library — animate approved stills into clips (veo-3.1-lite i2v).
Each approved still (gpt2 v01-v24 portrait, nano nn_*/rp_* landscape) becomes an 8s muted-use
b-roll clip via startImage i2v. Subtle-documentary motion prompts; audio ignored at edit time.
Skip-if-exists → re-run resumes. Output: outputs/depo_docu/broll_clips/<slug>.mp4

  .venv/bin/python scripts/depo_docu_broll_i2v.py [--only slug1,slug2]
"""
import argparse
import glob
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from googleflow_client import generate_veo, upload_asset, download

SRC = "outputs/depo_docu/broll_stills"
OUT = "outputs/depo_docu/broll_clips"
os.makedirs(OUT, exist_ok=True)

BASE = ("Subtle documentary motion only: gentle handheld drift, people and hands in frame continue "
        "their natural small movements, nothing new enters the frame, no cuts, no zoom bursts. "
        "Keep the scene exactly as the image. Muted natural light. No speech. "
        "NO on-screen text, NO captions, NO logos, NO watermark.")
HINT = {
    "v01": "The doctor's pen traces slowly along the scan; the patient nods slightly.",
    "v02": "The doctor gestures at the screen; the woman's hand lowers slowly from her mouth.",
    "v03": "The radiologist scrolls; scan slices change on the monitor with a soft glow.",
    "v04": "The films pass slowly from one hand to the other.",
    "v05": "The doctor's hands turn the brain model slightly while gesturing.",
    "v06": "The nurse's hands finish adjusting the IV line; the patient breathes slowly.",
    "v07": "The bed keeps rolling down the corridor; ceiling lights pass overhead.",
    "v08": "The table slides slowly into the scanner bore.",
    "v09": "The drip chamber drips once; fingers twitch slightly.",
    "v10": "The plunger draws liquid up slowly from the vial.",
    "v11": "The nurse completes the injection smoothly; the woman stays looking away.",
    "v12": "The swab wipes a small circle on the arm.",
    "v13": "Very slow push-in toward the box and vial.",
    "v14": "Slow lateral pan along the shelf, focus holding on the violet box.",
    "v15": "The gloved hand sets the vial down and withdraws.",
    "v16": "She taps the screen; the younger woman leans in closer.",
    "v17": "The cursor clicks to the next scan image.",
    "v18": "The phone tilts slightly in her hand, screen catching light.",
    "v19": "A page turns slowly in the folder.",
    "v20": "The document slides the rest of the way out of the envelope.",
    "v21": "The red pen completes its circle around the paragraph.",
    "v22": "The pen finishes the signature stroke.",
    "v23": "The folder passes across the table between hands.",
    "v24": "She climbs two more steps, coat moving slightly.",
    "nn_doc_points": "The doctor's pen moves along the lightbox scan; the patient stays still.",
    "nn_monitor": "The doctor steadies the monitor; the woman blinks, hand at her mouth.",
    "nn_postop": "The nurse's hands finish the IV adjustment; the patient rests.",
    "nn_injection": "The injection completes smoothly; she keeps facing the window.",
    "nn_depo_box": "Very slow push-in; the pharmacist moves softly out of focus behind.",
    "nn_laptop_point": "She points along the scan on screen; the younger woman nods.",
    "rp1_desk": "Very slow push-in toward the paper's title; light flickers softly.",
    "rp2_laptop": "She scrolls the document slightly; screen glow shifts on her hands.",
    "rp3_hands": "The page tilts gently in her hands as she reads.",
}


def stills():
    out = []
    for f in sorted(glob.glob(f"{SRC}/v*.png")) + sorted(glob.glob(f"{SRC}/nn_*.png")) + sorted(glob.glob(f"{SRC}/rp*.png")):
        slug = os.path.splitext(os.path.basename(f))[0]
        out.append((slug, f))
    return out


import subprocess


def animate(slug, path):
    """One clip. Returns (slug, status, note). Model = omni-flash: it's video-first and does
    NOT run Veo's speech-audio filter, so the random AUDIO_GENERATION_FILTERED failure that
    plagued veo-3.1-fast/lite never fires (verified 2026-07-09: 3/3 clinical stills passed
    first try, no retries). Cheapest model too. We STRIP the audio track (-an) on download so
    the b-roll is truly silent — nobody is talking in b-roll."""
    dest = f"{OUT}/{slug}.mp4"
    if os.path.exists(dest) and os.path.getsize(dest) > 50000:
        return slug, "cached", ""
    w, h = Image.open(path).size
    aspect = "portrait" if h >= w else "landscape"
    key = slug[:3] if slug.startswith("v") and slug[1:3].isdigit() else slug
    prompt = (HINT.get(key, HINT.get(slug, "")) + " " + BASE).strip()
    try:
        mgid = upload_asset(path)
        r = generate_veo(prompt=prompt, image_mgid=mgid, duration=8,
                         aspect_ratio=aspect, model="omni-flash", attempts=4)
        if r.get("status") == "success" and r.get("urls"):
            tmp = f"{OUT}/.{slug}_raw.mp4"
            download(r["urls"][0], tmp)
            subprocess.run(["ffmpeg", "-y", "-i", tmp, "-c:v", "copy", "-an", dest],
                           capture_output=True)
            os.remove(tmp)
            return slug, "ok", ""
        return slug, "FAIL", str(r.get("raw"))[:120]
    except Exception as e:
        return slug, "EXC", str(e)[:120]


def main():
    from concurrent.futures import ThreadPoolExecutor, as_completed
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()
    todo = stills()
    if args.only:
        want = {s.strip() for s in args.only.split(",")}
        todo = [(s, f) for s, f in todo if s in want]
    pending = [(s, f) for s, f in todo
               if not (os.path.exists(f"{OUT}/{s}.mp4") and os.path.getsize(f"{OUT}/{s}.mp4") > 50000)]
    print(f"{len(todo)} stills, {len(pending)} pending, {args.workers} workers", flush=True)
    ok, fail = [], []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(animate, s, f): s for s, f in pending}
        for fut in as_completed(futs):
            slug, status, note = fut.result()
            print(f"  {slug} -> {status} {note}".rstrip(), flush=True)
            (ok if status in ("ok", "cached") else fail).append(slug)
    print(f"\nDONE: {len(ok)} ok, {len(fail)} failed", flush=True)
    if fail:
        print("FAILED: " + ",".join(sorted(fail)), flush=True)


if __name__ == "__main__":
    main()
