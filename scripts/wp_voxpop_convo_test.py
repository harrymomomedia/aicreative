"""Back-and-forth conversation test — BOTH women speak, taking turns, in ONE clip.
Tests distinct-voice separation (Veo's known weak spot) on Grok (15s, 4 turns) vs Veo (8s, 2 turns).
Same v2 two-shot anchor.
"""
import sys, pathlib, requests
from kie_client import upload_file, generate_grok
from poyo_client import generate_veo

OUT = pathlib.Path("outputs/wp_voxpop/convo"); OUT.mkdir(parents=True, exist_ok=True)
url = upload_file("outputs/wp_voxpop/twoshot/v2_profile.png")

COMMON = (
 "Wide 16:9 candid street interview, locked static camera. A NATURAL BACK-AND-FORTH conversation "
 "between the two women. They TAKE TURNS — only one talks at a time while the other listens with "
 "mouth CLOSED. DISTINCT voices: the interviewer on the LEFT (denim jacket) is younger, warmer, "
 "brighter; the woman on the RIGHT (grey hoodie) is older, lower, weathered Latina. ~2.4 words/sec.\n"
 "PRONUNCIATION LOCK: 'Chowchilla' = 'Chow-CHILL-uh'.\n"
 "DIALOGUE LOCK: English only, no filler, follow the exact lines and speaker order.\n"
 "No on-screen text, no captions, no subtitles.\n"
)
FULL = COMMON + (
 "SPOKEN DIALOGUE (verbatim, in order):\n"
 "INTERVIEWER: \"Did you know women abused at Chow-CHILL-uh may qualify for significant potential compensation?\"\n"
 "WOMAN: \"Wait, for real? My cousin was in there. She never told anybody what happened.\"\n"
 "INTERVIEWER: \"It is free and confidential to check.\"\n"
 "WOMAN: \"That is about time. Those women deserve that.\"\n"
)
SHORT = COMMON + (
 "SPOKEN DIALOGUE (verbatim, in order):\n"
 "INTERVIEWER: \"Did you know women abused at Chow-CHILL-uh may qualify for compensation?\"\n"
 "WOMAN: \"Wait, for real? My cousin was in there.\"\n"
)

def run_grok():
    print("[grok] 15s back-and-forth"); r = generate_grok(FULL, image_urls=[url], duration="15",
        resolution="720p", aspect_ratio="16:9")
    if r.get("urls"):
        (OUT/"convo_grok15.mp4").write_bytes(requests.get(r["urls"][0], timeout=600).content); print("[grok done]")
    else: print("[grok FAIL]", str(r.get("raw"))[:300])

def run_veo():
    print("[veo] 8s 2-turn"); r = generate_veo(SHORT, image_urls=[url, url], aspect_ratio="16:9",
        resolution="720p", generation_type="frame")
    if r.get("urls"):
        (OUT/"convo_veo8.mp4").write_bytes(requests.get(r["urls"][0], timeout=300).content); print("[veo done]")
    else: print("[veo FAIL]", str(r.get("raw"))[:300])

which = sys.argv[1] if len(sys.argv) > 1 else "both"
if which in ("grok","both"): run_grok()
if which in ("veo","both"): run_veo()
