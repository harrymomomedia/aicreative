"""Depo meningioma UGC scale-out — 10 distinct-format testimonials, 1 persona each.
Diagnosis-first: "meningioma"/"brain tumor" lands in the FIRST sentence (3-5s filter). Each script
is a DIFFERENT format/voice so no two sound same-authored. Generated on useapi google-flow Veo 3.1
Lite LOW-PRIORITY (the locked path), i2v off the 4:5 persona still. ~7-9 clips each (auto-segmented
on sentence boundaries at ~17 words/clip). Captions added later (Nick), 4:5 at finalize.

  python scripts/depo_ugc10_gen.py test          # clip01 of ALL 10 (QA gate)
  python scripts/depo_ugc10_gen.py test 4        # clip01 of ad 4 only
  python scripts/depo_ugc10_gen.py full 4        # all clips of ad 4
  python scripts/depo_ugc10_gen.py all           # every clip of every ad (paced, resumable)
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from googleflow_client import generate_veo, upload_asset, download   # FREE veo-3.1-lite-low-priority

PRON = '"meningioma" = "men-in-jee-OH-muh". "Depo" = "DEP-oh" (short e like "deck", NOT "depot").'
OUT = "outputs/depo_ugc10"

# n, slug, persona file, voice, tone(register), full script (meningioma front-loaded)
ADS = [
    dict(n=1, slug="story_arc", persona="persona_01_couch_round_twa.png",
         voice="a warm, weary middle-aged Black woman, low and steady, plain-spoken",
         tone="reflective storytelling, tired but warm; settles into the memory",
         script="A meningioma. That's the word that changed everything for me last spring. A brain tumor, "
                "growing in the lining of my skull. Let me tell you how I got there, because it might save you "
                "some time. It started with headaches that wouldn't quit. I figured it was stress. Then one "
                "morning I couldn't read the cereal box, the words were all doubled. They sent me for a scan, "
                "and there it was. I sat in that parking lot and cried, because I take care of myself. I eat "
                "right, I walk every day. None of it made sense. So I went home and started reading, and I kept "
                "seeing the same thing. The Depo shot. The birth control I'd gotten for years. Women who used it "
                "are far more likely to grow this exact tumor, and I had no idea. So if you've got a meningioma "
                "and you were on Depo, look into it. It's free to see if you qualify, and it stays private."),
    dict(n=2, slug="urgent_psa", persona="persona_02_kitchen_oval_braids.png",
         voice="a sharp, clear middle-aged Black woman, fast and direct, urgent",
         tone="urgent public-service warning, talking straight at the viewer, no fluff",
         script="If you have a meningioma, a brain tumor, and you ever had the Depo birth control shot, stop "
                "scrolling and listen to me. These two things are connected. There are real studies now. Women "
                "who got that shot are showing up with this exact tumor at way higher rates, and almost none of "
                "us were warned. I wasn't. I found out by accident. Here's what you need to know. It costs you "
                "nothing to check if you have a case. You don't go to a courthouse. You don't pay a dime up "
                "front. You answer a few questions, in private, and that's it. I'm not telling you this to scare "
                "you. I'm telling you because somebody should have told me sooner. If that's you, go see if you "
                "qualify. Today, not next month."),
    dict(n=3, slug="the_list", persona="persona_03_bedroom_heart_afro.png",
         voice="an organized, matter-of-fact middle-aged Black woman, clear and a little brisk",
         tone="organized and purposeful, counting off points, calm authority",
         script="If you've got a meningioma, here are three things nobody told me when I got mine. I'm saying "
                "them out loud for whoever needs to hear it. Number one. A meningioma is not always random bad "
                "luck. Mine wasn't. Number two. The Depo shot, that birth control they give you every three "
                "months, is linked to these tumors. I was on it for six years, and not one person mentioned a "
                "risk. Number three, and this is the one I almost missed. If both of those are true for you, you "
                "may qualify for compensation for it. I thought checking would be a hassle. It took me two "
                "minutes, on my phone, in my own kitchen. Free, and nobody else has to know. So that's it. Three "
                "things. If you've got the diagnosis and a history with that shot, please don't sit on it like I "
                "almost did."),
    dict(n=4, slug="phone_call", persona="persona_04_desk_angular_locs.png",
         voice="an animated, conversational middle-aged Black woman, expressive, telling a story",
         tone="conversational and a little breathless, reliving the phone call, then resolve",
         script="Two years ago, they pulled a meningioma out of my head. A brain tumor. So when my cousin called "
                "me last Tuesday, out of breath, and asked, did you ever take that Depo shot, I went cold. She "
                "said, girl, turn on the news. Apparently there's this whole thing now. The shot is linked to "
                "brain tumors. To meningiomas. The exact thing I had surgery for. The whole time I thought I'd "
                "done something wrong, ate something, stressed myself sick. No. It was the shot my own doctor put "
                "me on. She found this place where you can check if you qualify for compensation. Free, takes a "
                "minute. I did it that same night. So now I'm the one making the calls. If you had that shot and "
                "you've got a meningioma, check. Don't wait for somebody to call you."),
    dict(n=5, slug="myth_buster", persona="persona_05_couch_full_headwrap.png",
         voice="a knowing, steady middle-aged Black woman, a little challenging, sure of herself",
         tone="knowing objection-killer, gently challenging, anticipates your excuses",
         script="If you've got a meningioma and you took the Depo shot, let me guess what you're thinking, "
                "because I thought all of it too. You're thinking it was years ago, it's too late. It's not. "
                "You're thinking you can't afford a lawyer. It costs you nothing to find out. You're thinking "
                "you're not the type to sue anybody. Neither am I. But this isn't about that. It's about what "
                "they didn't tell us. Here's the deal. I have a meningioma, a brain tumor, and I was on that shot "
                "for a long time. Those two things are connected, and the company knew before I did. Checking "
                "whether you have a case is free, it's private, and you never step foot in a courtroom. So "
                "whatever reason you've got for not looking into it, I promise I had the same one, and I was "
                "wrong. Go see."),
    dict(n=6, slug="fired_up", persona="persona_06_dining_thin_tapered.png",
         voice="a fired-up middle-aged Black woman, indignant, voice tight with anger then steadying",
         tone="angry and indignant, barely contained, then resolve; never shouting, but hot",
         script="They gave me a brain tumor. A meningioma. And I am so angry I can barely sit still, so excuse "
                "me. They knew. That's what gets me. They knew that Depo shot could do this and kept handing it "
                "out like candy. I got one every three months for the better part of a decade because my doctor "
                "said it was the easy choice. The easy choice gave me a tumor in my head. You know what that does "
                "to your life? The scans, the waiting, not knowing if it's growing. And the whole time the answer "
                "was sitting in a study somebody buried. So no, I won't be quiet about it. If you took that shot "
                "and you've got a meningioma too, you're not crazy, and it is not your fault. Go find out if you "
                "qualify for compensation. It's free, it's private, and it is the very least we deserve."),
    dict(n=7, slug="quiet_reflection", persona="persona_07_armchair_square_twists.png",
         voice="a soft, slow middle-aged Black woman, intimate, almost talking to herself",
         tone="quiet, intimate, vulnerable; slow and gentle, like a confession",
         script="I have a meningioma. A tumor in the lining of my brain. I don't really talk about it much, but "
                "I've been sitting with it, and I think somebody needs to hear it from a regular person. They "
                "found it almost three years ago now. For the longest time I carried this quiet guilt, like I'd "
                "brought it on myself somehow. I hadn't. I found that out slowly, late at night, reading. The "
                "birth control shot I trusted, Depo, it's been linked to exactly this. I just sat there when I "
                "read it. All that guilt, for nothing. If you're somewhere in that same place right now, scared, "
                "blaming yourself, I want you to know it might not be yours to carry. There's a way to find out "
                "if you qualify for compensation, quietly, for free. No pressure. Just look, when you're ready. "
                "That's all I wanted to say."),
    dict(n=8, slug="do_this", persona="persona_08_counter_long_bun.png",
         voice="a practical, encouraging middle-aged Black woman, clear and steady, coaching",
         tone="practical and encouraging, walking you through steps like a helpful friend",
         script="If you've got a meningioma, I'm going to walk you through exactly what to do, because I wish "
                "someone had done this for me. First, think back. Were you ever on the Depo shot? The injection, "
                "every three months. If yes, keep going. Second, that shot is linked to the kind of brain tumor "
                "you have. Not a rumor, there are real studies. Third, and this is the part people skip, go check "
                "if you qualify for compensation. Not later. Now. It's a few simple questions, it's free, and "
                "it's completely private. You don't need paperwork in front of you, you don't need a lawyer yet, "
                "you don't need to leave your house. That's the whole list. Diagnosis, the shot, then check. If "
                "that's you, do step three today. Don't let it sit."),
    dict(n=9, slug="to_you", persona="persona_09_bedroom_soft_curly.png",
         voice="a gentle, warm middle-aged Black woman, tender, speaking to one person",
         tone="tender second-person empathy, speaking directly to a frightened newly-diagnosed woman",
         script="If you just heard the word meningioma for the first time, a brain tumor, I made this video for "
                "you. I know exactly where you are. The fear, the questions, the way everyone keeps telling you "
                "it'll be fine when it doesn't feel fine. I was there two years ago. And there's one thing I "
                "really need you to know, because it took me too long to find out. If you were ever on the Depo "
                "birth control shot, your tumor and that shot may be connected. They're linked. Which means what "
                "happened to you might not be random, and might not be your fault. A lot of us are finding this "
                "out right now. You may qualify for compensation for what you've been through, and checking is "
                "free and private. I can't take the fear away. But I can hand you this. Please look into it."),
    dict(n=10, slug="straight_talk", persona="persona_10_hall_broad_cornrows.png",
         voice="a plain, no-nonsense middle-aged Black woman, efficient, dry and direct",
         tone="plain and efficient, no story, just the facts laid out fast",
         script="If you have a meningioma and you were on the Depo shot, I'm going to save you about forty hours "
                "of Googling, because I already did it. Short version. A meningioma is a brain tumor, usually not "
                "cancer but serious. The Depo-Provera shot is linked to it. A big study found women who used it "
                "over a year had a much higher rate of these tumors. I used it for years. I have the tumor. "
                "Connect the dots. The part that matters for you. There's an active legal claim, and you may "
                "qualify for significant compensation. It's free to check, it's confidential, and it takes a "
                "couple minutes. I'm not going to dress it up or tell you a sad story, you've got enough going "
                "on. If the diagnosis and the shot are both true for you, go check. The link's right there."),
]


def segment(script, lo=12, hi=18):
    """Split into clip lines on sentence boundaries, ~12-18 words each (Veo ~2.4 wps over 8s).
    Keeps adding while a clip is under `lo` so no clip is underfilled (underfilled => Veo improvises)."""
    sents = re.findall(r"[^.?!]+[.?!]+", script)
    clips, cur = [], ""
    for s in sents:
        s = s.strip()
        cand = (cur + " " + s).strip()
        if not cur:
            cur = s
        elif len(cur.split()) < lo or len(cand.split()) <= hi:
            cur = cand
        else:
            clips.append(cur); cur = s
    if cur:
        if clips and len(cur.split()) < lo:
            clips[-1] += " " + cur
        else:
            clips.append(cur)
    return clips


def last_word(s):
    t = re.findall(r"[A-Za-z']+", s)
    return t[-1] if t else ""


def P(ad, line):
    return f"""She is talking directly into her phone's front camera, filming a candid selfie video, like a real iPhone video. An ordinary Black woman about 45. {ad['tone']}.
GAZE: soft eye contact into the phone lens, natural blinks, occasional small glance away then back. Warm dark-brown eyes, OPEN, the SAME color throughout (never lighter/changing).
BODY: small natural movements, a slight nod or head tilt; relaxed, real.
VOICE: {ad['voice']}, NOT young.
TONE: {ad['tone']}.
SPEED: about 2.4 words per second, natural conversational pace.
AUDIO CRITICAL: she speaks clearly and fully audibly at a close conversational volume right into the phone mic. NOT whispered, NOT muttered.
PRONUNCIATION: {PRON}
DIALOGUE LOCK: English only. Say ONLY the words in SPOKEN DIALOGUE, in order. No fillers (no uh, um, like, you know), no extra or trailing words, no repetition. Stop after the final word "{last_word(line)}".
NO on-screen text, NO captions, NO subtitles, NO watermark.
SPOKEN DIALOGUE (verbatim, stop after final word): "{line}\""""


def gen(ad, idx, line, mgid):
    out = Path(OUT) / f"ad{ad['n']:02d}_{ad['slug']}" / f"clip{idx:02d}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 50000:
        return "cached"
    # free Lite I2V: duration MUST be 8, anchor MUST be 9:16 (4:5 anchors get paygate-rejected)
    r = generate_veo(prompt=P(ad, line), image_mgid=mgid, duration=8, aspect_ratio="portrait")
    if r.get("status") != "success" or not r.get("urls"):
        return "FAIL: " + str(r.get("raw"))[:160]
    download(r["urls"][0], str(out))
    return "ok"


def to_9x16(path):
    """Center-crop a 4:5 anchor to 9:16 (free Lite I2V only accepts 9:16 input). Cache as *_9x16.png."""
    from PIL import Image
    out = Path(path).with_name(Path(path).stem + "_9x16.png")
    if not out.exists():
        im = Image.open(path).convert("RGB"); w, h = im.size
        tw = int(h * 9 / 16); x = (w - tw) // 2
        im.crop((x, 0, x + tw, h)).save(out)
    return str(out)


def run_ad(ad, only_clip1=False):
    clips = segment(ad["script"])
    mgid = upload_asset(to_9x16(str(Path(OUT) / ad["persona"])))
    rng = clips[:1] if only_clip1 else clips
    print(f"[ad{ad['n']:02d} {ad['slug']}] {len(clips)} clips, generating {len(rng)}", flush=True)
    for i, line in enumerate(rng, 1):
        print(f"  ad{ad['n']:02d} clip{i:02d} -> {gen(ad, i, line, mgid)}", flush=True)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"
    which = int(sys.argv[2]) if len(sys.argv) > 2 else None
    ads = [a for a in ADS if which is None or a["n"] == which]
    if mode == "test":
        for a in ads:
            run_ad(a, only_clip1=True)
    elif mode in ("full", "all"):
        for a in ads:
            run_ad(a, only_clip1=False)


if __name__ == "__main__":
    main()
