#!/usr/bin/env python3
"""First 16s of the Depo interview: 4 Veo 3.1 Fast clips (Poyo, frame mode, $0.10 each).
Two Q&A beats. Each person gets a TALKING clip + a LISTENING clip so the stacked version's
non-speaker pane isn't lip-syncing. Anchors: surv_face_v1 (subject, looks right),
doc_alone_v1_L (interviewer, looks left). Skip-if-exists.

Run: .venv/bin/python scripts/depo_interview_veo16.py
"""
import concurrent.futures as cf
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import poyo_client as poyo

REF = Path("outputs/depo_interview/reference")
OUT = Path("outputs/depo_interview/clips")
OUT.mkdir(parents=True, exist_ok=True)

SURV = REF / "surv_face_v1.png"        # subject, gazes screen-right
DOC = REF / "doc_alone_v1_L.png"       # interviewer, gazes screen-left

NOTEXT = "No on-screen text, no captions, no subtitles."

DOC_TALK = (
    "Documentary interviewer, a warm middle-aged woman, gently asking a question to the person "
    "off-camera on her left.\n"
    "GAZE: toward the person to her left, attentive, never into the lens.\n"
    "BODY: calm, a slight nod, natural blinks, subtle.\n"
    "VOICE: warm, measured, empathetic, unhurried.\nTONE: gentle, caring.\nSPEED: ~2.4 words/sec.\n"
    "AUDIO CRITICAL: she speaks CLEARLY at full conversational volume, right into the microphone. "
    "Not soft, not muttered.\n"
    "PRONUNCIATION LOCK: \"meningioma\" = \"men-in-jee-OH-muh\".\n"
    "DIALOGUE LOCK: English only. Speak ONLY the words in SPOKEN DIALOGUE, in order, no added "
    "words, no fillers, no trailing words; stop after the final word.\n"
    "SPOKEN DIALOGUE (verbatim): \"When they told you it was a brain meningioma, did anyone ever "
    "explain why you got it?\"\n" + NOTEXT
)

SURV_TALK = (
    "A weary middle-aged Black woman being interviewed, answering quietly.\n"
    "GAZE: toward the interviewer off-camera on her right, not into the lens.\n"
    "BODY: tired, a small resigned head shake, natural blinks, subtle.\n"
    "VOICE: warm, weathered, quiet and heavy.\n"
    "TONE: resigned, matter-of-fact — she believed it for years.\nSPEED: ~2.4 words/sec.\n"
    "AUDIO CRITICAL: clear, full conversational volume right into the microphone.\n"
    "DIALOGUE LOCK: English only. Speak ONLY the SPOKEN DIALOGUE, no added/filler/trailing words; "
    "stop after the final word.\n"
    "SPOKEN DIALOGUE (verbatim): \"No. Bad luck, they kept saying. Over and over. And for a long "
    "time, I believed that.\"\n" + NOTEXT
)

DOC_LISTEN = (
    "Documentary interviewer listening intently to the person off-camera on her left.\n"
    "GAZE: on the off-camera speaker to her left.\n"
    "BODY: attentive stillness, slow empathetic nods, soft micro-expressions, natural blinks; may "
    "glance once at her notepad.\n"
    "She does NOT speak — mouth stays closed, completely silent the entire clip.\n"
    "Only quiet ambient room tone, no dialogue, no voice.\n" + NOTEXT
)

SURV_LISTEN = (
    "A weary middle-aged Black woman listening to an interviewer's question off-camera on her right.\n"
    "GAZE: on the off-camera interviewer to her right.\n"
    "BODY: quiet attentiveness, a slight thoughtful nod, weary natural blinks, a subtle breath.\n"
    "She does NOT speak — mouth stays closed, completely silent the entire clip.\n"
    "Only quiet ambient room tone, no dialogue, no voice.\n" + NOTEXT
)

# name -> (anchor, prompt)
CLIPS = {
    "doc_talk_1": (DOC, DOC_TALK),
    "surv_listen_1": (SURV, SURV_LISTEN),
    "surv_talk_1": (SURV, SURV_TALK),
    "doc_listen_1": (DOC, DOC_LISTEN),
}


def gen(name):
    out = OUT / f"{name}.mp4"
    if out.exists():
        print(f"[skip] {out}")
        return
    anchor, prompt = CLIPS[name]
    url = poyo.upload_file(str(anchor))
    print(f"[gen ] {name} (anchor {anchor.name})")
    res = poyo.generate_veo(prompt, image_urls=[url, url], generation_type="frame",
                            aspect_ratio="9:16", resolution="720p")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {name}: {res.get('raw')}")
        return
    poyo.download(res["urls"][0], out)
    print(f"[done] {out}")


with cf.ThreadPoolExecutor(max_workers=4) as ex:
    list(ex.map(gen, CLIPS.keys()))
print("ALL DONE")
