"""cawp R-batch — the approved real-story scripts (R1-R7; R8 medical held for firm sign-off).
ONE version per ad (user rule 2026-06-10: no tone/persona variants): one persona, one tone each.
FREE google-flow Veo 3.1 Lite low-priority, 8s clips, portrait, i2v from approved Latina refs.
Real basis per script: inventory/womens_prison_testimonial_research.md. Skip-if-exists; prints
'[ok] <path>' per landed clip (monitor-friendly)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests

from googleflow_client import generate_veo, upload_asset

PERSONAS = {
    "l1": "outputs/cawp_personas_latina/reference/l1_car.png",
    "l2": "outputs/cawp_personas_latina/reference/l2_kitchen.png",
    "l4": "outputs/cawp_personas_latina/reference/l4_porch.png",
}
VOICE = {
    "l1": "Latina woman, around fifty, natural everyday speaking voice.",
    "l2": "Latina woman, mid fifties, natural everyday speaking voice.",
    "l4": "Latina woman, late forties, natural everyday speaking voice.",
}
BODY = {
    "l1": "seated in the PARKED car, engine off, the scene outside the windows completely STILL, slight lean toward the lens, small hand gestures, natural blinks.",
    "l2": "leaning on the kitchen counter holding the phone, small head tilts, natural blinks.",
    "l4": "sitting on the porch steps holding the phone, slight handheld sway, natural blinks, small nods.",
}

AUDIO = ("AUDIO CRITICAL: she speaks CLEARLY AUDIBLY at full conversational projection into the "
         "phone microphone, clean foreground audio, NOT whispered, NOT muttered.")
LOCKS = ("PRONUNCIATION LOCK: 'Chowchilla' is pronounced 'Chow-chill-uh'; 'C-I-W' is spoken as the "
         "three letters, see eye double-you. CRITICAL DIALOGUE LOCK: she speaks ENGLISH ONLY. Speak "
         "ONLY the words listed in SPOKEN DIALOGUE, in order, with no fillers, no insertions, no "
         "trailing words, and STOP speaking after the final word. Her dark-brown eyes stay the SAME "
         "color throughout, open and on the lens. ABSOLUTELY NO on-screen text, no captions, no "
         "subtitles.")

SCRIPTS = {
    "r1_niceone": {
        "persona": "l2",
        "tone": ("quiet and reflective, a little sad, like admitting something she finally "
                 "understands. NOT salesy, NOT cheerful."),
        "lines": [
            "Nobody warns you about the nice one. That's the messed up part.",
            "At Chowchilla the mean guards, whatever, you knew what they were. It was the friendly one you had to watch.",
            "Always asking how you're doing. Little favors. Extra phone time. Maybe he leaves something for you.",
            "I thought he actually cared. He didn't. It was a setup the whole time.",
            "What came after was sexual abuse. Took me years to even use those words.",
            "If that happened to you, lawyers are on these cases now. You may qualify for significant potential compensation.",
            "And listen, it counts even if he never forced you. You were locked up. You couldn't really say no.",
            "The form's short. When you were there, what happened. All of it stays between you and the firm.",
            "It's confusing when he was nice to you. It still wasn't okay. Tap below, see if you qualify.",
        ],
    },
    "r2_believed": {
        "persona": "l4",
        "tone": ("building conviction, visibly moved at the verdict, steadier and resolute by the "
                 "end. NOT salesy, NOT newscaster."),
        "lines": [
            "Whole time I was at Chowchilla I told myself one thing. Nobody's ever gonna believe us.",
            "We're felons, right? Our word against a guard? Come on. That's how I thought for years.",
            "Then last year I watched the news and women from that prison got up on the stand.",
            "Some still locked up, testifying about the sexual abuse those guards put on them. And the jury believed them.",
            "That officer got two hundred twenty-four years. I cried in my kitchen, I'm not even gonna lie.",
            "So if a guard sexually abused you in there, it's different now. You may qualify for significant potential compensation.",
            "Almost five hundred women have already filed. Real cases, real lawyers. The feds are investigating both prisons.",
            "You fill out a private form, what happened and when. If they call you, nobody else ever knows.",
            "I waited twenty years for proof somebody would listen. We got it. Tap below, see if you qualify.",
        ],
    },
    "r3_ididtell": {
        "persona": "l1",
        "tone": ("level and hard, controlled, zero self-pity, firm at the end. NOT salesy, "
                 "NOT cheerful."),
        "lines": [
            "Everybody asks why the women at Chowchilla didn't report it. Some of us did. Let me explain what happened then.",
            "A woman I knew told them what a guard was doing to her. They threw her in the SHU.",
            "Called it protection. Then they shipped her up north, away from her kids. Case closed, insufficient evidence.",
            "So yeah. The rest of us learned the lesson. You keep your mouth shut and you go home.",
            "That was then. Last year a jury believed thirteen women and that officer's never getting out.",
            "If you were sexually abused at Chowchilla, you can finally do something. You may qualify for significant potential compensation.",
            "No six-oh-two this time. No I-S-U room. Just one private form, and lawyers who don't work for the state.",
            "If somebody from the firm calls you, that's confidential. Your name don't go back to anybody.",
            "Telling didn't work back then. I know. It works now. Tap the button and see if you qualify.",
        ],
    },
    "r4_buddysystem": {
        "persona": "l2",
        "tone": ("matter-of-fact and knowing, talking to people who were there, warm at the close. "
                 "NOT salesy."),
        "lines": [
            "If you were at Chowchilla you remember the buddy system. We didn't even call it that, we just did it.",
            "You did not walk certain places alone. Everybody knew which officers. Nobody had to say it out loud.",
            "Think about that. We organized our whole day around staying safe from the people running the place.",
            "It was sexual abuse, what was happening in there. And everybody upstairs acted surprised when it hit the news.",
            "Women from the California women's prisons may qualify for significant potential compensation. That includes you.",
            "You don't need proof from back then. No old paperwork. What you lived through is the starting point.",
            "It's a couple questions on a private page. Your dates, what happened. Nothing posts anywhere.",
            "If a lawyer reaches out it's one private conversation. Your family stays out of it unless you want them in.",
            "You protected each other then. This is the same thing, honestly. Tap below and check if you qualify.",
        ],
    },
    "r5_mydate": {
        "persona": "l4",
        "tone": ("quiet and intense, weight on every word, steady and resolved at the end. "
                 "NOT salesy, NOT cheerful."),
        "lines": [
            "He knew about my release date from C-I-W in Chino. That's the part I can't get past.",
            "At C-I-W the guards knew exactly what going home meant to you. Some of them used it.",
            "You get a call-out, you think it's about your release. It wasn't about your release.",
            "And you went along with whatever happened because your date was sitting in his hands. That's sexual abuse.",
            "He can't touch your date now. You're home. And lawyers are taking these cases right now.",
            "You may qualify for significant potential compensation. Even if it was years ago.",
            "The form is a few minutes, what happened and when. Everything you put stays with the law firm.",
            "Same if they call you after. One conversation, private, done. Nobody at your job or your house knows.",
            "They used going home against us. You're home now. Tap below, see if you qualify.",
        ],
    },
    "r6_stillcounts": {
        "persona": "l2",
        "tone": ("warm, direct, gently insistent, like talking a friend out of a mistake. "
                 "NOT salesy, NOT preachy."),
        "lines": [
            "Can I talk to the women from Chowchilla and C-I-W who think this doesn't apply to them? That was me.",
            "I didn't call it abuse for years. He never hit me. I took the extra phone time, the little gifts.",
            "I told myself it was a relationship. In a prison. With a guard. Listen to how that sounds.",
            "Here's what a lawyer told me. Inside, you legally cannot consent to staff. None of us could.",
            "So it was sexual abuse. Even if you went along. Even if he was sweet about it.",
            "Whether you were at Chowchilla or C-I-W, you may qualify for significant potential compensation.",
            "The form doesn't judge you. It just asks where you were and what happened. Couple minutes.",
            "Whatever you share is sealed with the lawyers, the call too if they make one.",
            "I almost talked myself out of this. Don't do that. Tap below and find out if you qualify.",
        ],
    },
    "r8_appointments": {
        "persona": "l4",
        "tone": ("quiet and steady, the relief of finally saying something carried for decades, "
                 "lifting to calm encouragement at the end. NOT salesy, NOT melodramatic."),
        "lines": [
            "There's women who stopped going to their medical appointments inside. On purpose. I was one of them.",
            "This was twenty-some years ago, back at the women's prison. People outside never understood it.",
            "Why would anybody skip the doctor? You know why. Because of what happened in those rooms.",
            "What happened to some of us in there wasn't care. It was sexual abuse.",
            "And it wasn't just guards. Medical staff, work supervisors, whoever had power over you. It all counts.",
            "Women from the California women's prisons may qualify for significant potential compensation. Even from twenty years back.",
            "There's a short private form. Where you were, around when, what happened. Your own words.",
            "Nothing gets posted anywhere. If the firm calls you back, that stays private too.",
            "I waited twenty years thinking nobody would care. Turns out that wasn't true. Tap below, see if you qualify.",
        ],
    },
    "r7_nightcount": {
        "persona": "l1",
        "tone": ("low, hushed and haunted through the memory, lifting to calm resolve at the end. "
                 "NOT salesy, NOT melodramatic."),
        "lines": [
            "Women from C-I-W will know what I mean by this. You learned to sleep light in there.",
            "Three in the morning is when nobody's watching the ones who're supposed to be watching us.",
            "A flashlight in your cell at night still does something to me. I leave a lamp on to this day.",
            "What some of those officers did on night shift was sexual abuse. They pled guilty. It's documented.",
            "So this is real. Women from the California women's prisons may qualify for significant potential compensation.",
            "Doesn't matter if it was two thousand seventeen or way back when they still called it Frontera.",
            "Short private form. Where you were, when, what happened. You write it in your own words.",
            "It's confidential start to finish, even if a lawyer calls to go over your case with you.",
            "You slept light for years cause of them. Look into this. Tap the link and see if you qualify.",
        ],
    },
}


def build_prompt(persona, tone, dialogue):
    return (f"GAZE: locked on the camera lens the entire clip. BODY LANGUAGE: {BODY[persona]} "
            f"VOICE STYLE: {VOICE[persona]} TONE: {tone} "
            f"PACE LOCK: about 2.4 words per second, deliberate, each line given weight. "
            f"{AUDIO} {LOCKS} "
            f'SPOKEN DIALOGUE (verbatim, no additions, stop after final word): "{dialogue}"')


def main():
    mgids = {}
    for slug, path in PERSONAS.items():
        mgids[slug] = upload_asset(path)
        print(f"uploaded {slug} -> {mgids[slug]}", flush=True)

    for ad, cfg in SCRIPTS.items():
        persona = cfg["persona"]
        out_dir = f"outputs/cawp_{ad}_{persona}"
        os.makedirs(out_dir, exist_ok=True)
        for i, line in enumerate(cfg["lines"], 1):
            out = f"{out_dir}/clip{i}.mp4"
            if os.path.exists(out) and os.path.getsize(out) > 0:
                print(f"[skip] {out}", flush=True)
                continue
            prompt = build_prompt(persona, cfg["tone"], line)
            try:
                res = generate_veo(prompt, image_mgid=mgids[persona], duration=8,
                                   aspect_ratio="portrait")
                if res.get("status") != "success" or not res.get("urls"):
                    print(f"[FAIL] {out}: {str(res.get('raw'))[:140]}", flush=True)
                    continue
                data = requests.get(res["urls"][0], timeout=600)
                data.raise_for_status()
                with open(out, "wb") as f:
                    f.write(data.content)
                print(f"[ok] {out}", flush=True)
            except Exception as e:
                print(f"[FAIL] {out}: {e}", flush=True)
    print("done — R-batch complete", flush=True)


if __name__ == "__main__":
    main()
