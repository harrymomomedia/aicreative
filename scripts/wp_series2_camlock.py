"""Derive into-lens CLOSER anchors for the 3 series-2 survivors via gpt-image-2 i2i.
Identity held via input_urls (their reverse-shot anchor), minimal prompt = only the pose/gaze
change: squared to camera, eyes locked on the lens, holding the same small podcast mic.
Writes <survivor>_cam.png. skip-if-exists.
"""
import pathlib, requests
from kie_client import generate_gpt_image, upload_file

REF = pathlib.Path("outputs/wp_series2/reference")
SURV = ["surv1_maria", "surv2_denise", "surv3_kathy"]
PROMPT = ("This exact same woman, same face, same hair, same earrings, same clothing, same courthouse-"
          "steps background. She now faces the camera straight on, squared to the lens, and BOTH eyes "
          "are locked DIRECTLY on the camera lens — looking right down the barrel of the lens at the "
          "viewer, not to either side, not down. She holds the same small black podcast microphone "
          "(round black foam ball, tiny blue LED) in her own hand near her mouth as if speaking to "
          "camera. Photoreal candid documentary photo, natural skin, no retouching, no filter. "
          "Waist-up vertical 9:16 framing.")

def main():
    for s in SURV:
        dst = REF / f"{s}_cam.png"
        if dst.exists(): print(f"[skip] {s}"); continue
        url = upload_file(str(REF / f"{s}.png"))
        r = generate_gpt_image(PROMPT, image_urls=[url], aspect_ratio="9:16", resolution="2K",
                               input_fidelity="high")
        if r.get("status") == "success" and r.get("urls"):
            dst.write_bytes(requests.get(r["urls"][0], timeout=120).content); print(f"[done] {s}")
        else:
            print(f"[FAIL] {s}", str(r.get("raw"))[:160])
    print("SERIES2 CAMLOCK DONE")

if __name__ == "__main__":
    main()
