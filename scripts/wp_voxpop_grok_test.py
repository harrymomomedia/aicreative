"""Grok Imagine i2v test from the v2 two-shot anchor — probe whether 30s actually works,
whether it holds BOTH identities, and whether it produces synced speech audio.
ONE speaker: Respondent A answers a longer beat; interviewer holds mic + stays SILENT.
"""
import pathlib, requests
from kie_client import upload_file, generate_grok

OUT = pathlib.Path("outputs/wp_voxpop/grok"); OUT.mkdir(parents=True, exist_ok=True)
url = upload_file("outputs/wp_voxpop/twoshot/v2_profile.png")

PROMPT = (
 "Wide 16:9 candid street interview, locked static camera. The woman on the RIGHT in the grey "
 "hoodie answers into the microphone, looking at the interviewer beside her. Weathered, low, "
 "slightly rough Latina voice, around 40s, honest and a little emotional, ~2.4 words per second.\n"
 "CRITICAL — ONLY the right woman speaks. The woman on the LEFT holding the microphone stays "
 "SILENT the entire clip, mouth CLOSED, just listening and nodding slightly, makes NO sound.\n"
 "AUDIO CRITICAL: she speaks CLEARLY at full conversational volume, clean broadcast-quality audio.\n"
 "PRONUNCIATION LOCK: 'Chowchilla' is said 'Chow-CHILL-uh'.\n"
 "DIALOGUE LOCK: English only, no filler, no extra or trailing words, stop after the final word.\n"
 "SPOKEN DIALOGUE (verbatim): \"Wait, for real? My cousin was in Chow-CHILL-uh. She never told "
 "anybody what happened to her in there. The things those guards did to those women, it was wrong. "
 "And nobody believed them, because they were locked up. So if California is finally doing "
 "something about it, that is about time. Those women deserve that.\"\n"
 "No on-screen text, no captions, no subtitles."
)
print("[prompt]\n"+PROMPT+"\n")
print("[gen] Grok Imagine i2v, 30s, 720p, 16:9")
r = generate_grok(PROMPT, image_urls=[url], duration="30", resolution="720p", aspect_ratio="16:9")
if r.get("urls"):
    dst = OUT / "voxpop_A_grok30.mp4"
    dst.write_bytes(requests.get(r["urls"][0], timeout=600).content)
    print("[done] ->", dst)
else:
    print("[FAIL]", str(r.get("raw"))[:500])
