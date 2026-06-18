"""cawp clip generation — F1 news-reaction (persona l4) + F5 three-questions announcer (persona l1).
FREE google-flow Veo 3.1 Lite low-priority (slow queue, $0). 8s clips, portrait.
Tone variants per feedback_video_tone_variants. Sequential submits, skip-if-exists.
Prints one '[ok] <path>' line per landed clip (monitor-friendly)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests

from googleflow_client import generate_veo, upload_asset

PERSONAS = {
    "l4": "outputs/cawp_personas_latina/reference/l4_porch.png",
    "l1": "outputs/cawp_personas_latina/reference/l1_car.png",
}

AUDIO = ("AUDIO CRITICAL: she speaks CLEARLY AUDIBLY at full conversational projection into the "
         "phone microphone, clean foreground audio, NOT whispered, NOT muttered.")

LOCKS = ("PRONUNCIATION LOCK: 'Chowchilla' is pronounced 'Chow-chill-uh'; 'C-I-W' is spoken as the "
         "three letters, see eye double-you. CRITICAL DIALOGUE LOCK: she speaks ENGLISH ONLY. Speak "
         "ONLY the words listed in SPOKEN DIALOGUE, in order, with no fillers, no insertions, no "
         "trailing words, and STOP speaking after the final word. Her dark-brown eyes stay the SAME "
         "color throughout, open and on the lens. ABSOLUTELY NO on-screen text, no captions, no "
         "subtitles.")


def build_prompt(gaze, body, voice, tone, dialogue):
    return (f"GAZE: {gaze} BODY LANGUAGE: {body} VOICE STYLE: {voice} TONE: {tone} "
            f"PACE LOCK: about 2.4 words per second, deliberate, each line given weight. "
            f"{AUDIO} {LOCKS} "
            f'SPOKEN DIALOGUE (verbatim, no additions, stop after final word): "{dialogue}"')


F1_DIALOGUE = [
    "Stop scrolling, look at this headline real quick. Two hundred twenty-four years. That's what that guard from Chowchilla got.",
    "Last year. And this one, that's the Justice Department investigating both women's prisons, Chowchilla and C-I-W.",
    "And this one. Almost five hundred women already filed. These are real news stories, you can look up every one.",
    "So here's what I'm telling you. If staff sexually abused you in either of those prisons, this is the time.",
    "You may qualify for significant potential compensation. The form's at the link below, and it's three things, basically.",
    "Where you were, when, what happened. Couple minutes, it's private, and it costs nothing to check.",
    "If a lawyer calls you after, that stays between you two. Don't just watch this and keep scrolling.",
    "Tap the link and answer those questions. That part only you can do.",
]

F5_DIALOGUE = [
    "Three quick questions for the women who did time in California. One. Were you ever at Chowchilla or C-I-W?",
    "Two. Did a guard or any staff member ever cross the line with you sexually? Even once.",
    "Even if he was never reported. Three. Have you kept it to yourself all these years?",
    "If that's three yeses, stop scrolling, because this is for you.",
    "What they did was sexual abuse, and you may qualify for significant potential compensation.",
    "The same form almost five hundred women already used is linked under this video.",
    "It asks where, when, and what happened. Your answers are private, the call after is private too.",
    "And checking costs you nothing. You just answered three questions for me right now.",
    "The form is barely more than that. Tap it and finish what you started.",
]

F1_VOICE = "Latina woman, late forties, natural everyday speaking voice."
F5_VOICE = "Latina woman, around fifty, natural everyday speaking voice."

F1_BODY = ("slight handheld sway like a held phone, leans in a touch on key words, natural blinks, "
           "small emphatic nods.")
F1_BODY_POINT = ("slight handheld sway like a held phone, natural blinks. Once during the clip her "
                 "free hand comes up ALREADY FORMED as a pointing finger aimed straight UP above "
                 "her head toward the headline above her, holds a beat, then lowers. The hand never "
                 "covers her face.")
F5_BODY = ("seated in the PARKED car, engine off, the scene outside the windows completely STILL, "
           "slight lean toward the lens, a small emphatic hand gesture rising into frame now and "
           "then, natural blinks.")

GAZE_LENS = "locked on the camera lens the entire clip."
GAZE_GLANCE = ("on the camera lens; once, on a reference to the headline, a quick glance up and "
               "immediately back to the lens.")

F1_TONES = {
    "concerned": ("concerned and urgent, like warning a friend about something serious she just "
                  "found out. NOT salesy, NOT newscaster, NOT cheerful."),
    "anger": ("controlled anger rising under the words, firm and pointed, jaw set. NOT shouting, "
              "NOT salesy, NOT cheerful."),
}
F5_TONES = {
    "firedup": ("fired up, voice raised, calling the whole state out, near-shouting but controlled "
                "and real. NOT cheerful, NOT TV-ad voice."),
    "stern": ("dead serious and stern, low controlled urgency, like a hard warning from someone who "
              "was there. NOT salesy, NOT cheerful."),
    "heavy": ("heavy and sad through the questions, quiet weight in the voice, lifting into calm "
              "resolve on the final sentence. NOT salesy, NOT cheerful."),
}


def jobs():
    # interleave tone-A waves first so both ads get early signal, then the other tones
    waves = [
        ("f1", "l4", "concerned"), ("f5", "l1", "firedup"),
        ("f1", "l4", "anger"), ("f5", "l1", "stern"), ("f5", "l1", "heavy"),
    ]
    for ad, persona, tone in waves:
        dialogue = F1_DIALOGUE if ad == "f1" else F5_DIALOGUE
        for i, line in enumerate(dialogue, 1):
            yield ad, persona, tone, i, line


def main():
    mgids = {}
    for slug, path in PERSONAS.items():
        mgids[slug] = upload_asset(path)
        print(f"uploaded {slug} -> {mgids[slug]}", flush=True)

    for ad, persona, tone, i, line in jobs():
        out_dir = f"outputs/cawp_{ad}_{persona}"
        os.makedirs(out_dir, exist_ok=True)
        out = f"{out_dir}/clip{i}_{tone}.mp4"
        if os.path.exists(out) and os.path.getsize(out) > 0:
            print(f"[skip] {out}", flush=True)
            continue
        if ad == "f1":
            gaze = GAZE_GLANCE if i <= 3 else GAZE_LENS
            body = F1_BODY_POINT if i <= 3 else F1_BODY
            prompt = build_prompt(gaze, body, F1_VOICE, F1_TONES[tone], line)
        else:
            prompt = build_prompt(GAZE_LENS, F5_BODY, F5_VOICE, F5_TONES[tone], line)
        try:
            res = generate_veo(prompt, image_mgid=mgids[persona], duration=8, aspect_ratio="portrait")
            if res.get("status") != "success" or not res.get("urls"):
                print(f"[FAIL] {out}: {str(res.get('raw'))[:160]}", flush=True)
                continue
            data = requests.get(res["urls"][0], timeout=600)
            data.raise_for_status()
            with open(out, "wb") as f:
                f.write(data.content)
            print(f"[ok] {out}", flush=True)
        except Exception as e:
            print(f"[FAIL] {out}: {e}", flush=True)
    print("done — all waves complete", flush=True)


if __name__ == "__main__":
    main()
