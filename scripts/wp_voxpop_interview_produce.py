"""STREET INTERVIEW (conversational) — reporter with mic stops a woman on the sidewalk who turns
out to be a survivor; informative back-and-forth, 500-women hook. Grok, 3 clips, ONE two-shot
anchor (interviewer + Respondent A). Chowchilla = plain spelling + descriptive lock; 'at Chowchilla'.
"""
import sys, pathlib, requests
from kie_client import upload_file, generate_grok

OUT = pathlib.Path("outputs/wp_voxpop/interview_ad"); OUT.mkdir(parents=True, exist_ok=True)
ANCHOR = "outputs/wp_voxpop/twoshot/v2_profile.png"

PRON = ("Pronunciation: 'Chowchilla' is a California women's prison, pronounced as three English "
        "syllables: chow (rhymes with 'cow') + chill + uh, stress the MIDDLE syllable, one fluid "
        "word, NOT spelled out, NEVER Spanish.\n")
COMMON = (
 "Wide 16:9 candid STREET interview on a sunny sidewalk, locked static camera. A reporter (LEFT, "
 "denim jacket, holding a microphone) is interviewing a weathered woman (RIGHT, grey hoodie). "
 "Natural BACK-AND-FORTH: they TAKE TURNS, only one talks at a time while the other listens with "
 "mouth CLOSED. The reporter is calm, informative and warm; the woman is candid and a little "
 "emotional. ~2.4 words/sec.\n" + PRON +
 "DIALOGUE LOCK: English only, no filler, no extra words, follow the exact lines and speaker order.\n"
 "AUDIO: clean spoken dialogue only, natural street ambience, NO background music, NO song.\n"
 "No on-screen text, no captions, no subtitles.\n")

CLIPS = {
 "clip1": {"duration":"15", "dialogue":
   "REPORTER: \"Nearly 500 women who were incarcerated in California's prisons are coming forward. You were at Chowchilla. What happened in there?\"\n"
   "WOMAN: \"The guards crossed the line. Sexually. And back then, nobody would have believed us.\"\n"
   "REPORTER: \"A lot of women think that because they never reported it, it is too late.\"\n"
   "WOMAN: \"That is exactly what I thought. I thought it was my fault.\"\n"},
 "clip2": {"duration":"15", "dialogue":
   "REPORTER: \"But under California law, a woman in prison cannot consent to a guard. So women like you may qualify for significant potential compensation.\"\n"
   "WOMAN: \"Wait. Even after all these years?\"\n"
   "REPORTER: \"Even now. It is free to check, completely confidential, and you never go to court.\"\n"
   "WOMAN: \"If I had only known that sooner.\"\n"},
 "clip3": {"duration":"12", "dialogue":
   "REPORTER: \"If you were at Chowchilla, Valley State, or Folsom, there is a private two-minute form.\"\n"
   "WOMAN: \"So anyone who was in there should check?\"\n"
   "REPORTER: \"Yes. Tap below and see if you qualify.\"\n"},
}

only = sys.argv[1] if len(sys.argv) > 1 else None
url = upload_file(ANCHOR)
for slug, c in CLIPS.items():
    if only and only != slug: continue
    dst = OUT / f"{slug}.mp4"
    if dst.exists(): print(f"[skip] {slug}"); continue
    prompt = COMMON + "SPOKEN DIALOGUE (verbatim, in order):\n" + c["dialogue"]
    print(f"[gen] {slug} Grok {c['duration']}s")
    r = generate_grok(prompt, image_urls=[url], duration=c["duration"], resolution="720p", aspect_ratio="16:9")
    if r.get("urls"):
        dst.write_bytes(requests.get(r["urls"][0], timeout=600).content); print(f"[done] {slug}")
    else:
        print(f"[FAIL] {slug}", str(r.get("raw"))[:250])
print("INTERVIEW PRODUCE DONE")
