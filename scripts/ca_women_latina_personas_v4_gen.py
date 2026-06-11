"""
CA Women's Prison — 4 DISTINCT Latina Personas v4 (ages 42–45)
Mixed framing: 2 extreme close-up + 2 medium close-up
2 outdoor + 2 indoor | fresh locations not used in v1/v2/v3
useapi.net nano-banana-2 | 9:16
"""
import os, requests, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
OUT = Path("outputs/ca_women_latina_personas_v4")
OUT.mkdir(parents=True, exist_ok=True)

PERSONAS = [
    {
        "id": "persona_CWL4_F1",
        "label": "Latina 43 — Guatemalan Maya — outdoor Fresno backyard citrus — MEDIUM CLOSE-UP",
        "prompt": (
            "Medium close-up portrait photograph, framed from mid-chest to top of head, "
            "subject centered in the 9:16 frame. "
            "43-year-old Guatemalan-American woman with Maya indigenous heritage. "
            "FACE SHAPE: very wide, short face — broad flat wide forehead, "
            "extremely wide prominent cheekbones, small rounded chin, flat nose with wide nostrils, "
            "low-set heavy brows. Compact facial structure. "
            "SKIN: deep warm copper-brown, heavy sun weathering, NOT olive — "
            "reddish-brown undertone with visible sun damage on cheeks, "
            "forehead lines, deep nasolabial folds, small raised moles on the left cheek. "
            "HAIR: very long thick straight jet-black hair with coarse texture, "
            "a few grey strands at the temples, worn loose, parted in the middle, "
            "falls past the chest, no styling. "
            "EYES: near-black dark brown, slightly wide-set, heavy-lidded, "
            "calm direct gaze into the lens. "
            "MOUTH: wide full lips, flat serious neutral line. "
            "BODY: wearing a plain washed-out burgundy V-neck t-shirt, visible chest and shoulders. "
            "SETTING: outdoors in a modest California Central Valley backyard, "
            "soft warm late-afternoon light filtering through citrus trees — "
            "oranges and lemons visible and blurred behind her in the background, "
            "weathered wood fence out of focus, dry California grass. "
            "Golden hour backyard, warm side-light on face. "
            "Photoreal documentary phone portrait, NOT glamour, NOT celebrity — "
            "ordinary hard-lived woman. Visible pores, sun damage, no makeup, no filter, "
            "no retouching, no beauty mode. 9:16 vertical portrait, photo-realistic."
        ),
    },
    {
        "id": "persona_CWL4_F2",
        "label": "Latina 45 — Dominican/Caribbean features — indoor California kitchen — EXTREME CLOSE-UP",
        "prompt": (
            "Extreme close-up portrait photograph, face filling the 9:16 frame from chin to crown. "
            "45-year-old Dominican-American woman with Caribbean heritage. "
            "FACE SHAPE: heart-shaped face — wide forehead tapering to a pointed narrow chin, "
            "high defined cheekbones, slightly concave temples, full rounded cheeks. "
            "SKIN: rich dark warm brown — deep mahogany-brown, NOT olive, NOT copper — "
            "a true deep brown with neutral-warm undertone. "
            "Visible pores, age spots on the forehead, soft forehead lines, "
            "natural dark skin around the eyes, slight under-eye puffiness. "
            "HAIR: medium-length natural hair with tight 4C coils, significant grey mixed throughout, "
            "worn loose and unstyled, volume and frizz at the crown, some coils at the forehead. "
            "Distinct: her hair is visibly coily-natural, very different texture from straight Latina hair. "
            "EYES: dark warm brown, medium-sized, direct steady gaze into the lens, "
            "slight tiredness at the edges. "
            "MOUTH: full lush lips, medium dark pink tone, flat neutral line. "
            "SETTING: indoors in a modest California kitchen — warm mid-afternoon window light "
            "coming from the right, slightly harsh natural light. Background completely blurred — "
            "kitchen tile backsplash, a pot on the stove, wooden cabinets out of focus. "
            "Photoreal documentary phone portrait, NOT glamour, NOT celebrity — "
            "ordinary hard-lived woman. Visible pores, no makeup, no filter, "
            "no retouching, no beauty mode. 9:16 vertical portrait, photo-realistic."
        ),
    },
    {
        "id": "persona_CWL4_F3",
        "label": "Latina 42 — Peruvian/Andean features — indoor Sacramento living room — MEDIUM CLOSE-UP",
        "prompt": (
            "Medium close-up portrait photograph, framed from mid-chest to top of head, "
            "subject centered in the 9:16 frame. "
            "42-year-old Peruvian-American woman with Andean heritage. "
            "FACE SHAPE: long rectangular face — narrow forehead, long straight nose with a slight hump "
            "at the bridge, strong angular jawline, prominent cheekbones mid-face, "
            "elongated from forehead to chin. "
            "SKIN: medium warm brown, slightly yellow-amber undertone, NOT deep copper — "
            "a mid-tone warm brown. Natural skin with visible texture, fine lines at the eye corners, "
            "slight uneven tone, faint dark spots at the jaw. "
            "HAIR: thick medium-brown hair with auburn highlights, wavy texture, "
            "shoulder length, some grey at the roots, worn down and slightly tousled — "
            "not straight, not curly, an S-wave pattern. "
            "EYES: light-medium brown with a hazel-green tint — slightly lighter than average, "
            "almond shaped, calm inward expression, gaze slightly downward then up at the lens. "
            "MOUTH: medium lips, slightly asymmetric, flat neutral line. "
            "BODY: wearing a plain cream-colored cotton blouse with a simple collar, "
            "visible chest and shoulders. "
            "SETTING: indoors in a modest Sacramento apartment living room — "
            "soft diffuse overcast window light from a grey California afternoon. "
            "Background completely blurred — an old fabric couch in muted brown, "
            "a bookshelf out of focus, a plant in the corner. "
            "Photoreal documentary phone portrait, NOT glamour, NOT celebrity — "
            "ordinary hard-lived woman. Visible pores, no makeup, no filter, "
            "no retouching, no beauty mode. 9:16 vertical portrait, photo-realistic."
        ),
    },
    {
        "id": "persona_CWL4_F4",
        "label": "Latina 44 — Nicaraguan/Central American features — outdoor San Diego boardwalk — EXTREME CLOSE-UP",
        "prompt": (
            "Extreme close-up portrait photograph, face filling the 9:16 frame from chin to crown. "
            "44-year-old Nicaraguan-American woman with Central American heritage. "
            "FACE SHAPE: oval face with a strong rounded forehead, defined cheekbones at mid-face, "
            "slightly wide jaw tapering to a rounded chin. Balanced proportions, not narrow, not wide. "
            "SKIN: light warm tan — lighter than most Latinas, with warm peachy-olive undertone, "
            "NOT yellow, NOT cool — slight warmth. Fine lines around the eyes, visible sun freckles "
            "across the nose and upper cheeks from outdoor exposure, slight uneven redness on the nose. "
            "HAIR: shoulder-length loosely curly dark brown hair — 2C-3A loose spirals, "
            "frizzy at the top, some grey hairs visible, worn loose, "
            "wind-slightly-tousled from outdoor setting. Distinct from straight or coily types. "
            "EYES: medium brown, slightly wide, slightly drooping at outer corners giving a "
            "melancholy or tired expression, direct gaze into the lens. "
            "MOUTH: thin-medium lips, slightly pale tone, flat neutral or slight downward line. "
            "SETTING: outdoors at a San Diego coastal boardwalk or promenade — "
            "bright harsh Pacific coastal light, slight marine haze, cool-bright daylight. "
            "Background completely blurred — chain-link fence, a palm tree base, "
            "and the blurred distant ocean horizon out of focus. "
            "Photoreal documentary phone portrait, NOT glamour, NOT celebrity — "
            "ordinary hard-lived woman. Visible pores, no makeup, no filter, "
            "no retouching, no beauty mode. 9:16 vertical portrait, photo-realistic."
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
    print(f"CA Women Latina Personas V4 (mixed framing) — nano-banana-2 → {OUT}\n")
    print("F1: 43, Guatemalan Maya — Fresno backyard citrus (outdoor) — MEDIUM CLOSE-UP")
    print("F2: 45, Dominican/Caribbean — California kitchen (indoor) — EXTREME CLOSE-UP")
    print("F3: 42, Peruvian/Andean — Sacramento apartment living room (indoor) — MEDIUM CLOSE-UP")
    print("F4: 44, Nicaraguan — San Diego coastal boardwalk (outdoor) — EXTREME CLOSE-UP\n")

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
