"""Depo-Provera brain-meningioma — First-Person Testimonial UGC ad (diagnosis-first).
Messenger: ordinary Black woman ~45. Two anchors (p4 porch/locs, p5 couch/headwrap), SAME script (A/B).
Diagnosis-first arc: meningioma hook -> not-your-fault -> Depo link -> never warned/not alone ->
compensation (compliant) -> kill objections -> CTA. Into-lens soft confession register.
Free google-flow veo-3.1-lite-low-priority, startImage i2v. clip01 off the persona still; clips 02+
off eyes-open anchors rotated from clip01.

  python scripts/depo_testimonial_gen.py both test   # clip01 on BOTH personas (QA test)
  python scripts/depo_testimonial_gen.py p4          # full 7-clip ad (p4)
  python scripts/depo_testimonial_gen.py p5
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from googleflow_client import generate_veo, upload_asset, download   # FREE veo-3.1-lite-low-priority

PRON_PLAIN = "Natural clear American English."
MEN = '"meningioma" = "men-in-jee-OH-muh".'
DEPO = '"Depo" = "DEP-oh".'

# (cid, line, duration, tone, body, pronunciation)
CLIPS = [
    ("clip01", "When the doctor said the words brain tumor, everything just stopped. A meningioma.", 6,
     "Shaken, intimate, holding the emotion back.", "A slow breath before she starts, a small shake of the head.", MEN),
    ("clip02", "I kept asking where it came from. I ate right. I did everything right.", 6,
     "Searching, vulnerable, quietly bewildered.", "A faint shrug, eyes drop for a beat then back to the lens.", PRON_PLAIN),
    ("clip03", "The one thing I'd done for years was the Depo shot. Every three months, like clockwork.", 8,
     "Quiet realization settling in.", "A slow nod.", DEPO),
    ("clip04", "Nobody ever warned me it could do this. And it turns out, I'm not the only one.", 8,
     "A flicker of anger, then steadying.", "Jaw tightens, then eases.", PRON_PLAIN),
    ("clip05", "Women diagnosed with a meningioma after that shot may qualify for significant compensation.", 6,
     "Steadier, informative, grounded.", "A slight nod.", MEN),
    ("clip06", "It's free and private to check. You don't go to court, and an attorney handles everything quietly.", 8,
     "Reassuring, sincere, NOT salesy.", "Calm, a small reassuring nod.", PRON_PLAIN),
    ("clip07", "If you have a meningioma and you were on the Depo shot, tap below and see if you qualify.", 8,
     "Warm, direct, a caring nudge to act; sincere, NOT salesy.", "Steady eye contact, a small nod toward the button.",
     MEN + " " + DEPO),
]

PERSONAS = {
    "p4": {
        "anchor": "outputs/depo_testimonial/persona_04_porch_angular_locs.png",
        "out": "outputs/depo_testimonial/p4_porch",
        "reg": "She is an ordinary Black woman about 45, weathered and tired, filming a candid selfie testimonial on her phone.",
        "voice": "a weary middle-aged Black woman's voice, about 45, low and a little hoarse, plain-spoken, NOT young.",
    },
    "p5": {
        "anchor": "outputs/depo_testimonial/persona_05_couch_full_headwrap.png",
        "out": "outputs/depo_testimonial/p5_headwrap",
        "reg": "She is an ordinary Black woman about 45, heavyset and weary, filming a candid selfie testimonial on her phone.",
        "voice": "a soft, tired middle-aged Black woman's voice, about 45, warm and low, with a slight heaviness, NOT young.",
    },
}


def P(reg, voice, line, tone, body, pron, last):
    return f"""She is talking directly into her phone's front camera, filming a candid selfie testimonial. {reg}
GAZE: soft, direct eye contact into the phone lens, confiding to the viewer; natural blinks, an occasional brief glance down then back. Warm dark-brown eyes, OPEN, staying the SAME color throughout (never lighter or changing).
BODY: small natural movements. {body}
VOICE: {voice}
TONE: {tone}
SPEED: about 2.3 words per second, slow and deliberate, each word given weight.
AUDIO CRITICAL: she speaks clearly and fully audibly at a close conversational volume right into the phone mic. NOT whispered, NOT muttered.
PRONUNCIATION: {pron}
DIALOGUE LOCK: English only. Say ONLY the words in SPOKEN DIALOGUE, in order. No fillers (no uh, um, like, you know), no extra or trailing words, no repetition. Stop after the final word "{last}".
NO on-screen text, NO captions, NO subtitles, NO watermark.
SPOKEN DIALOGUE (verbatim, stop after final word): "{line}\""""


def last_word(s):
    t = re.findall(r"[A-Za-z']+", s)
    return t[-1] if t else ""


def gen(pkey, clip, anchor_mgid):
    cid, line, dur, tone, body, pron = clip
    out = Path(PERSONAS[pkey]["out"]) / f"{cid}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 50000:
        return cid, "cached"
    prompt = P(PERSONAS[pkey]["reg"], PERSONAS[pkey]["voice"], line, tone, body, pron, last_word(line))
    r = generate_veo(prompt=prompt, image_mgid=anchor_mgid, duration=dur, aspect_ratio="portrait")
    if r.get("status") != "success" or not r.get("urls"):
        return cid, "FAILED: " + str(r.get("raw"))[:200]
    download(r["urls"][0], str(out))
    return cid, "success"


def run_persona(pkey, mode):
    cfg = PERSONAS[pkey]
    still_mgid = upload_asset(cfg["anchor"])
    print(f"[{pkey}] anchor uploaded", flush=True)
    if mode == "test":
        print(f"[{pkey}] clip01 -> {gen(pkey, CLIPS[0], still_mgid)}", flush=True)
        return
    # full: clip01 off the still
    print(f"[{pkey}] clip01 -> {gen(pkey, CLIPS[0], still_mgid)}", flush=True)
    adir = Path(cfg["out"]) / "anchors"
    if not list(adir.glob("_anchor_*.jpg")):
        subprocess.run([".venv/bin/python", "scripts/pick_clean_anchors.py", str(Path(cfg["out"]) / "clip01.mp4"),
                        "--out-dir", str(adir), "--n", "6", "--prefix", "_anchor"], check=False)
    anchors = sorted(adir.glob("_anchor_*.jpg"))
    amgids = [upload_asset(str(a), "image/jpeg") for a in anchors] or [still_mgid]
    print(f"[{pkey}] {len(amgids)} eyes-open anchors", flush=True)
    for i, c in enumerate(CLIPS[1:]):
        print(f"[{pkey}] {c[0]} -> {gen(pkey, c, amgids[i % len(amgids)])}", flush=True)


def main():
    who = sys.argv[1] if len(sys.argv) > 1 else "both"
    mode = sys.argv[2] if len(sys.argv) > 2 else "full"
    keys = ["p4", "p5"] if who == "both" else [who]
    for k in keys:
        run_persona(k, mode)


if __name__ == "__main__":
    main()
