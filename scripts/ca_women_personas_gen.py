"""
CA Women's Prison (CCWF/CIW Chowchilla) — 4 Survivor Personas
3 Latina + 1 Black | ages 42–62 | 2 outdoor + 2 indoor | working-class CA settings
useapi.net nano-banana-pro | 9:16 | realism tail baked in
"""
import os, requests, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
OUT = Path("outputs/ca_women_personas")
OUT.mkdir(parents=True, exist_ok=True)

# Shared realism tail — never glamorous, survivor-real, hard-lived
REAL = (
    "Photoreal candid documentary phone portrait, NOT a glamour or fashion shoot, "
    "NOT a celebrity portrait — an ordinary, everyday, hard-lived woman with plain average features. "
    "Weathered real skin with visible pores, sun damage, fine lines and wrinkles, under-eye darkness, "
    "no makeup or minimal, no filter, no retouching, no beauty mode, no skin smoothing. "
    "Tired but steady eyes carrying weight. Practical un-styled hair with grown-out color and grey roots. "
    "Plain worn clothing. 9:16 vertical portrait, photo-realistic."
)

PERSONAS = [
    {
        "id": "persona_CW_F1",
        "label": "Latina — 52 — Outside, Central Valley front porch — afternoon",
        "prompt": (
            "Portrait photograph of a 52-year-old Latina woman, medium close-up framing from "
            "mid-torso to top of head, sitting on the front porch of a modest older Central Valley "
            "home. Sun-worn olive-tan skin, deep crow's-feet and forehead lines, weathered hands. "
            "Greying dark hair pulled back in a simple low ponytail with loose strands, natural "
            "grey at the temples. Calm tired direct gaze straight into the camera lens, mouth "
            "closed and neutral, a heaviness behind the eyes. A small old faded tattoo on the "
            "forearm. Wearing a plain worn maroon t-shirt and a thin open cardigan. "
            "Warm late-afternoon Central Valley sunlight, slightly hazy, soft golden side light. "
            "Background slightly out of focus — chipped porch railing, a screen door, a potted "
            "plant, dry yellow-brown yard and a quiet residential street beyond. " + REAL
        ),
    },
    {
        "id": "persona_CW_F2",
        "label": "Latina — 45 — Inside, small kitchen — window light",
        "prompt": (
            "Portrait photograph of a 45-year-old Latina woman, close-up framing from shoulders "
            "to top of head, standing in the small kitchen of a modest working-class California "
            "apartment. Medium-tan skin with visible pores and fine lines, faint acne scarring on "
            "one cheek, slight under-eye shadow. Shoulder-length dark brown hair with grown-out "
            "roots, pulled half-back, a little frizz. Steady serious gaze directly into the lens, "
            "lips closed, jaw set, holding something back. Wearing a plain grey long-sleeve thermal "
            "shirt. Soft natural daylight from a side kitchen window, warm subdued indoor tone. "
            "Background slightly out of focus — older laminate counter, a few everyday dishes on a "
            "drying rack, plain off-white cabinets, a wall calendar, lived-in unstaged domestic space. "
            + REAL
        ),
    },
    {
        "id": "persona_CW_F3",
        "label": "Latina — 60 — Outside, older sedan / parking lot — overcast",
        "prompt": (
            "Portrait photograph of a 60-year-old Latina woman, medium close-up framing from "
            "chest to top of head, standing beside an older sedan in a plain parking lot. "
            "Deeply sun-weathered olive skin, pronounced wrinkles, sagging under-eyes, age spots, "
            "thin lips. Short practical greying dark hair, mostly grey, simple and un-styled. "
            "Direct weary gaze into the camera lens, mouth a flat neutral line, weight of decades "
            "in the expression. Wearing a plain navy zip-up fleece jacket over a faded shirt. "
            "Flat overcast Central California daylight, even soft light, no harsh shadows. "
            "Background slightly out of focus — the side of a dull older sedan, faded asphalt, "
            "a cinder-block wall, a distant strip-mall edge, ordinary working-class setting. " + REAL
        ),
    },
    {
        "id": "persona_CW_F4",
        "label": "Black — 48 — Inside, plain bedroom / edge of bed — lamp light",
        "prompt": (
            "Portrait photograph of a 48-year-old Black African-American woman, close-up framing "
            "from shoulders to top of head, sitting on the edge of a bed in a plain modest bedroom. "
            "Deep brown skin with visible pores, fine lines, under-eye darkness, a few faint "
            "blemishes, natural texture. Natural hair pulled back simply with edges showing grey, "
            "or a short practical natural style, un-styled. Steady tired direct gaze into the "
            "camera lens, lips closed, a quiet steadiness, carrying weight. Wearing a plain "
            "worn charcoal hoodie. Warm low lamp light from the side, soft shadows across the "
            "room, subdued evening indoor tone. Background slightly out of focus — a simple "
            "headboard, a plain bedspread, a nightstand with a lamp, an off-white wall, modest "
            "lived-in bedroom. " + REAL
        ),
    },
]


def generate(p):
    pid = p["id"]
    out_path = OUT / f"{pid}.jpg"
    if out_path.exists() and out_path.stat().st_size > 50_000:
        print(f"  {pid}: exists ({out_path.stat().st_size // 1024}KB), skipping")
        return pid, str(out_path)

    payload = {
        "prompt": p["prompt"],
        "model": "nano-banana-pro",
        "aspectRatio": "9:16",
    }
    r = requests.post(
        "https://api.useapi.net/v1/google-flow/images",
        headers=HEADERS, json=payload, timeout=120,
    )
    if r.status_code not in (200, 201):
        raise RuntimeError(f"{pid}: {r.status_code} {r.text[:300]}")

    data = r.json()
    media = data.get("media", [])
    if not media:
        raise RuntimeError(f"{pid}: no media in response — {data}")

    saved = []
    for i, m in enumerate(media):
        g = m.get("image", {}).get("generatedImage", {})
        url = g.get("fifeUrl", "")
        mid = g.get("mediaGenerationId", "")
        if not url:
            continue
        vpath = OUT / f"{pid}_v{i+1}.jpg"
        img_r = requests.get(url, timeout=60)
        img_r.raise_for_status()
        vpath.write_bytes(img_r.content)
        saved.append(vpath)
        print(f"  {pid}_v{i+1}: saved {vpath.stat().st_size // 1024}KB  mediaId: {mid}")

    if saved:
        shutil.copy(saved[0], out_path)

    print(f"✓ {pid}: {out_path}  [{p['label']}]  ({len(saved)} variants)")
    return pid, str(out_path)


if __name__ == "__main__":
    print(f"CA Women's Prison — 4 Survivor Personas (nano-banana-pro) → {OUT}\n")
    print("F1: Latina 52, Central Valley porch | F2: Latina 45, small kitchen")
    print("F3: Latina 60, older sedan lot | F4: Black 48, plain bedroom\n")

    results = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(generate, p): p["id"] for p in PERSONAS}
        for fut in as_completed(futs):
            pid = futs[fut]
            try:
                pid, path = fut.result()
                results[pid] = path
            except Exception as e:
                print(f"✗ {pid} ERROR: {e}")

    print(f"\nCompleted: {len(results)}/4")
    for pid in sorted(results):
        print(f"  {pid}: {results[pid]}")
