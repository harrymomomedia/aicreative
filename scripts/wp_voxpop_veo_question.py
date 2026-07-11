"""Missing piece — the INTERVIEWER QUESTION clip (one speaker = interviewer).
Interviewer asks the compliant question; Respondent A listens SILENT.
Same v2 two-shot anchor, Poyo Veo 3.1 Fast 16:9 8s. Cut Q -> A in edit.
"""
import pathlib, requests
from kie_client import upload_file
from poyo_client import generate_veo

OUT = pathlib.Path("outputs/wp_voxpop/veo"); OUT.mkdir(parents=True, exist_ok=True)
url = upload_file("outputs/wp_voxpop/twoshot/v2_profile.png")

PROMPT = (
 "Wide 16:9 candid street interview, locked static camera. The woman on the LEFT (denim jacket) "
 "holds the microphone up and ASKS a question, warm friendly reporter tone, looking at the woman "
 "beside her, ~2.4 words per second.\n"
 "CRITICAL — ONLY the left woman (interviewer) speaks. The woman on the RIGHT in the grey hoodie "
 "stays SILENT the whole clip, mouth CLOSED, just listening, makes NO sound.\n"
 "AUDIO CRITICAL: the interviewer speaks CLEARLY at full conversational volume, clean "
 "broadcast-quality audio. NOT salesy, NO TV-ad inflection on 'compensation'.\n"
 "PRONUNCIATION LOCK: 'Chowchilla' is said 'Chow-CHILL-uh'.\n"
 "DIALOGUE LOCK: English only, no filler, no extra or trailing words, stop after the final word.\n"
 "SPOKEN DIALOGUE (verbatim): \"Did you know women who were abused at California prisons like "
 "Chow-CHILL-uh may qualify for significant potential compensation?\"\n"
 "No on-screen text, no captions, no subtitles."
)
print("[prompt]\n"+PROMPT+"\n[gen] Poyo veo3.1-fast 16:9 720p frame mode")
r = generate_veo(PROMPT, image_urls=[url, url], aspect_ratio="16:9", resolution="720p",
                 generation_type="frame")
if r.get("urls"):
    dst = OUT / "voxpop_Q_test.mp4"
    dst.write_bytes(requests.get(r["urls"][0], timeout=300).content)
    print("[done] ->", dst)
else:
    print("[FAIL]", str(r.get("raw"))[:400])
