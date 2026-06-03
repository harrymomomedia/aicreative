"""Tort IL JDC — single-person UGC testimonial ads (#1 whistleblower, #4 brother, #5 cousin/Audy).
Front-loaded scripts: sexual-abuse + juvenile-detention context + "significant compensation" land in
the first 1-2 beats. Child-safety split: the "sexually abused" line is never in the same clip as a
kid/juvenile/juvie word. Direct-to-lens testimonial register. KIE veo3_lite, FIRST_AND_LAST_FRAMES.
clip01 from the picked persona still; clips 02+ from eyes-open anchors rotated off clip01.

  python scripts/jdc_tort_gen.py <whis|bro|fam> test   # clip01 (+ clip02 for whis) off the still
  python scripts/jdc_tort_gen.py <whis|bro|fam>         # full: clip01 -> anchors -> rest
"""
import sys, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from googleflow_client import generate_veo, upload_asset, download   # FREE veo-3.1-lite-low-priority

PRON_PLAIN = "Natural clear American English."


def P(reg, voice, line, tone, body, pron, last):
    return f"""He is talking directly into his phone's front camera, filming a candid selfie testimonial. {reg}
GAZE: steady direct eye contact into the phone lens, addressing the viewer; natural blinks, an occasional brief glance away then back. Warm dark-brown eyes, OPEN, staying the SAME color throughout (never lighter or changing).
BODY: small natural movements. {body}
VOICE: {voice}
TONE: {tone}
SPEED: about 2.5 words per second, deliberate, each word given weight.
AUDIO CRITICAL: he speaks clearly and fully audibly at a close conversational volume right into the phone mic. NOT whispered, NOT muttered.
PRONUNCIATION: {pron}
DIALOGUE LOCK: English only. Say ONLY the words in SPOKEN DIALOGUE, in order. No fillers (no uh, um, like, you know), no extra or trailing words, no repetition. Stop after the final word "{last}".
NO on-screen text, NO captions, NO subtitles, NO watermark.
SPOKEN DIALOGUE (verbatim, stop after final word): "{line}\""""

VIDEOS = {
    "whis": {
        "anchor": "outputs/illinois_jdc_tort_whistleblower/reference/whis3.png",
        "out": "outputs/illinois_jdc_tort_whistleblower",
        "reg": "He is a calm, weathered older man in his late 40s — a former juvenile-facility staff member who finally decided to talk.",
        "voice": "a low, steady older man's voice, late 40s, gravelly and grounded, plain-spoken, NOT young.",
        "clips": [
            ("clip01", "I worked inside St. Charles, one of Illinois' juvenile centers, for ten years. If you were a kid in there, hear me out.",
             "Serious, weathered, bracing to speak.", "A slow breath before he starts.",
             '"St. Charles" plainly as "saint charles". "Illinois" = "ill-uh-NOY". "juvenile" = "JOO-vuh-nile".'),
            ("clip02", "I watched staff sexually abuse the people locked up in there. And the state is finally being sued for it.",
             "Grave, unflinching, matter-of-fact.", "Steady gaze, a slight tightening of the jaw.",
             'say "sexually abuse" clearly and plainly.'),
            ("clip03", "If that was you, you may qualify for significant compensation. Nearly a thousand people have already come forward.",
             "Direct and credible, leaning in.", "A small nod.", '"Illinois" plainly.'),
            ("clip04", "I know how they did it. Privileges, phone time, snacks, on the ones nobody checked on. The showers, room checks at night.",
             "Knowing, heavy.", "Slight shake of the head.", PRON_PLAIN),
            ("clip05", "And when a kid spoke up, they landed in the hole. I stayed quiet too long.",
             "Regretful, resolved.", "Eyes lower for a beat, then back to the lens.", PRON_PLAIN),
            ("clip06", "There's no deadline anymore. Tap below, put in your name and number. It's free, confidential, you never see a courtroom.",
             "Caring, direct, sincere, NOT salesy.", "Calm steady eye contact, a small nod toward the button.", PRON_PLAIN),
        ],
    },
    "bro": {
        "anchor": "outputs/illinois_jdc_tort_brother/reference/bro5.png",
        "out": "outputs/illinois_jdc_tort_brother",
        "reg": "He is an ordinary man in his late 30s speaking for his younger brother, protective and holding back anger.",
        "voice": "a steady man's voice, late 30s, grounded and controlled, a protective edge underneath.",
        "clips": [
            ("clip01", "My little brother got locked up in an Illinois juvenile center at fifteen. He came home different and never told anyone why.",
             "Protective, controlled, jaw set.", "A slow breath, eyes steady.",
             '"Illinois" = "ill-uh-NOY". "juvenile" = "JOO-vuh-nile".'),
            ("clip02", "I'll tell you why. A staff member sexually abused him in there. And he's not the only one. Nearly a thousand people are suing Illinois.",
             "Heavier, quiet anger, then steadying.", "Looks down for a beat, then back to the lens.",
             'say "sexually abused" clearly and plainly. "Illinois" plainly.'),
            ("clip03", "If somebody you love came back from an Illinois juvie and shut down, this might be why. And there may be significant compensation.",
             "Direct to the viewer, sincere.", "Leans a touch closer.", '"juvie" = "JOO-vee".'),
            ("clip04", "It's confidential, it's free, he never goes to court. LA County just settled cases like this for billions.",
             "Reassuring, then a spark of this-is-real.", "Eyebrows lift slightly.", '"LA" = the letters "ell-ay".'),
            ("clip05", "If this is you, or somebody you love, tap below. Just a name and number. No deadline, and nobody has to know.",
             "Warm, protective, a caring nudge to act; sincere, NOT salesy.", "Direct into the lens, small nod.", PRON_PLAIN),
        ],
    },
    "fam": {
        "anchor": "outputs/illinois_jdc_tort_family/reference/fam2.png",
        "out": "outputs/illinois_jdc_tort_family",
        "reg": "He is an ordinary man in his early 30s, calm and heavy, telling the truth plainly into the camera.",
        "voice": "a calm man's voice, early 30s, low and matter-of-fact, carrying weight but steady.",
        "clips": [
            ("clip01", "Me and my cousin were both locked up at the Audy Home, Cook County juvenile detention, years apart. Same place, same kind of staff.",
             "Matter-of-fact, grounded.", "Steady, a small shrug.",
             '"Audy Home" = "AW-dee home". "Cook County" plainly. "juvenile" = "JOO-vuh-nile".'),
            ("clip02", "We both got sexually abused in there. Didn't tell each other till last year. Turns out it's nearly a thousand of us suing the state.",
             "Quiet, then steadier as the number lands.", "Eyes drop for a beat, then back.",
             'say "sexually abused" clearly and plainly.'),
            ("clip03", "We may both qualify for significant compensation. There's no deadline in Illinois. Hasn't been since twenty fourteen.",
             "Grounded, informative.", "A slight nod.", '"Illinois" = "ill-uh-NOY".'),
            ("clip04", "Nobody believes a kid over a guard. That was the whole bet back then. Not anymore.",
             "A flicker of anger, then resolve.", "Brows pull together, then ease.", PRON_PLAIN),
            ("clip05", "If it hit two people in my family, it hit somebody in yours. Tap below, name and number. Free, confidential, no courtroom.",
             "Direct to the viewer, sincere, NOT salesy.", "Steady eye contact, small nod toward the button.", PRON_PLAIN),
        ],
    },
}


def last_word(s):
    import re
    t = re.findall(r"[A-Za-z']+", s)
    return t[-1] if t else ""


def gen(v, clip, anchor_mgid):
    cid, line, tone, body, pron = clip
    out = Path(VIDEOS[v]["out"]) / f"{cid}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 50000:
        return cid, "cached"
    prompt = P(VIDEOS[v]["reg"], VIDEOS[v]["voice"], line, tone, body, pron, last_word(line))
    r = generate_veo(prompt=prompt, image_mgid=anchor_mgid, duration=8, aspect_ratio="portrait")
    if r.get("status") != "success" or not r.get("urls"):
        return cid, "FAILED: " + str(r.get("raw"))[:200]
    download(r["urls"][0], str(out))
    return cid, "success"


def main():
    v = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "full"
    cfg = VIDEOS[v]
    still_mgid = upload_asset(cfg["anchor"])               # upload persona still once → startImage mgid
    print(f"[{v}] anchor uploaded (mgid)", flush=True)
    if mode in ("test", "clip01"):
        clips = cfg["clips"][:2] if (mode == "test" and v == "whis") else cfg["clips"][:1]
        for c in clips:
            print(f"[{v}] {gen(v, c, still_mgid)}", flush=True)
        return
    # full: clip01 off the still
    print(f"[{v}] {gen(v, cfg['clips'][0], still_mgid)}", flush=True)
    # eyes-open anchors off clip01 → upload each → rotate
    adir = Path(cfg["out"]) / "anchors"
    if not list(adir.glob("_anchor_*.jpg")):
        subprocess.run([".venv/bin/python", "scripts/pick_clean_anchors.py", str(Path(cfg["out"]) / "clip01.mp4"),
                        "--out-dir", str(adir), "--n", "6", "--prefix", "_anchor"], check=False)
    anchors = sorted(adir.glob("_anchor_*.jpg"))
    amgids = [upload_asset(str(a), "image/jpeg") for a in anchors] or [still_mgid]
    print(f"[{v}] {len(amgids)} eyes-open anchors", flush=True)
    for i, c in enumerate(cfg["clips"][1:]):
        print(f"[{v}] {gen(v, c, amgids[i % len(amgids)])}", flush=True)


if __name__ == "__main__":
    main()
