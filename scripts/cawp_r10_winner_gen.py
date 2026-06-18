"""R10 — the ORIGINAL winning Chowchilla script on 10 new personas (user 2026-06-11):
exact same script per persona, ONLY the first sentence swapped (slight variants).
Compliance fixes as R9: locked phrase + privacy line (no 'nobody's calling you'); Mee-hah respell.
Tone: worried baseline, controlled anger on clips 4-5. 100 clips, FREE google-flow queue."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests

from cawp_r_batch_gen import AUDIO, LOCKS
from googleflow_client import generate_veo, upload_asset

REF = "outputs/cawp_personas_latina/reference"

TONE = ("worried and serious, weight in her voice, like telling a younger cousin something "
        "important. NO smiling, NOT cheerful, NOT salesy - earnest and worried, softening only "
        "slightly on 'it's not too late'.")
TONE_ANGRY = ("worried turning to controlled ANGER as she says it - jaw tightens, eyes harden, "
              "voice gets firmer and lower. NOT shouting, NOT smiling, NOT salesy.")
ANGRY_CLIPS = {4, 5}

MIJA_LOCK = ("PRONUNCIATION LOCK ADDITION: 'Mee-hah' is the Spanish endearment Mija, pronounced "
             "MEE-hah, warm and natural. ")

# persona slug -> (reference image, first sentence variant)
PERSONAS = {
    "l7":  (f"{REF}/l7_laundromat.png",  "Chowchilla women's prison. I was in there fifteen years ago."),
    "l8":  (f"{REF}/l8_backyard.png",    "Chowchilla was, like, twenty years ago for me."),
    "l9":  (f"{REF}/l9_balcony.png",     "Did time at Chowchilla, like, sixteen years back."),
    "l10": (f"{REF}/l10_truck.png",      "Chowchilla. That was twenty-five years ago for me."),
    "l11": (f"{REF}/l11_diningtable.png","It's been twelve years since Chowchilla for me."),
    "l12": (f"{REF}/l12_frontyard.png",  "Me, I was at Chowchilla, like, eighteen years ago."),
    "l14": (f"{REF}/l14_patio.png",      "Thirty years ago I was inside Chowchilla."),
    "l17": (f"{REF}/l17_kitchen2.png",   "Chowchilla was back in the nineties for me."),
    "l19": (f"{REF}/l19_couch2.png",     "I was locked up at Chowchilla, like, twenty-two years ago."),
    "l21": (f"{REF}/l21_bedroom2.png",   "Chowchilla women's prison was ten years ago for me."),
}

BODY_DESC = {
    "l7":  "sitting in a laundromat holding the phone, every washing machine behind her IDLE and STILL, no drums spinning, no motion in the background, small head tilts, natural blinks.",
    "l8":  "in a plastic chair in her backyard holding the phone, slight handheld sway, natural blinks.",
    "l9":  "on her apartment balcony at dusk holding the phone, slight lean in, natural blinks.",
    "l10": "in the passenger seat of a parked truck, engine off, scene outside the window STILL, holding the phone, natural blinks.",
    "l11": "at her dining table holding the phone, lamp light, small nods, natural blinks.",
    "l12": "standing in her front yard holding the phone, the street behind her empty and STILL, no passing cars, slight handheld sway, natural blinks.",
    "l14": "in a rocking chair on her patio holding the phone, gentle movement, natural blinks.",
    "l17": "at her kitchen counter holding the phone, small head tilts, natural blinks.",
    "l19": "in the corner of her couch holding the phone, lamp light, natural blinks.",
    "l21": "sitting against her headboard holding the phone, lamp light, natural blinks.",
}

VOICE = "Latina woman, middle aged, natural everyday speaking voice matching her appearance."

# clips 2-10: the winner verbatim (compliance-fixed), identical for all personas
LINES = [
    "You know, and I moved on. Then my sister, uh, she sends me this article.",
    "She's like, Mee-hah, you need to look at this. Women from the California women's prisons.",
    "They're finding out they may qualify for significant potential compensation for what the guards did to them. Sexual abuse.",
    "And I'm reading it like, that happened to me. That happened to a lot of us in there.",
    "So there's a form. You put, when you were there, what happened. That's it.",
    "Nobody's showing up at your house. It all stays private, between you and the lawyers.",
    "You just find out if you got a case. I filled it out. Took me, like, two minutes.",
    "I'm just saying, Mee-hah, it's not too late. I thought it was, but it's not.",
    "Tap the button. See if you qualify.",
]


BG_LOCK = ("BACKGROUND LOCK: the background stays completely STATIC for the entire clip - "
           "no moving people, no vehicles, no screens, no flickering lights, no swaying objects, "
           "nothing in motion except her. ")


def build_prompt(body, tone, dialogue):
    return (f"GAZE: locked on the camera lens the entire clip. BODY LANGUAGE: {body} {BG_LOCK}"
            f"VOICE STYLE: {VOICE} TONE: {tone} "
            f"PACE LOCK: about 2.4 words per second, deliberate, natural pauses kept. "
            f"{AUDIO} {MIJA_LOCK}{LOCKS} "
            f'SPOKEN DIALOGUE (verbatim, no additions, stop after final word): "{dialogue}"')


def gen(out, prompt, duration=8):
    if os.path.exists(out) and os.path.getsize(out) > 0:
        print(f"[skip] {out}", flush=True)
        return
    try:
        res = generate_veo(prompt, image_mgid=MGID, duration=duration, aspect_ratio="portrait")
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
    for slug, (ref, first_sentence) in PERSONAS.items():
        out_dir = f"outputs/cawp_r10_winner_{slug}"
        os.makedirs(out_dir, exist_ok=True)
        MGID = upload_asset(ref)
        print(f"uploaded {slug} -> {MGID}", flush=True)
        body = BODY_DESC[slug]
        clip1_line = f"{first_sentence} I thought, okay, that part of my life is over."
        gen(f"{out_dir}/clip1.mp4", build_prompt(body, TONE, clip1_line))
        for i, line in enumerate(LINES, 2):
            tone = TONE_ANGRY if i in ANGRY_CLIPS else TONE
            gen(f"{out_dir}/clip{i}.mp4", build_prompt(body, tone, line), duration=4 if i == 10 else 8)
    print("done - r10 winner gen complete", flush=True)
