"""Tier-2 ads — clip 1 of each (establishes persona), parallel on KIE Veo 3.1 Lite.

Ad 5 (Pattern Interrupt / "Stop scrolling")  -> persona 2 (westside guarded)
Ad 6 (The Secret You Never Told)             -> persona 3 (reflective 34)
Ad 7 (Stat Shock)                            -> persona 1 (southside young)
Ad 8 (They Kept You Quiet)                   -> persona 1 (southside young)

Short i2v prompts (persona/setting in the anchor PNG). Neutral voice descriptors
(no racial term) — identity carried by the anchor; voice unified at finalize.
Em-dashes stripped from spoken lines. Outputs: outputs/<slug>/clip1.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file as kie_upload, generate_veo as kie_generate_veo, download as kie_download

PERS = Path("outputs/illinois_jdc_ugc/personas_demographic")
P1 = PERS / "persona_01_southside_young.png"
P2 = PERS / "persona_02_westside_guarded.png"
P3 = PERS / "persona_03_reflective_34.png"

TAIL = (
    "\nAUDIO CRITICAL: clearly audible at FULL conversational projection, NOT whispered, "
    "NOT muttered. Broadcast quality.\n\nNO on-screen text, NO captions, NO subtitles, NO watermarks."
)

AD5_C1 = """\
GAZE: Snaps directly into the phone lens on "Stop scrolling", then holds hard, locked. Warm dark-brown eyes, same color throughout, open.
BODY: Still, controlled, a sharp settle on the first two words. No gestures.
VOICE: man, late 20s, mid-to-low rough register.
TONE: Pattern-interrupt command — arresting, confrontational, then direct and exclusionary. NOT salesy.
SPEED: ~2.4 words/sec, punchy on the open, deliberate after.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "you".

SPOKEN DIALOGUE (verbatim, stop after final word):
"Stop scrolling. If a guard or staff sexually abused you inside an Illinois juvenile hall, this is for you."

After "you" he holds, hard eye contact. NO further words.""" + TAIL

AD6_C1 = """\
GAZE: Into the lens, quiet, knowing, intimate. A small searching look on "Did you?". Warm dark-brown eyes, same color throughout, open.
BODY: Head still, slow blink, faint lean in. No gestures.
VOICE: man, mid 30s, mature deeper register, weathered.
TONE: Intimate, gentle, knowing — a question only a survivor answers yes to. NOT performative.
SPEED: ~2.4 words/sec, slow, real beat before "Did you?".

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "you".

SPOKEN DIALOGUE (verbatim, stop after final word):
"You never told anybody what that guard did to you in there. Did you?"

After "you" he holds, soft eye contact. NO further words.""" + TAIL

AD7_C1 = """\
GAZE: Direct into the lens, steady, clear. Warm dark-brown eyes, same color throughout, open.
BODY: Still, composed, a single slow nod. No gestures.
VOICE: man, around 20, light-to-mid tenor, clear.
TONE: Matter-of-fact credibility — stating a real, surprising number. Grounded, not hyped.
SPEED: ~2.4 words/sec, deliberate, even.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "forward".

SPOKEN DIALOGUE (verbatim, stop after final word):
"Almost a thousand people have already come forward."

After "forward" he holds, steady eye contact. NO further words.""" + TAIL

AD8_C1 = """\
GAZE: Into the lens, hard, steady. Warm dark-brown eyes, same color throughout, open.
BODY: Still, controlled, slight jaw tension on "mouth shut". No gestures.
VOICE: man, around 20, light-to-mid tenor, clear.
TONE: Controlled outrage, validating — naming what the perpetrator did. Firm, NOT pleading.
SPEED: ~2.4 words/sec, deliberate, weight on "keep your mouth shut".

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "shut".

SPOKEN DIALOGUE (verbatim, stop after final word):
"The guard who sexually abused you told you to keep your mouth shut."

After "shut" he holds, hard eye contact. NO further words.""" + TAIL

# (slug, persona_png, prompt)
ADS = [
    ("illinois_jdc_stopscroll_p02", P2, AD5_C1),
    ("illinois_jdc_secret_p03",     P3, AD6_C1),
    ("illinois_jdc_statshock_p01",  P1, AD7_C1),
    ("illinois_jdc_keptquiet_p01",  P1, AD8_C1),
]


def submit_one(slug, anchor, prompt):
    out = Path(f"outputs/{slug}/clip1.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 100_000:
        return slug, "skip", f"{out} exists"
    print(f"[{slug}] upload {anchor.name}", flush=True)
    url = kie_upload(str(anchor))
    print(f"[{slug}] submit ({len(prompt)} chars)", flush=True)
    r = kie_generate_veo(
        prompt=prompt,
        aspect_ratio="9:16",
        image_urls=[url, url],
        mode="FIRST_AND_LAST_FRAMES_2_VIDEO",
        model="veo3_lite",
        resolution="720p",
    )
    if r["status"] != "success" or not r.get("urls"):
        return slug, "FAILED", str(r.get("raw"))[:300]
    kie_download(r["urls"][0], str(out))
    return slug, "success", str(out)


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
