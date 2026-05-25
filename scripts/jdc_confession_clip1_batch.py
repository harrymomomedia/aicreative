"""Clip 1 of all 4 Tier-1 ads, in parallel. Each establishes its persona.

Ad 1 (Confession)        → persona 3 (34)
Ad 2 (Memory Trigger)    → persona 2 (26)
Ad 3 (He's Still Out There) → persona 2 (26)   (same persona, own ad folder)
Ad 4 (You Were a Kid)    → persona 1 (20)

Short i2v prompts (persona + setting already in anchor).
KIE Veo Lite 720p, FIRST_AND_LAST_FRAMES anchor, parallel.

Outputs:
  outputs/illinois_jdc_confession_p03/clip1.mp4   (Ad 1)
  outputs/illinois_jdc_memorytrigger_p02/clip1.mp4 (Ad 2)
  outputs/illinois_jdc_stillout_p02/clip1.mp4      (Ad 3)
  outputs/illinois_jdc_youwereakid_p01/clip1.mp4   (Ad 4)
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file as kie_upload, generate_veo as kie_generate_veo, download as kie_download

PERS = Path("outputs/illinois_jdc_ugc/personas_demographic")

COMMON_TAIL = (
    "\nAUDIO CRITICAL: clearly audible at FULL conversational projection, like he's "
    "speaking right into the phone mic. NOT whispered, NOT muttered. Broadcast quality.\n\n"
    "NO on-screen text, NO captions, NO subtitles, NO watermarks."
)

# (ad_slug, anchor, prompt, out)
ADS = [
    (
        "illinois_jdc_confession_p03",
        PERS / "persona_03_reflective_34.png",
        """GAZE: Direct into the phone camera the whole clip; a brief downward glance on "One of the guards" then back to the lens.
BODY: Head mostly still, slow heavy blink, faint jaw tension. No hand gestures.
VOICE: Black man, mid 30s, mature deeper register, quiet and weathered.
TONE: Reflective, heavy, reluctant — a confession held in for years.
SPEED: ~2.4 words per second, slow and deliberate, real pauses between the short sentences.

PRONUNCIATION: "Saint Charles" = full word "Saint".

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "guards".

SPOKEN DIALOGUE (verbatim, stop after final word):
"I was fifteen when it happened. Saint Charles. One of the guards."

After "guards" he holds, eyes on camera, a slow breath. NO further words.""" + COMMON_TAIL,
    ),
    (
        "illinois_jdc_memorytrigger_p02",
        PERS / "persona_02_westside_guarded.png",
        """GAZE: Locked directly on the phone camera the whole clip, intense, almost confrontational.
BODY: Very still, minimal movement, slow blink. Slight head lift on the second sentence.
VOICE: Black man, late 20s, mid-to-low rough register, quiet but firm.
TONE: Visceral, knowing, empathetic-but-direct — he's naming what the viewer is feeling.
SPEED: ~2.4 words per second, slow, weighted, pause between the two sentences.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "juvie".

SPOKEN DIALOGUE (verbatim, stop after final word):
"You remember which one of them it was. You remember which juvie."

After "juvie" he holds, eyes locked on camera. NO further words.""" + COMMON_TAIL,
    ),
    (
        "illinois_jdc_stillout_p02",
        PERS / "persona_02_westside_guarded.png",
        """GAZE: Direct, hard, locked on the phone camera.
BODY: Still, controlled, slight tightening of the jaw on "got away with it". No gestures.
VOICE: Black man, late 20s, mid-to-low register, controlled anger underneath.
TONE: Righteous, controlled fury — accountability, not pleading.
SPEED: ~2.4 words per second, deliberate, a beat before "He got away with it".

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "it".

SPOKEN DIALOGUE (verbatim, stop after final word):
"The staff member who sexually abused you in that juvenile hall? He got away with it."

After "it" he holds, hard eye contact. NO further words.""" + COMMON_TAIL,
    ),
    (
        "illinois_jdc_youwereakid_p01",
        PERS / "persona_01_southside_young.png",
        """GAZE: Direct into the phone camera, steady, unflinching.
BODY: Still, composed, slow blink. Subtle nod after "sexually abused you".
VOICE: Black man, around 20, light-to-mid tenor, steady and clear.
TONE: Stark, righteous, matter-of-fact — stating a hard truth plainly.
SPEED: ~2.4 words per second, deliberate, clear pauses between the three short sentences.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "you".

SPOKEN DIALOGUE (verbatim, stop after final word):
"You were a child. Locked up. And a grown adult sexually abused you."

After "you" he holds, eyes on camera. NO further words.""" + COMMON_TAIL,
    ),
]


def submit_one(ad_slug, anchor, prompt):
    out = Path(f"outputs/{ad_slug}/clip1.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"[{ad_slug}] uploading anchor {anchor.name}", flush=True)
    url = kie_upload(str(anchor))
    print(f"[{ad_slug}] submitting (prompt {len(prompt)} chars)", flush=True)
    r = kie_generate_veo(
        prompt=prompt,
        aspect_ratio="9:16",
        image_urls=[url, url],
        mode="FIRST_AND_LAST_FRAMES_2_VIDEO",
        model="veo3_lite",
        resolution="720p",
    )
    if r["status"] != "success" or not r.get("urls"):
        return ad_slug, "failed", str(r.get("raw"))[:300]
    kie_download(r["urls"][0], str(out))
    return ad_slug, "success", str(out)


def main():
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(submit_one, s, a, p): s for s, a, p in ADS}
        for f in as_completed(futures):
            s = futures[f]
            try:
                slug, status, info = f.result()
                print(f"[{slug}] {status}: {info}", flush=True)
            except Exception as e:
                print(f"[{s}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
