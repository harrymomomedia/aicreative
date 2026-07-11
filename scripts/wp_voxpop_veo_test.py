"""Vox-pop Veo test clip from the v2 two-shot anchor.
ONE speaker per clip: Respondent A answers, interviewer holds mic + stays SILENT.
Poyo Veo 3.1 Fast, 16:9 (wide, for punch-in), frame mode (anchor passed twice).
"""
import pathlib, requests
from kie_client import upload_file
from poyo_client import generate_veo

OUT = pathlib.Path("outputs/wp_voxpop/veo"); OUT.mkdir(parents=True, exist_ok=True)
anchor = "outputs/wp_voxpop/twoshot/v2_profile.png"

print("[upload] anchor -> host")
url = upload_file(anchor)

PROMPT = (
 "Wide 16:9 candid street interview, locked static camera. The woman on the RIGHT in the grey "
 "hoodie answers, looking at the interviewer beside her, weathered low slightly-rough Latina "
 "voice, around 40s, surprised and guarded with a flicker of emotion, ~2.4 words per second.\n"
 "CRITICAL — ONLY the right woman speaks. The woman on the LEFT holding the microphone stays "
 "SILENT the entire clip, mouth CLOSED, just listening and nodding slightly, makes NO sound.\n"
 "AUDIO CRITICAL: she speaks CLEARLY at full conversational volume into the mic, clean "
 "broadcast-quality audio that fills the foreground.\n"
 "PRONUNCIATION LOCK: 'Chowchilla' is said 'Chow-CHILL-uh'.\n"
 "DIALOGUE LOCK: English only. No filler, no 'um/uh/like', no extra or trailing words. Speak only "
 "the words below, in order, and STOP after the final word.\n"
 "SPOKEN DIALOGUE (verbatim): \"Wait, for real? My cousin was in Chow-CHILL-uh. She never told "
 "anybody what happened in there.\"\n"
 "No on-screen text, no captions, no subtitles."
)
print("[prompt]\n"+PROMPT+"\n")
print("[gen] Poyo veo3.1-fast, 16:9 720p, frame mode")
r = generate_veo(PROMPT, image_urls=[url, url], aspect_ratio="16:9", resolution="720p",
                 generation_type="frame")
if r.get("urls"):
    dst = OUT / "voxpop_A_test.mp4"
    dst.write_bytes(requests.get(r["urls"][0], timeout=300).content)
    print("[done] ->", dst)
else:
    print("[FAIL]", str(r.get("raw"))[:400])
