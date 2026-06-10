"""
CA Women's Prison — 4 DISTINCT Latina Personas (ages 42–45) — CLOSE-UP
Each woman visually differentiated: different heritage features, face shape,
skin tone, hair type, age markers, and setting.
2 outdoor + 2 indoor | useapi.net nano-banana-2 | 9:16
"""
import os, requests, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
OUT = Path("outputs/ca_women_latina_personas_v3")
OUT.mkdir(parents=True, exist_ok=True)

PERSONAS = [
    {
        "id": "persona_CWL3_F1",
        "label": "Latina 42 — Oaxacan/Mexican indigenous features — backyard steps — outdoor morning",
        "prompt": (
            "Extreme close-up portrait photograph, face filling the 9:16 frame from chin to crown. "
            "42-year-old Mexican-American woman with Oaxacan indigenous heritage. "
            "FACE SHAPE: broad, wide, flat — prominent wide cheekbones, flat wide nose with a rounded tip, "
            "strong square jaw, low forehead. "
            "SKIN: deep warm copper-brown, heavily sun-weathered, NOT olive — deep tan with warm reddish-brown undertone. "
            "Visible pores, forehead creases, deep smile lines, small raised mole above the lip on the right side. "
            "HAIR: thick coarse black hair cut very short — barely jaw-length, slight natural wave, "
            "prominent grey streaks running through from the temples, no styling, air-dried. "
            "EYES: dark near-black brown, slightly deep-set under heavy brows, calm and direct into the lens. "
            "MOUTH: full lips, flat neutral line, closed. "
            "SETTING: outdoors, seated on concrete back-porch steps of a modest California home, "
            "soft morning side-light, warm diffuse sun, background completely blurred — "
            "weathered stucco wall and a potted cactus out of focus. "
            "Wearing a plain faded olive-green t-shirt. "
            "Photoreal documentary phone portrait, NOT glamour, NOT celebrity — ordinary everyday hard-lived woman. "
            "Visible pores, sun damage, no makeup, no filter, no retouching, no beauty mode. "
            "9:16 vertical portrait, photo-realistic."
        ),
    },
    {
        "id": "persona_CWL3_F2",
        "label": "Latina 44 — Salvadoran/Central American features — outdoor swap meet — bright midday",
        "prompt": (
            "Extreme close-up portrait photograph, face filling the 9:16 frame from chin to crown. "
            "44-year-old Salvadoran-American woman. "
            "FACE SHAPE: narrow elongated oval face, high sharply defined cheekbones, slightly pointed chin, "
            "long straight nose with a slight downward hook at the tip. "
            "SKIN: light golden tan, warm yellow-golden undertone, NOT olive-brown — lighter than average Latina, "
            "slight freckling across the nose bridge, fine lines around the eyes and at the corners of the mouth, "
            "slightly uneven skin tone. "
            "HAIR: long straight dark brown hair with significant grey roots growing in at the part, "
            "pulled back tightly in a simple low ponytail, a few escaped strands around the face, slightly dry. "
            "EYES: medium brown, almond-shaped, calm and level, looking straight into the lens. "
            "MOUTH: thin lips pressed together in a flat neutral line. "
            "SETTING: outdoors at an open-air swap meet or flea market, bright flat midday California sun, "
            "harsh even light with slight bleaching. Background completely blurred — "
            "colorful vendor stalls and fabric out of focus. "
            "Wearing a plain light-blue button-down shirt. "
            "Photoreal documentary phone portrait, NOT glamour, NOT celebrity — ordinary everyday hard-lived woman. "
            "Visible pores, fine lines, no makeup, no filter, no retouching, no beauty mode. "
            "9:16 vertical portrait, photo-realistic."
        ),
    },
    {
        "id": "persona_CWL3_F3",
        "label": "Latina 43 — Puerto Rican/Caribbean features — indoor living room sofa — lamp light",
        "prompt": (
            "Extreme close-up portrait photograph, face filling the 9:16 frame from chin to crown. "
            "43-year-old Puerto Rican woman. "
            "FACE SHAPE: round full-cheeked face, soft rounded jawline, round forehead, small chin. "
            "SKIN: warm medium-brown with reddish undertone — deeper than tan, lighter than dark brown, "
            "NOT olive — a warm caramel-brown. Visible pores, slight under-eye puffiness, "
            "faint dark circles, natural blemish on the chin, soft forehead lines. "
            "HAIR: thick curly dark brown hair, mixed with grey throughout, "
            "shoulder-length, worn loose and natural — ringlets and waves, "
            "some frizz, not styled or blown out. "
            "EYES: warm medium brown, round and slightly wide-set, steady gaze into the lens, "
            "a heaviness in the expression. "
            "MOUTH: full lips, naturally dark pink, soft neutral line, not smiling. "
            "SETTING: indoors, seated on a sofa in a modest California living room, "
            "warm amber-orange lamp light from the side, soft shadows, evening. "
            "Background completely blurred — a worn couch cushion and a plain wall with a framed photo out of focus. "
            "Wearing a plain dark-red scoop-neck top. "
            "Photoreal documentary phone portrait, NOT glamour, NOT celebrity — ordinary everyday hard-lived woman. "
            "Visible pores, no makeup, no filter, no retouching, no beauty mode. "
            "9:16 vertical portrait, photo-realistic."
        ),
    },
    {
        "id": "persona_CWL3_F4",
        "label": "Latina 45 — Mestiza Mexican lighter features — indoor laundromat — fluorescent light",
        "prompt": (
            "Extreme close-up portrait photograph, face filling the 9:16 frame from chin to crown. "
            "45-year-old Mexican-American woman, lighter mestiza features. "
            "FACE SHAPE: square angular jaw, wide forehead, strong prominent brow ridge, "
            "deep-set hooded eyes, angular nose with a defined bridge. "
            "SKIN: medium-light olive, cool undertone, NOT warm brown — more European-leaning complexion. "
            "Fine lines at the eyes, vertical frown lines between the brows, slight under-eye shadows, "
            "a few age spots on the temple. "
            "HAIR: short blunt bob cut just below the ears, dark brown-black hair "
            "with a dramatic wide natural silver-white streak running from the front hairline — "
            "a distinctive natural grey streak, not dyed, rest of hair dark. Un-styled and slightly flat. "
            "EYES: dark brown, deep-set under heavy brows, direct and serious gaze into the lens. "
            "MOUTH: medium lips, flat serious neutral line, jaw slightly set. "
            "SETTING: indoors at a laundromat — harsh flat fluorescent overhead lighting, "
            "cold neutral-white cast, slightly unflattering even illumination. "
            "Background completely blurred — a row of washing machines and a folding table out of focus. "
            "Wearing a plain dark charcoal zip-up hoodie. "
            "Photoreal documentary phone portrait, NOT glamour, NOT celebrity — ordinary everyday hard-lived woman. "
            "Visible pores, no makeup, no filter, no retouching, no beauty mode. "
            "9:16 vertical portrait, photo-realistic."
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
        "model": "nano-banana-2",
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
    print(f"CA Women Latina Personas V3 (DISTINCT close-ups) — nano-banana-2 → {OUT}\n")
    print("F1: 42, Oaxacan/Mexican indigenous — backyard steps (outdoor)")
    print("F2: 44, Salvadoran — swap meet (outdoor)")
    print("F3: 43, Puerto Rican — living room sofa (indoor)")
    print("F4: 45, Mestiza Mexican — laundromat (indoor)\n")

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
