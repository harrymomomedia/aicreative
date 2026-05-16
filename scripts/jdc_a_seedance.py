"""Illinois JDC ad — Persona A (Urban Peer) via KIE Seedance.

Pipeline:
  - 2 talking-head clips of persona A (12s each, KIE Seedance with ref image)
  - 5 B-roll clips (text-to-video, no ref image)
  - All in parallel where possible

Outputs:
  outputs/illinois_jdc_urban_peer/
    talking_head_clip{1,2}.mp4
    broll_{1..5}.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_seedance, upload_file, download

OUT_DIR = Path("outputs/illinois_jdc_urban_peer")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Upload persona A once
ANCHOR_PATH = OUT_DIR / "reference/1.png"
ANCHOR_URL_FILE = OUT_DIR / "anchor_url.txt"
if ANCHOR_URL_FILE.exists():
    ANCHOR_URL = ANCHOR_URL_FILE.read_text().strip()
    print(f"reusing anchor: {ANCHOR_URL}")
else:
    ANCHOR_URL = upload_file(str(ANCHOR_PATH), "image/png")
    ANCHOR_URL_FILE.write_text(ANCHOR_URL)
    print(f"uploaded anchor: {ANCHOR_URL}")


# ─── PERSONA A talking head prompts (2 clips chained via same ref) ───

CHARACTER = (
    "A handheld phone selfie video, 9:16 portrait, photoreal UGC. "
    "A Black man, mid-20s, short 360 waves haircut with clean line-up, thin chinstrap beard, "
    "plain heather-grey pullover hoodie, single small silver hoop earring (left ear). "
    "He stands outside on a Chicago neighborhood side street, brick three-flat building behind him with chipped paint trim, "
    "chain-link fence partly visible, autumn leaves on the sidewalk, overcast daylight. "
    "Visible pores, faint razor bumps, fine lines, slight oil shine, weathered skin. "
    "No makeup, no beauty mode, no retouching, no filter. "
    "Camera locked, no zoom, no pan, static handheld selfie framing."
)

TONE_HYPED = (
    "Emotional register: HYPED, urgent, leaning into the camera, eyebrows engaged, "
    "peer-to-peer street vernacular, slightly louder than calm — like he's calling out to his block. "
    "NOT a news anchor, NOT calm, NOT older-brother — urgent, animated, in your face."
)

LOCKS = (
    "CRITICAL — EYES OPEN AND ON CAMERA: Throughout the entire clip his eyes stay OPEN and looking DIRECTLY at the lens. "
    "CRITICAL — DIALOGUE LOCK: He speaks in ENGLISH ONLY. Do NOT add fillers like 'uh', 'um', 'like'. "
    "Do NOT add any trailing words at the end. Speak ONLY the words listed verbatim, STOP after the final word. "
    "ABSOLUTELY NO on-screen text, no captions, no subtitles, no watermarks, no logos."
)

TH_CLIP_1_SCRIPT = (
    "Yo. People got abused in Illinois juvenile centers, "
    "Cook County, Saint Charles, Harrisburg. "
    "Now survivors are stepping up and getting significant potential compensation."
)
TH_CLIP_2_SCRIPT = (
    "Don't be one of them. Millions have already been awarded in cases like this. "
    "If that's your story, tap in right now. "
    "Significant potential compensation might got your name on it."
)


def build_th_prompt(spoken):
    return (
        f"{CHARACTER}\n\n{TONE_HYPED}\n\n{LOCKS}\n\n"
        f"SPOKEN DIALOGUE (verbatim, no additions, stop after final word): \"{spoken}\""
    )


# ─── B-ROLL prompts (text-to-video, no ref image) ───

BROLL_PROMPTS = {
    1: (
        "Wide low-angle shot of a uniformed prison guard escorting a teenage boy in an "
        "orange jumpsuit down a long fluorescent-lit institutional hallway. Checkered linoleum floor, "
        "doors lining both walls, deep one-point perspective. Cold blue-fluorescent lighting. "
        "Handheld documentary feel. No on-screen text.",
        4,
    ),
    2: (
        "Wide exterior daylight shot of a grey concrete institutional juvenile detention building "
        "behind a tall chain-link fence topped with coiled razor wire. Overcast sky, "
        "single barred window visible, weathered concrete. Static locked shot. No on-screen text.",
        5,
    ),
    3: (
        "Close-up overhead shot of a fanned stack of cashier's checks lying beside a heavy wooden "
        "judge's gavel on a polished wooden desk. Soft warm side light from a desk lamp. "
        "Slow subtle push-in. No on-screen text.",
        5,
    ),
    4: (
        "Over-the-shoulder shot from behind a survivor sitting across a wooden desk from "
        "an attorney in a white shirt and dark tie. The attorney leans forward listening, soft daylight "
        "from a window on the right side of frame. Warm, quiet, intimate. No on-screen text.",
        5,
    ),
    5: (
        "POV extreme close-up of a person's hand holding a smartphone, thumb hovering then tapping "
        "a bright green 'SUBMIT' button on a web qualification form on the screen. "
        "Slight motion blur on the thumb. Phone screen is sharp. No on-screen text.",
        5,
    ),
}


# ─── Generation jobs ───

def gen_talking_head(clip_idx, spoken):
    out = OUT_DIR / f"talking_head_clip{clip_idx}.mp4"
    if out.exists():
        return clip_idx, "exists", str(out)
    prompt = build_th_prompt(spoken)
    print(f"[TH{clip_idx}] submitting...", flush=True)
    r = generate_seedance(
        prompt=prompt,
        duration=12,
        aspect_ratio="9:16",
        ref_images=[ANCHOR_URL],
        generate_audio=True,
    )
    if r["status"] != "success" or not r["urls"]:
        return clip_idx, "failed", str(r.get("raw"))[:300]
    download(r["urls"][0], str(out))
    return clip_idx, "success", str(out)


def gen_broll(idx, prompt, duration):
    out = OUT_DIR / f"broll_{idx}.mp4"
    if out.exists():
        return idx, "exists", str(out)
    print(f"[BROLL{idx}] submitting...", flush=True)
    r = generate_seedance(
        prompt=prompt,
        duration=duration,
        aspect_ratio="9:16",
        ref_images=None,
        generate_audio=False,
    )
    if r["status"] != "success" or not r["urls"]:
        return idx, "failed", str(r.get("raw"))[:300]
    download(r["urls"][0], str(out))
    return idx, "success", str(out)


def main():
    jobs = []
    jobs.append(("TH", 1, lambda: gen_talking_head(1, TH_CLIP_1_SCRIPT)))
    jobs.append(("TH", 2, lambda: gen_talking_head(2, TH_CLIP_2_SCRIPT)))
    for idx, (prompt, dur) in BROLL_PROMPTS.items():
        jobs.append(("BROLL", idx, lambda p=prompt, d=dur, i=idx: gen_broll(i, p, d)))

    results = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(j[2]): (j[0], j[1]) for j in jobs}
        for f in as_completed(futures):
            kind, idx = futures[f]
            try:
                _, status, info = f.result()
                results[(kind, idx)] = (status, info)
                print(f"[{kind}{idx}] {status}: {info}", flush=True)
            except Exception as e:
                results[(kind, idx)] = ("EXC", str(e))
                print(f"[{kind}{idx}] EXC: {e}", flush=True)

    print("\n=== SUMMARY ===")
    for (kind, idx), (status, info) in sorted(results.items()):
        print(f"  {kind}{idx}: {status}")


if __name__ == "__main__":
    main()
