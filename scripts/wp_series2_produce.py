"""'It Was Never Consent' street-interview series — 3 videos, shot-reverse-shot solo clips.
Each turn = a SOLO Veo clip (i2v) from the interviewer / survivor / into-lens-closer anchor.
Recurring interviewer (looks right, matched mic), 3 distinct survivors (look left), courthouse.
Poyo Veo 3.1 Fast 8s, generation_type=frame (anchor twice). skip-if-exists.

Usage: wp_series2_produce.py <video> [turn_idx]   video in {relationship, moved, kids}
"""
import sys, pathlib, requests
from kie_client import upload_file
from poyo_client import generate_veo

REF2 = "outputs/wp_series2/reference"
IV = "outputs/wp_interview2/reference/interviewer_mic.png"     # recurring interviewer (looks right)
PRON = ("PRONUNCIATION: 'Chowchilla' = three English syllables chow (rhymes with cow) + chill + uh, "
        "stress the middle syllable, one fluid word, never Spanish. ")

# per video: survivor reverse-shot anchor + into-lens closer anchor + turns
VIDEOS = {
 "relationship": {
   "sv": f"{REF2}/surv1_maria.png", "cam": f"{REF2}/surv1_maria_cam.png",
   "turns": [
     (1,"I","How old were you when it started with that officer?"),
     (2,"S","Thirty-one. He was the first person in there who treated me like I mattered."),
     (3,"I","So in your mind, was it a relationship?"),
     (4,"S","For years I told myself it was. That was easier than saying what it really was."),
     (5,"S","He had the keys. He decided when I ate, when I showered, if I got written up."),
     (6,"I","And the sex, was that ever something you could actually say no to?"),
     (7,"S","No. Saying no meant the hole, or losing my good time. So I stopped saying it."),
     (8,"I","So he sexually abused you, using that power over you."),
     (9,"S","It took me years to call it that. A guard was sexually assaulting me and calling it love."),
     (10,"I","Under California law, a woman in prison can never consent to a guard."),
     (11,"I","Women abused at Chowchilla may qualify for significant potential compensation."),
     (12,"I","It is free to check, it is confidential, and you never go to court."),
     (13,"C","If a guard did this to you, it was never your fault. See if you qualify."),
   ]},
 "moved": {
   "sv": f"{REF2}/surv2_denise.png", "cam": f"{REF2}/surv2_denise_cam.png",
   "turns": [
     (1,"I","When you finally told someone what that guard was doing, what happened?"),
     (2,"S","They didn't help me. They shipped me to another yard and wrote me up for lying."),
     (3,"I","So reporting it made your life worse?"),
     (4,"S","Way worse. After that, every woman in there knew what happens if you talk."),
     (5,"S","He would corner me in the supply room. No cameras. Said nobody believes an inmate."),
     (6,"I","Was it ever something you agreed to?"),
     (7,"S","How do you agree with the man who controls your parole? It was sexual abuse. Plain."),
     (8,"I","Women sexually abused by staff at Valley State and Chowchilla may qualify for significant potential compensation."),
     (9,"I","It is confidential, and there is no court."),
     (10,"C","You are not a number, and you are not alone. See if you qualify."),
   ]},
 "kids": {
   "sv": f"{REF2}/surv3_kathy.png", "cam": f"{REF2}/surv3_kathy_cam.png",
   "turns": [
     (1,"I","Have you ever told your family what really happened to you inside?"),
     (2,"S","No. My kids still don't know. I carried it by myself for eleven years."),
     (3,"I","Why keep it a secret for so long?"),
     (4,"S","Shame. I thought people would say I let it happen. I didn't let anything happen."),
     (5,"S","He was a guard. He would come to my cell at count. I had nowhere to go."),
     (6,"I","So this wasn't an affair. This was sexual abuse."),
     (7,"S","He sexually abused me for two years and dressed it up as a favor. I see that now."),
     (8,"I","And you are not the only one. Hundreds of women are saying the same thing."),
     (9,"S","That is what made me open my mouth. I am not the crazy one. It was real."),
     (10,"I","Women sexually abused by staff at Chowchilla, Valley State, or Chino may qualify for significant potential compensation."),
     (11,"C","If this happened to you, you can finally tell someone. See if you qualify."),
   ]},
}

def prompt_for(spk, line):
    if spk == "I":
        who = ("The woman holding the small podcast microphone speaks to the person she is interviewing "
               "off to her right, warm, calm, everyday tone, gentle. Gaze off-camera to her right.")
    elif spk == "C":
        who = ("The older woman holds the microphone in her own hand near her mouth and speaks STRAIGHT "
               "INTO the camera lens, directly to the viewer, heartfelt and steady, urging them. Gaze "
               "locked on the camera lens.")
    else:
        who = ("The older woman speaks candidly to the interviewer off to her left, weathered, honest, "
               "quietly emotional, measured. Gaze off-camera to her left.")
    pron = PRON if "Chowchilla" in line else ""
    return (
     "Vertical 9:16 candid street interview at a courthouse, locked static camera, single person in "
     f"frame. {who} ~2.4 words per second. AUDIO CRITICAL: clear full conversational volume, clean, "
     "NO music. " + pron +
     "DIALOGUE LOCK: English only, no filler, no 'um/uh', no extra or trailing words, stop after the "
     f"final word. SPOKEN DIALOGUE (verbatim): \"{line}\". No on-screen text, no captions.")

def _main():
    video = sys.argv[1]
    only = int(sys.argv[2]) if len(sys.argv) > 2 else None
    cfg = VIDEOS[video]
    OUT = pathlib.Path(f"outputs/wp_series2/{video}"); OUT.mkdir(parents=True, exist_ok=True)
    iv_url = upload_file(IV); sv_url = upload_file(cfg["sv"]); cam_url = upload_file(cfg["cam"])
    for idx, spk, line in cfg["turns"]:
        if only and idx != only: continue
        dst = OUT / f"t{idx:02d}_{spk}.mp4"
        if dst.exists(): print(f"[skip] {video} t{idx}"); continue
        url = {"I": iv_url, "S": sv_url, "C": cam_url}[spk]
        r = generate_veo(prompt_for(spk, line), image_urls=[url, url], aspect_ratio="9:16",
                         resolution="720p", generation_type="frame")
        if r.get("urls"):
            dst.write_bytes(requests.get(r["urls"][0], timeout=300).content); print(f"[done] {video} t{idx}")
        else:
            print(f"[FAIL] {video} t{idx}", str(r.get("raw"))[:150])
    print(f"SERIES2 PRODUCE DONE {video}")

if __name__ == "__main__":
    _main()
