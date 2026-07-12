"""'The Nice One' v2 — shot-reverse-shot. Each turn = a SOLO Veo clip (i2v) from the interviewer
or survivor anchor (both already 9:16 solo shots at the courthouse, matching angle + mic). No
two-shot, so Veo never has to pick who talks. Poyo Veo 3.1 Fast 8s. skip-if-exists.
"""
import sys, pathlib, requests
from kie_client import upload_file
from poyo_client import generate_veo

OUT = pathlib.Path("outputs/wp_interview2/niceone"); OUT.mkdir(parents=True, exist_ok=True)
IV = "outputs/wp_interview2/reference/interviewer_a.png"      # interviewer (looks screen-right)
SV = "outputs/wp_interview2/reference/survivor_match_a.png"   # survivor (looks screen-left)
PRON = ("PRONUNCIATION: 'Chowchilla' = three English syllables chow (rhymes with cow) + chill + uh, "
        "stress the middle syllable, one fluid word, never Spanish. ")

# (idx, speaker I=interviewer / S=survivor, line)  — each <=~19 words to fit 8s
TURNS = [
 (1,"I","So how long were you inside at Chowchilla?"),
 (2,"S","Six years. Sounds a lot longer when I say it out loud."),
 (3,"I","Was there a staff member?"),
 (4,"S","The nice one. Always asking how I was, slipping me little things. I really thought he cared."),
 (5,"I","And then it changed?"),
 (6,"S","It didn't change. That was the trick. He'd get me alone, somewhere with no camera."),
 (7,"S","And it stopped being my choice. If I said no, he'd go after my parole date."),
 (8,"I","He was sexually abusing you."),
 (9,"S","For almost two years. I called it a relationship, because that was easier than the truth."),
 (10,"S","The truth was a guard was sexually assaulting me, and I could not make it stop."),
 (11,"I","That was never on you. Women sexually abused by staff at Chowchilla may qualify for significant potential compensation."),
 (12,"I","It's confidential. There is no court. And it is free just to find out."),
 (13,"S","After all this time. Maybe I will."),
]

def prompt_for(spk, line):
    if spk == "I":
        who = ("The woman holding the small podcast microphone speaks to the person she is "
               "interviewing off to her right, warm, calm, everyday tone, gentle. Gaze off-camera "
               "to her right.")
    else:
        who = ("The older woman speaks candidly to the interviewer off to her left, weathered, "
               "honest, quietly emotional, measured. Gaze off-camera to her left.")
    pron = PRON if "Chowchilla" in line else ""
    return (
     "Vertical 9:16 candid street interview at a courthouse, locked static camera, single person in "
     f"frame. {who} ~2.4 words per second. AUDIO CRITICAL: clear full conversational volume, clean, "
     "NO music. " + pron +
     "DIALOGUE LOCK: English only, no filler, no 'um/uh', no extra or trailing words, stop after the "
     f"final word. SPOKEN DIALOGUE (verbatim): \"{line}\". No on-screen text, no captions.")

def _main():
    only = int(sys.argv[1]) if len(sys.argv) > 1 else None
    iv_url = upload_file(IV); sv_url = upload_file(SV)
    for idx, spk, line in TURNS:
        if only and idx != only: continue
        dst = OUT / f"t{idx:02d}_{spk}.mp4"
        if dst.exists(): print(f"[skip] t{idx}"); continue
        url = iv_url if spk == "I" else sv_url
        r = generate_veo(prompt_for(spk, line), image_urls=[url, url], aspect_ratio="9:16",
                         resolution="720p", generation_type="frame")
        if r.get("urls"):
            dst.write_bytes(requests.get(r["urls"][0], timeout=300).content); print(f"[done] t{idx}")
        else:
            print(f"[FAIL] t{idx}", str(r.get("raw"))[:150])
    print("NICEONE PRODUCE DONE")

if __name__ == "__main__":
    _main()
