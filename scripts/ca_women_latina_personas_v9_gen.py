"""
CA Women's Prison — 4 American Latina Personas v9 (ages 45–60)
California-raised Latinas, relatable everyday look, UGC selfie mode
Not over-aged / not over-weathered — authentic but approachable
useapi.net nano-banana-pro | 9:16
"""
import os, requests, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
OUT = Path("outputs/ca_women_latina_personas_v9")
OUT.mkdir(parents=True, exist_ok=True)

PERSONAS = [
    {
        "id": "persona_CWL9_F1",
        "label": "Latina 48 — Mexican-American, East LA — indoor bedroom selfie",
        "prompt": (
            "UGC phone selfie, 9:16 vertical portrait. "
            "Phone held at arm's length, eye level, seated on a bed. "
            "Looking directly at the camera. Candid, real — NOT a studio portrait.\n\n"
            "48-year-old Mexican-American woman, born and raised in East Los Angeles. "
            "FACE: round soft oval — full cheeks, warm brown skin, medium-dark "
            "warm complexion, golden undertone. "
            "Natural aging: forehead lines, smile lines around the mouth, "
            "slight under-eye shadows, visible pores — NOT heavily carved or deeply wrinkled. "
            "Looks 48, not 65. "
            "NO makeup, no filter, no retouching, no beauty mode. "
            "HAIR: dark brown hair, grown-out, grey appearing at the roots and temples — "
            "pulled into a messy ponytail or half-up. Simple and practical. "
            "EYES: warm dark brown, direct steady gaze at the lens. "
            "MOUTH: medium lips, natural warm tone, relaxed neutral expression. "
            "Natural teeth — not bright white, not polished. "
            "BODY: medium build, visible neck and shoulders. "
            "CLOTHING: plain heather-grey or navy t-shirt, lived-in.\n\n"
            "SETTING: indoor — small bedroom, simple. Plain wall or headboard slightly "
            "blurred behind her, warm lamp or window light. Background fully blurred.\n\n"
            "Photoreal phone selfie. Ordinary everyday American Latina woman. "
            "Real skin, natural hair, no beauty filter. 9:16 vertical, photo-realistic."
        ),
    },
    {
        "id": "persona_CWL9_F2",
        "label": "Latina 55 — Cuban-American, Bay Area — outdoor front porch selfie",
        "prompt": (
            "UGC phone selfie, 9:16 vertical portrait. "
            "Phone held at arm's length, slightly above eye level — standing on a front "
            "porch or front step of a house, looking up at the lens. "
            "Candid, real — NOT a studio portrait.\n\n"
            "55-year-old Cuban-American woman, raised in the San Francisco Bay Area. "
            "FACE: long oval — higher cheekbones, slightly angular jaw, "
            "warm light-to-medium olive-brown complexion, Spanish-Caribbean mix. "
            "Natural aging for 55: forehead lines, defined nasolabial folds, "
            "slight hollowing under the cheekbones, under-eye shadows — "
            "looks 55, natural and real, NOT extreme weathering. "
            "NO makeup, no filter, no retouching, no beauty mode. "
            "HAIR: wavy medium-brown hair, significant silver-grey throughout — "
            "worn loose to the shoulder or in a loose low bun. "
            "Natural wave, not styled, grey roots blending in. "
            "EYES: warm hazel-brown, direct gaze at the lens, a measured steadiness. "
            "MOUTH: medium lips, natural tone, composed resting expression. "
            "Natural teeth, not polished. "
            "BODY: slim to medium build, visible neck and collarbone. "
            "CLOTHING: open button-down flannel shirt over a plain white tank top, casual.\n\n"
            "SETTING: outdoor — front porch or front steps of a modest Bay Area house. "
            "Afternoon soft natural light on her face. Blurred background — "
            "wood railing, garden, parked car at the curb. "
            "Quiet residential neighborhood, unglamorous.\n\n"
            "Photoreal phone selfie. Ordinary everyday American Latina woman. "
            "Real skin, natural grey-streaked hair, no beauty filter. 9:16 vertical, photo-realistic."
        ),
    },
    {
        "id": "persona_CWL9_F3",
        "label": "Latina 52 — Colombian-American, San Fernando Valley — indoor kitchen selfie",
        "prompt": (
            "UGC phone selfie, 9:16 vertical portrait. "
            "Phone held at arm's length, slightly below eye level — sitting at a kitchen "
            "table, looking up into the lens. Candid, real — NOT a studio portrait.\n\n"
            "52-year-old Colombian-American woman, raised in the San Fernando Valley, Los Angeles. "
            "FACE: heart-shaped — broader forehead, high defined cheekbones, "
            "slightly fuller mid-cheek, softly tapered jaw. "
            "Skin: warm medium olive-brown, South American Latina complexion. "
            "Natural aging for 52: moderate forehead lines, smile lines, "
            "slight under-eye darkness, natural skin texture and pores — "
            "looks 52, NOT aggressively aged. "
            "NO makeup, no filter, no retouching, no beauty mode. "
            "HAIR: straight dark brown hair, heavily streaked with grey — "
            "more than half grey now, dark underneath. "
            "Worn loose or in a simple low ponytail, flat and practical, not styled. "
            "EYES: warm medium brown, alert and direct, looking straight into the lens. "
            "MOUTH: medium full lips, natural warm rose tone, relaxed neutral expression. "
            "Natural teeth, slightly imperfect, not polished. "
            "BODY: medium build, visible neck and upper chest. "
            "VISIBLE DETAIL: a small simple tattoo on the forearm or wrist — older ink, faded. "
            "CLOTHING: plain dark green or black scoop-neck top, simple and worn.\n\n"
            "SETTING: indoor — modest apartment kitchen, small California apartment. "
            "Plain table surface visible at frame edge, simple overhead light. "
            "Background fully blurred — basic kitchen countertop or cabinets.\n\n"
            "Photoreal phone selfie. Ordinary everyday American Latina woman. "
            "Real skin, grey-streaked hair, faded tattoo, no beauty filter. "
            "9:16 vertical, photo-realistic."
        ),
    },
    {
        "id": "persona_CWL9_F4",
        "label": "Latina 58 — Puerto Rican-American, Inland Empire — outdoor apartment balcony selfie",
        "prompt": (
            "UGC phone selfie, 9:16 vertical portrait. "
            "Phone held at arm's length, eye level — standing on a small apartment balcony "
            "or leaning against an exterior railing, looking directly at the lens. "
            "Candid, real — NOT a studio portrait.\n\n"
            "58-year-old Puerto Rican-American woman, raised in the Inland Empire "
            "(Riverside / San Bernardino). Boricua heritage — Caribbean Latina, "
            "warm brown complexion with reddish-golden undertone. "
            "FACE: full round oval — broad soft cheekbones, full cheeks, "
            "rounded chin, broad forehead. "
            "Skin: warm medium-dark honey-brown, Caribbean complexion. "
            "Natural aging for 58: forehead creases, pronounced smile lines, "
            "some jowl softness beginning, under-eye shadows and slight puffiness — "
            "looks 58, real and lived-in, NOT extreme. "
            "NO makeup, no filter, no retouching, no beauty mode. "
            "HAIR: natural curly-wavy hair (3A-3B), dark brown heavily mixed with silver-grey — "
            "majority grey now, worn loosely pulled back or in a low curly ponytail, "
            "some curls escaping around the face. Natural texture, not blown out. "
            "EYES: warm dark brown, wide and direct, carrying quiet weight and steadiness. "
            "MOUTH: medium-full lips, natural warm tone, neutral composed expression. "
            "Natural teeth, not polished. "
            "BODY: fuller heavier build, visible neck and upper chest. "
            "CLOTHING: plain purple or dark teal v-neck t-shirt, comfortable and worn.\n\n"
            "SETTING: outdoor — small apartment balcony or exterior corridor, "
            "Inland Empire apartment complex. Flat afternoon California daylight. "
            "Blurred background — plain stucco wall or railing, parking lot below. "
            "Real unglamorous California apartment exterior.\n\n"
            "Photoreal phone selfie. Ordinary everyday American Latina woman. "
            "Real skin, natural curly-grey hair, no beauty filter. "
            "9:16 vertical, photo-realistic."
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
        print(f"  {pid}_v{i+1}: saved {vpath.stat().st_size // 1024}KB")

    if saved:
        shutil.copy(saved[0], out_path)

    print(f"✓ {pid}: [{p['label']}]  ({len(saved)} variants)")
    return pid, str(out_path)


if __name__ == "__main__":
    print(f"CA Women Latina Personas V9 (American Latina, ages 45–60) — nano-banana-pro → {OUT}\n")
    print("F1: 48  Mexican-American / East LA          — bedroom (indoor)")
    print("F2: 55  Cuban-American / Bay Area           — front porch (outdoor)")
    print("F3: 52  Colombian-American / San Fernando   — kitchen (indoor)")
    print("F4: 58  Puerto Rican-American / IE          — apartment balcony (outdoor)\n")

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
