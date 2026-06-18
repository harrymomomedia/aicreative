"""R9 'Mija' v2 — winner script, concerned tone, 12 user-picked hooks (9 Chowchilla / 3 CIW)
with per-hook BRIDGE variants so each discovery mechanism flows into the untouched winner body
("She's like, Mee-hah, you need to look at this..." onward identical). User rule: keep the arc,
keep the second half. FREE google-flow queue; skip-if-exists; [ok] per clip."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests

from cawp_r_batch_gen import AUDIO, LOCKS, VOICE, BODY
from googleflow_client import generate_veo, upload_asset

PERSONA_REF = "outputs/cawp_personas_latina/reference/l2_kitchen.png"
OUT_DIR = "outputs/cawp_r9_mija_l2"
os.makedirs(OUT_DIR, exist_ok=True)

TONE = ("worried and serious, weight in her voice, like telling a younger cousin something "
        "important across the kitchen table. NO smiling, NOT cheerful, NOT salesy - her face "
        "stays earnest and worried, softening only slightly on 'it's not too late'.")

# per-beat overrides (user 2026-06-11: 'switching between worried vs angry')
TONE_ANGRY = ("worried turning to controlled ANGER as she says it - jaw tightens, eyes harden, "
              "voice gets firmer and lower. NOT shouting, NOT smiling, NOT salesy.")
ANGRY_BEATS = {4, 5}  # body4 (guards/sexual abuse), body5 (that happened to me)

MIJA_LOCK = ("PRONUNCIATION LOCK ADDITION: 'Mee-hah' is the Spanish endearment Mija, pronounced "
             "MEE-hah, warm and natural. ")

# hook slug -> (hook line, bridge slug)
HOOKS = {
    "i": ("My cellmate from Chowchilla found me on Facebook last month. That's how this whole thing started.", "cellmate"),
    "j": ("I drove past the exit to Chowchilla last year and my hands started shaking. Twenty years later.", "sister"),
    "k": ("My daughter asked me why I never talk about Chowchilla. I finally have an answer.", "sister"),
    "m": ("An article about Chowchilla sat in my phone for a week before I could open it.", "phone"),
    "o": ("I used to change the channel when prison stuff came on. Then Chowchilla was the headline.", "headline"),
    "p": ("At my mom's funeral, a woman from my old Chowchilla unit pulled me aside. You need to hear this.", "funeral"),
    "q": ("Me and my sister made a promise to never talk about Chowchilla again. I'm breaking it today.", "sister"),
    "s": ("Five women from my old Chowchilla yard already filed. Five. That's how I found out.", "yard"),
    "v": ("I'm fifty-six years old and I just told my husband about Chowchilla last night.", "sister"),
    "y": ("Nobody ever asks what happened to the women from C-I-W. Somebody finally did.", "sister"),
    "x": ("My old bunkie from C-I-W called me crying last week. Good crying. Let me explain.", "bunkie"),
    "z": ("My daughter found out I was at C-I-W from a news story. We finally talked about it.", "daughter"),
}

BRIDGES = {
    "sister": "I buried all that twenty years ago, you know. Then my sister, uh, she sends me this article.",
    "cellmate": "We got to talking, you know, catching up on everything. Then she sends me this article.",
    "phone": "My sister sent it to me, you know. She kept saying, did you read it yet.",
    "headline": "Then one night it's right there on the news. And my sister starts blowing up my phone.",
    "funeral": "She grabbed my hand, you know, and pulled out her phone. Showed me this article.",
    "yard": "One of them called me, you know, from the old yard. She sends me this article.",
    "bunkie": "She could barely get the words out. Then she texts me this article.",
    "daughter": "She sat me down at my own kitchen table and pulled up this article.",
}

# clips 3-10: the winner's second half, UNTOUCHED
BODY_LINES = [
    "She's like, Mee-hah, you need to look at this. Women from the California women's prisons.",
    "They're finding out they may qualify for significant potential compensation for what the guards did to them. Sexual abuse.",
    "And I'm reading it like, that happened to me. That happened to a lot of us in there.",
    "So there's a form. You put, when you were there, what happened. That's it.",
    "Nobody's showing up at your house. It all stays private, between you and the lawyers.",
    "You just find out if you got a case. I filled it out. Took me, like, two minutes.",
    "I'm just saying, Mee-hah, it's not too late. I thought it was, but it's not.",
    "Tap the button. See if you qualify.",
]


def build_prompt(dialogue):
    return (f"GAZE: locked on the camera lens the entire clip. BODY LANGUAGE: {BODY['l2']} "
            f"VOICE STYLE: {VOICE['l2']} TONE: {TONE} "
            f"PACE LOCK: about 2.4 words per second, deliberate, natural pauses kept. "
            f"{AUDIO} {MIJA_LOCK}{LOCKS} "
            f'SPOKEN DIALOGUE (verbatim, no additions, stop after final word): "{dialogue}"')


def gen(out, dialogue, duration=8):
    if os.path.exists(out) and os.path.getsize(out) > 0:
        print(f"[skip] {out}", flush=True)
        return
    try:
        res = generate_veo(build_prompt(dialogue), image_mgid=MGID, duration=duration,
                           aspect_ratio="portrait")
        if res.get("status") != "success" or not res.get("urls"):
            print(f"[FAIL] {out}: {str(res.get('raw'))[:140]}", flush=True)
            return
        data = requests.get(res["urls"][0], timeout=600)
        data.raise_for_status()
        with open(out, "wb") as f:
            f.write(data.content)
        print(f"[ok] {out}", flush=True)
    except Exception as e:
        print(f"[FAIL] {out}: {e}", flush=True)


if __name__ == "__main__":
    MGID = upload_asset(PERSONA_REF)
    print(f"uploaded l2 -> {MGID}", flush=True)
    for slug, (line, _) in HOOKS.items():
        gen(f"{OUT_DIR}/hook_{slug}.mp4", line)
    for bslug, line in BRIDGES.items():
        gen(f"{OUT_DIR}/bridge_{bslug}.mp4", line)
    for i, line in enumerate(BODY_LINES, 3):
        if i in ANGRY_BEATS:
            saved, TONE = TONE, TONE_ANGRY
            gen(f"{OUT_DIR}/body{i}.mp4", line, duration=4 if i == 10 else 8)
            TONE = saved
        else:
            gen(f"{OUT_DIR}/body{i}.mp4", line, duration=4 if i == 10 else 8)
    print("done - r9 mija v2 gen complete", flush=True)
