"""Two-shot composite anchors for respondents B and C (interviewer + each), balanced profile.
Uses the fixed input_urls i2i (identity-preserving) + minimal prompt.
"""
import pathlib, concurrent.futures as cf, requests
from kie_client import generate_gpt_image, upload_file

REF = pathlib.Path("outputs/wp_voxpop/reference")
OUT = pathlib.Path("outputs/wp_voxpop/twoshot"); OUT.mkdir(parents=True, exist_ok=True)

iv = upload_file(str(REF / "interviewer.png"))

def build(slug, respondent_png):
    ra = upload_file(str(REF / respondent_png))
    prompt = (
      "Put these two exact people together in ONE candid documentary street-interview photo, wide "
      "16:9 horizontal framing on a sunny sidewalk. FIRST person = the interviewer holding the "
      "microphone, on the LEFT facing right. SECOND person = the woman being interviewed, on the "
      "RIGHT facing left, microphone between them near center, both faces clearly visible. "
      "No on-screen text.")
    r = generate_gpt_image(prompt, image_urls=[iv, ra], aspect_ratio="16:9", resolution="2K")
    if r.get("status") == "success" and r.get("urls"):
        dst = OUT / f"{slug}.png"
        dst.write_bytes(requests.get(r["urls"][0], timeout=120).content)
        return slug, str(dst)
    return slug, f"FAIL: {str(r.get('raw'))[:150]}"

jobs = {"v2_profile_B": "respondent_b.png", "v2_profile_C": "respondent_c.png"}
with cf.ThreadPoolExecutor(max_workers=2) as ex:
    for slug, res in ex.map(lambda kv: build(*kv), jobs.items()):
        print(f"[done] {slug} -> {res}")
print("ALL DONE")
