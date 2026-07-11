"""VEO version of the conversational street interview — ONE speaker per clip (the other stays
SILENT), Veo's clean-interview method. Poyo Veo 3.1 Fast 8s, v2_profile two-shot anchor.
Crop-to-speaker + trim in assembly. skip-if-exists.
"""
import sys, pathlib, requests, concurrent.futures as cf
from kie_client import upload_file
from poyo_client import generate_veo

OUT = pathlib.Path("outputs/wp_voxpop/interview_veo"); OUT.mkdir(parents=True, exist_ok=True)
ANCHOR = "outputs/wp_voxpop/twoshot/v2_profile.png"
PRON = ("PRONUNCIATION: 'Chowchilla' = three English syllables chow (rhymes with cow) + chill + uh, "
        "stress the middle syllable, one fluid word, never Spanish. ")

# (idx, speaker L=reporter/R=woman, line)
TURNS = [
 (1,"L","Nearly 500 women who were incarcerated in California's prisons are coming forward. You were at Chowchilla. What happened in there?"),
 (2,"R","The guards crossed the line. Sexually. And back then, nobody would have believed us."),
 (3,"L","A lot of women think that because they never reported it, it is too late."),
 (4,"R","That is exactly what I thought. I thought it was my fault."),
 (5,"L","Under California law, a woman in prison cannot consent to a guard. So women like you may qualify for significant potential compensation."),
 (6,"R","Wait. Even after all these years?"),
 (7,"L","Even now. It is free to check, completely confidential, and you never go to court."),
 (8,"R","If I had only known that sooner."),
 (9,"L","If you were at Chowchilla, Valley State, or Folsom, there is a private two-minute form."),
 (10,"R","So anyone who was in there should check?"),
 (11,"L","Yes. Tap below and see if you qualify."),
]

def prompt_for(spk, line):
    who = ("The reporter on the LEFT (denim jacket, holding the microphone)" if spk=="L"
           else "The woman on the RIGHT (grey hoodie, weathered)")
    other = "the woman on the RIGHT" if spk=="L" else "the reporter on the LEFT"
    pron = PRON if "Chowchilla" in line else ""
    return (
     "Wide 16:9 candid street interview on a sunny sidewalk, locked static camera. "
     f"{who} speaks, calm and natural, ~2.4 words per second. "
     f"CRITICAL — ONLY {who.split(' (')[0].lower()} speaks; {other} stays SILENT the entire clip, "
     "mouth CLOSED, just listening, makes NO sound. "
     "AUDIO CRITICAL: clear full conversational volume, clean broadcast-quality, NO music. " + pron +
     "DIALOGUE LOCK: English only, no filler, no 'um/uh', no extra or trailing words, stop after the "
     f"final word. SPOKEN DIALOGUE (verbatim): \"{line}\". No on-screen text, no captions.")

url = upload_file(ANCHOR)
only = int(sys.argv[1]) if len(sys.argv) > 1 else None

def gen(item):
    idx, spk, line = item
    if only and idx != only: return None
    dst = OUT / f"t{idx:02d}_{spk}.mp4"
    if dst.exists(): return f"[skip] t{idx}"
    r = generate_veo(prompt_for(spk, line), image_urls=[url, url], aspect_ratio="16:9",
                     resolution="720p", generation_type="frame")
    if r.get("urls"):
        dst.write_bytes(requests.get(r["urls"][0], timeout=300).content); return f"[done] t{idx}"
    return f"[FAIL] t{idx} {str(r.get('raw'))[:120]}"

with cf.ThreadPoolExecutor(max_workers=6) as ex:
    for res in ex.map(gen, TURNS):
        if res: print(res, flush=True)
print("VEO INTERVIEW PRODUCE DONE")
