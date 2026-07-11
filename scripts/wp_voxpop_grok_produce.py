"""FULL vox-pop ad produced on Grok Imagine (15s clips) — 3 respondents, back-and-forth.
Corrected Chowchilla pronunciation: NORMAL spelling in dialogue + detailed descriptive lock
(from chowchilla_a2_variations.py). skip-if-exists. Assemble separately.
"""
import sys, pathlib, requests
from kie_client import upload_file, generate_grok

OUT = pathlib.Path("outputs/wp_voxpop/grok_ad"); OUT.mkdir(parents=True, exist_ok=True)
TWO = pathlib.Path("outputs/wp_voxpop/twoshot")

PRON = (
 "Pronunciation: 'Chowchilla' is the name of a California women's prison, pronounced as three "
 "English syllables: chow (rhymes with 'cow') + chill + uh, stress on the MIDDLE syllable, said as "
 "one fluid word, NOT spelled out, NEVER as a Spanish word.\n"
)
COMMON = (
 "Wide 16:9 candid street interview, locked static camera. Natural BACK-AND-FORTH: the two women "
 "TAKE TURNS, only one talks at a time while the other listens with mouth CLOSED. The interviewer "
 "on the LEFT (denim jacket) is warm and friendly; the woman on the RIGHT (grey hoodie) is older, "
 "weathered, honest. ~2.4 words/sec.\n" + PRON +
 "DIALOGUE LOCK: English only, no filler, no extra words, follow the exact lines and speaker order.\n"
 "AUDIO: clean spoken dialogue only, natural street ambience, NO background music, NO song, NO score.\n"
 "No on-screen text, no captions, no subtitles.\n"
)

CLIPS = {
 "clip1_A": {
   "anchor": "v2_profile.png", "duration": "15",
   "dialogue":
     "INTERVIEWER: \"Did you know women who were sexually abused at Chowchilla may qualify for significant potential compensation?\"\n"
     "WOMAN: \"Wait, for real? My cousin was in there. She never told anybody what happened to her.\"\n"
     "INTERVIEWER: \"It is free and confidential to check.\"\n"
     "WOMAN: \"That is about time. Those women deserve that.\"\n" },
 "clip2_B": {
   "anchor": "v2_profile_B.png", "duration": "15",
   "dialogue":
     "INTERVIEWER: \"Have you heard what happened to the women at Chowchilla?\"\n"
     "WOMAN: \"Yeah. I did time in there. What those guards did to us, nobody listened back then.\"\n"
     "INTERVIEWER: \"You may qualify for significant potential compensation now.\"\n"
     "WOMAN: \"For real? After all these years?\"\n" },
 "clip3_C": {
   "anchor": "v2_profile_C.png", "duration": "12",
   "dialogue":
     "INTERVIEWER: \"If you were at Chowchilla, would you come forward?\"\n"
     "WOMAN: \"I would. Those women waited too long for somebody to finally listen.\"\n"
     "INTERVIEWER: \"It is free, confidential, and there is no court.\"\n" },
}

only = sys.argv[1] if len(sys.argv) > 1 else None
for slug, c in CLIPS.items():
    if only and only not in slug:
        continue
    dst = OUT / f"{slug}.mp4"
    if dst.exists():
        print(f"[skip] {slug} exists"); continue
    anchor = TWO / c["anchor"]
    if not anchor.exists():
        print(f"[wait] anchor missing: {anchor}"); continue
    url = upload_file(str(anchor))
    prompt = COMMON + "SPOKEN DIALOGUE (verbatim, in order):\n" + c["dialogue"]
    print(f"[gen] {slug} Grok {c['duration']}s\n{prompt}\n")
    r = generate_grok(prompt, image_urls=[url], duration=c["duration"], resolution="720p",
                      aspect_ratio="16:9")
    if r.get("urls"):
        dst.write_bytes(requests.get(r["urls"][0], timeout=600).content)
        print(f"[done] {slug} -> {dst}")
    else:
        print(f"[FAIL] {slug}", str(r.get("raw"))[:300])
print("PRODUCE DONE")
