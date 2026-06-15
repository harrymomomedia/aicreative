"""
CA Women's Prison — 4 American Latina Personas v10 (ages 50–60)
More variety: lighter/darker complexions, contemporary American styling,
no over-ethnic markers. Different from v8/v9 faces.
useapi.net nano-banana-pro | 9:16
"""
import os, requests, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
OUT = Path("outputs/ca_women_latina_personas_v10")
OUT.mkdir(parents=True, exist_ok=True)

REALISM = (
    "Photoreal candid phone selfie. NOT a glamour or fashion shoot, NOT a studio portrait. "
    "Ordinary everyday American woman. Natural skin with visible pores, fine lines, "
    "slight under-eye shadows, imperfect teeth, no beauty retouching, no filter, no makeup, "
    "no beauty mode. 9:16 vertical, photo-realistic."
)

PERSONAS = [
    {
        "id": "persona_CWL10_F1",
        "label": "Latina 54 — medium-light olive, dyed auburn hair, living room couch",
        "prompt": (
            "UGC phone selfie, 9:16 vertical portrait. "
            "Phone held at arm's length, eye level, sitting on a couch. "
            "Looking directly into the camera. Candid, real.\n\n"
            "54-year-old Latina woman, born in the United States, California. "
            "FACE: oval face, medium-light olive skin tone, warm undertone — "
            "looks like she tans easily but is currently indoor-pale. "
            "Natural aging for 54: gentle forehead lines, smile lines, "
            "slight under-eye shadows — looks her age, not heavily aged. "
            "HAIR: shoulder-length, medium auburn-brown, clearly dyed (a common box-dye color), "
            "with lighter grown-out roots, slight frizz, not styled — just dried. "
            "EYES: dark brown, direct and calm, looking into the lens. "
            "MOUTH: medium lips, natural tone, neutral resting expression. "
            "BODY: medium build, visible neck and shoulders. "
            "CLOTHING: plain burgundy or dusty rose zip-up hoodie, comfortable.\n\n"
            "SETTING: indoor — living room couch, middle-class American home. "
            "Blurred background — a TV, bookshelf, or throw pillow visible behind her. "
            "Warm afternoon indoor light, nothing glamorous.\n\n"
            + REALISM
        ),
    },
    {
        "id": "persona_CWL10_F2",
        "label": "Latina 59 — light warm complexion, dark bob going grey, outside front door",
        "prompt": (
            "UGC phone selfie, 9:16 vertical portrait. "
            "Phone held at arm's length, slightly above eye level — standing just outside "
            "a front door or on a doorstep. Looking up at the camera. Candid, real.\n\n"
            "59-year-old Latina woman, American-born, California. "
            "FACE: square-oval face, light warm skin — fair Latina complexion, "
            "some sun spots and freckles across the nose and cheeks. "
            "Natural aging for 59: more defined lines around the mouth and eyes, "
            "some jowl softness, real skin texture — looks 59. "
            "HAIR: straight dark brown bob to the jaw, heavily mixed with grey and white — "
            "more than half grey now. Low-maintenance cut, not styled, slightly flat. "
            "EYES: dark hazel or warm brown, steady gaze. "
            "MOUTH: thin to medium lips, natural tone, composed neutral expression. "
            "BODY: slim to medium build, visible neck and collar. "
            "CLOTHING: navy blue or grey quarter-zip pullover, casual everyday.\n\n"
            "SETTING: outdoor — just outside a house or apartment front door. "
            "Overcast California daylight or soft afternoon shade. "
            "Blurred background — door frame, porch railing, stucco wall.\n\n"
            + REALISM
        ),
    },
    {
        "id": "persona_CWL10_F3",
        "label": "Latina 51 — warm medium-dark skin, natural curly hair, car selfie",
        "prompt": (
            "UGC phone selfie, 9:16 vertical portrait. "
            "Phone held at arm's length, eye level — sitting in the driver's seat of a car, "
            "seatbelt on, looking at the camera. Candid, real.\n\n"
            "51-year-old Latina woman, born in California. "
            "FACE: round face, warm medium-dark brown complexion, golden-brown skin tone. "
            "Natural aging for 51: moderate smile lines, some forehead lines, "
            "slight under-eye shadows — looks early 50s, real and relatable. "
            "HAIR: natural curly texture (3A), dark brown with scattered grey threads starting — "
            "still mostly dark, some grey at temples. Worn loose and natural, not blown out. "
            "EYES: warm dark brown, alert and direct. "
            "MOUTH: medium-full lips, natural warm tone, relaxed neutral. "
            "BODY: medium build, shoulders visible, seatbelt across chest. "
            "CLOTHING: plain white or light grey t-shirt under the seatbelt.\n\n"
            "SETTING: inside a car — driver's seat. "
            "Window behind her shows blurred California suburban street, trees, daylight. "
            "Real car interior — steering wheel visible, nothing fancy.\n\n"
            + REALISM
        ),
    },
    {
        "id": "persona_CWL10_F4",
        "label": "Latina 56 — warm medium olive, salt-and-pepper layers, backyard patio",
        "prompt": (
            "UGC phone selfie, 9:16 vertical portrait. "
            "Phone held at arm's length, slightly below eye level — standing or sitting "
            "on a backyard patio, looking up into the camera. Candid, real.\n\n"
            "56-year-old Latina woman, raised in California. "
            "FACE: long oval face, warm medium olive complexion — Mediterranean-Latino mix. "
            "Natural aging for 56: defined nasolabial folds, forehead lines, "
            "under-eye darkness, real skin — looks 56, not polished. "
            "HAIR: medium-length layered cut to the shoulder, salt-and-pepper — "
            "roughly half dark brown, half white-grey, blended throughout, not dyed. "
            "Worn loose, natural volume, slightly wavy, slightly flat. "
            "EYES: warm medium brown, calm and direct gaze. "
            "MOUTH: medium lips, natural tone, soft neutral expression. "
            "BODY: medium build, visible neck and upper chest. "
            "CLOTHING: plain olive green or tan short-sleeve button-front shirt, casual.\n\n"
            "SETTING: outdoor — backyard patio or side yard of a modest California home. "
            "Afternoon daylight, natural shadow. Blurred background — "
            "fence, dry California plants, patio chair edge.\n\n"
            + REALISM
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
        if not url:
            continue
        vpath = OUT / f"{pid}_v{i+1}.jpg"
        img_r = requests.get(url, timeout=60)
        img_r.raise_for_status()
        vpath.write_bytes(img_r.content)
        saved.append(vpath)
        print(f"  {pid}_v{i+1}: saved {vpath.stat().st_size // 1024}KB")

    if saved:
        shutil.copy(saved[0], out_path)

    print(f"✓ {pid}: [{p['label']}]  ({len(saved)} variants)")
    return pid, str(out_path)


if __name__ == "__main__":
    print(f"CA Women Latina Personas V10 (American Latina, ages 50–60) — nano-banana-pro → {OUT}\n")
    print("F1: 54  medium-light olive, auburn dyed hair    — living room couch (indoor)")
    print("F2: 59  light warm complexion, grey bob         — front doorstep (outdoor)")
    print("F3: 51  warm medium-dark, natural curly         — car selfie")
    print("F4: 56  medium olive, salt-and-pepper layers    — backyard patio (outdoor)\n")

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
