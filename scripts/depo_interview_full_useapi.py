#!/usr/bin/env python3
"""Full Depo interview ad on the FREE useapi google-flow tier (Veo 3.1 Lite).
Every beat = a TALK clip (speaker) + a LISTEN clip (other person, for the stacked layout).
Listening prompts allow natural ambient audio (forbidding audio trips AUDIO_GENERATION_FILTERED
on the free tier); their audio is muted at stitch time. Skip-if-exists so re-runs resume through
the slow queue / transient failures.

Anchors: surv_face_v1 (subject, gazes screen-right), doc_alone_v1_L (interviewer, gazes left).
Run: .venv/bin/python scripts/depo_interview_full_useapi.py [--only name1,name2]
"""
import argparse, concurrent.futures as cf, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import googleflow_client as gf

REF = Path("outputs/depo_interview/reference")
OUT = Path("outputs/depo_interview/clips_useapi"); OUT.mkdir(parents=True, exist_ok=True)
SURV = str(REF / "surv_face_v1.png")
DOC = str(REF / "doc_alone_v1_L.png")
NOTEXT = "No on-screen text, no captions, no subtitles."

def talk(persona, side, tone, dialogue, pron=""):
    who = ("A weary middle-aged Black woman being interviewed" if persona == "surv"
           else "A warm middle-aged woman documentary interviewer")
    gaze = ("toward the interviewer off-camera on her right, not into the lens" if persona == "surv"
            else "toward the person off-camera on her left, not into the lens")
    return (f"{who}, speaking.\nGAZE: {gaze}.\nBODY: natural, subtle, real blinks and micro-"
            f"expressions.\nTONE: {tone}.\nSPEED: ~2.4 words/sec.\n"
            "AUDIO CRITICAL: speaks CLEARLY at full conversational volume, right into the "
            f"microphone.\n{pron}"
            "DIALOGUE LOCK: English only. Speak ONLY the SPOKEN DIALOGUE, in order, no added/"
            "filler/trailing words; stop after the final word.\n"
            f"SPOKEN DIALOGUE (verbatim): \"{dialogue}\"\n{NOTEXT}")

def listen(persona):
    if persona == "surv":
        return ("A weary middle-aged Black woman listening to an interviewer off-camera on her "
                "right.\nGAZE: on the interviewer to her right.\nBODY: quiet attentiveness, a "
                "slight thoughtful nod, weary natural blinks, a soft breath, a faint 'mm' of "
                "acknowledgement.\nSoft natural room ambience.\n" + NOTEXT)
    return ("A warm documentary interviewer listening intently to the person off-camera on her "
            "left.\nGAZE: on the speaker to her left.\nBODY: attentive stillness, slow empathetic "
            "nods, soft micro-expressions, natural blinks, may glance at her notepad, a faint "
            "'mm-hmm' of acknowledgement.\nSoft natural room ambience.\n" + NOTEXT)

MEN = 'PRONUNCIATION LOCK: "meningioma" = "men-in-jee-OH-muh".\n'

# (name, persona, anchor, prompt)
TALK_BEATS = [
    ("doc_talk_1", "doc", DOC, talk("doc","L","gentle, caring, curious",
        "When they told you it was a brain meningioma, did anyone ever explain why you got it?", MEN)),
    ("surv_talk_1", "surv", SURV, talk("surv","R","resigned, matter-of-fact, she believed it for years",
        "No. Bad luck, they kept saying. Over and over. And for a long time, I believed that.")),
    ("doc_talk_2", "doc", DOC, talk("doc","L","gently probing",
        "So what changed your mind about it just being bad luck?")),
    ("surv_talk_2", "surv", SURV, talk("surv","R","quiet, steady, a little disbelief",
        "A lawyer showed me the studies. Women on the Depo shot for over a year were up to five times more likely to get one.")),
    ("surv_talk_3", "surv", SURV, talk("surv","R","firm, wounded, plain",
        "Five times. That is not bad luck. And nobody ever warned me.")),
    ("doc_talk_3", "doc", DOC, talk("doc","L","warm, reassuring",
        "And you are not alone in this. So many other women are finding out the very same thing.")),
    ("surv_talk_4", "surv", SURV, talk("surv","R","steady, connected, resolve",
        "Not even close. Thousands of women. Same diagnosis, same shot. There is a federal lawsuit now.")),
    ("doc_talk_4", "doc", DOC, talk("doc","L","practical, gentle",
        "So what can someone actually do about it? Where would a person even start?")),
    ("surv_talk_5", "surv", SURV, talk("surv","R","helpful, calm, encouraging",
        "You answer a few private questions online. Your diagnosis, how long you were on Depo. It takes about a minute.")),
    ("surv_talk_6", "surv", SURV, talk("surv","R","warm, reassuring, low-key",
        "A lawyer reviews it for free. No court, it is confidential, and even if it was years ago, you may still qualify.")),
    ("doc_cta", "doc", DOC, (
        "A warm middle-aged woman documentary interviewer speaking DIRECTLY INTO the camera lens "
        "to the viewer.\nGAZE: straight into the lens, addressing the viewer.\nBODY: calm, sincere, "
        "a small caring nod.\nTONE: warm, direct, trustworthy, unhurried.\nSPEED: ~2.4 words/sec.\n"
        "AUDIO CRITICAL: clear, full conversational volume into the microphone.\n" + MEN +
        "DIALOGUE LOCK: English only. Speak ONLY the SPOKEN DIALOGUE, no added/filler/trailing "
        "words; stop after the final word.\n"
        "SPOKEN DIALOGUE (verbatim): \"If you or someone you love has a brain meningioma and was "
        "ever on Depo, you may qualify for significant compensation. Tap below and take the "
        "two-minute check.\"\n" + NOTEXT)),
]

# listening clips (one per beat, the OTHER persona) — not needed for the CTA (full-frame)
LISTEN_BEATS = []
for name, persona, _, _ in TALK_BEATS:
    if name == "doc_cta":
        continue
    other = "surv" if persona == "doc" else "doc"
    anchor = SURV if other == "surv" else DOC
    LISTEN_BEATS.append((f"{other}_listen_for_{name}", other, anchor, listen(other)))

ALL = TALK_BEATS + LISTEN_BEATS

def gen(item):
    name, persona, anchor, prompt = item
    out = OUT / f"{name}.mp4"
    if out.exists():
        print(f"[skip] {out}"); return
    print(f"[gen ] {name}")
    res = gf.generate_veo(prompt, image_path=anchor, duration=8, aspect_ratio="portrait")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {name}: {str(res.get('raw'))[:140]}"); return
    gf.download(res["urls"][0], out); print(f"[done] {out}")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only", default="")
    a = ap.parse_args()
    items = ALL
    if a.only:
        keep = set(a.only.split(",")); items = [i for i in ALL if i[0] in keep]
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(gen, items))
    print("ALL DONE")

if __name__ == "__main__":
    main()
