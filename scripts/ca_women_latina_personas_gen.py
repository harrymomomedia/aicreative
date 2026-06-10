"""
CA Women's Prison — 4 Latina Survivor Personas (ages 42–50)
2 outdoor + 2 indoor | unique California working-class settings
useapi.net nano-banana-2 | 9:16 | realism tail baked in
"""
import os, requests, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
OUT = Path("outputs/ca_women_latina_personas")
OUT.mkdir(parents=True, exist_ok=True)

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
        "id": "persona_CWL_F1",
        "label": "Latina — 45 — Outside, East LA apartment complex courtyard — late afternoon",
        "prompt": (
            "Portrait photograph of a 45-year-old Latina woman, medium close-up framing from "
            "mid-torso to top of head, standing in the open courtyard of a low-income East Los "
            "Angeles apartment complex. Medium-tan olive skin with visible pores, slight acne "
            "scarring on the jaw, faint sun damage across the nose and cheeks, fine lines around "
            "the eyes and mouth. Dark hair with grown-out highlights and visible grey at the roots, "
            "pulled back loosely in a messy bun with stray strands framing her face. Direct tired "
            "gaze into the camera lens, lips pressed together in a flat neutral line, carrying quiet "
            "weight. A small plain gold cross on a thin chain. Wearing a plain dark-purple v-neck "
            "t-shirt and dark jeans. Warm low late-afternoon Los Angeles sunlight, long soft shadows, "
            "slight golden haze. Background slightly out of focus — faded stucco walls painted beige "
            "and terracotta, a metal railing, a rusted mailbox cluster, potted plants on a concrete "
            "ledge, a clothesline with laundry, ordinary dense urban courtyard. " + REAL
        ),
    },
    {
        "id": "persona_CWL_F2",
        "label": "Latina — 42 — Outside, Central Valley roadside farm stand — midday",
        "prompt": (
            "Portrait photograph of a 42-year-old Latina woman, medium close-up framing from "
            "chest to top of head, standing at the edge of a roadside farm stand in the Central "
            "Valley of California. Sun-baked olive-tan skin, pronounced crow's feet, deep forehead "
            "lines from squinting, lip creases, visible capillaries across the cheeks from years "
            "in direct sun. Dark brown hair with significant grey roots, worn straight and flat "
            "against the head, pulled back tightly with a rubber band. Steady serious gaze directly "
            "into the lens, no expression, jaw set, quiet exhaustion in the eyes. Wearing a faded "
            "plaid flannel shirt over a plain white tank top. Flat harsh Central Valley midday sun, "
            "bright even light with slight bleaching, no dramatic shadows. Background slightly out "
            "of focus — a hand-lettered produce sign, wooden crates of oranges and stone fruit, a "
            "corrugated metal awning edge, brown dry fields stretching behind, a two-lane highway "
            "shoulder. " + REAL
        ),
    },
    {
        "id": "persona_CWL_F3",
        "label": "Latina — 48 — Inside, small neighborhood beauty salon hair station — window light",
        "prompt": (
            "Portrait photograph of a 48-year-old Latina woman, close-up framing from shoulders "
            "to top of head, seated in or standing beside a styling chair in a small neighborhood "
            "beauty salon in a working-class California city. Medium-deep tan skin with visible "
            "pores, forehead lines, under-eye puffiness, faint blemishes, no makeup. Dark hair "
            "with significant silver-grey streaks throughout, chin-length and slightly wavy, "
            "air-dried and un-styled. Steady direct gaze into the lens, mouth closed and flat, "
            "a heaviness behind the eyes. Wearing a plain black smock over a simple shirt. "
            "Soft diffused natural daylight from a street-facing salon window, warm-neutral indoor "
            "tone. Background slightly out of focus — a large mirror with photos tucked into the "
            "frame, a countertop with combs and product bottles, a wall-mounted dryer, product "
            "posters in Spanish and English, a cluttered lived-in salon interior. " + REAL
        ),
    },
    {
        "id": "persona_CWL_F4",
        "label": "Latina — 50 — Inside, modest home sewing room / spare bedroom — lamp light",
        "prompt": (
            "Portrait photograph of a 50-year-old Latina woman, close-up framing from shoulders "
            "to top of head, seated in a small sewing room or repurposed spare bedroom in a modest "
            "California home. Olive skin, deeply lined forehead and cheeks, pronounced nasolabial "
            "folds, under-eye darkness and slight bags, no makeup. Greying dark hair worn in a "
            "simple low braid over one shoulder, showing significant silver at the temples and "
            "parting. Calm steady gaze directly into the camera lens, lips closed in a neutral "
            "line, a quiet resigned steadiness. Wearing a plain dark-burgundy long-sleeve shirt. "
            "Warm low lamp light from a side table lamp, soft orange-yellow cast, gentle shadows. "
            "Background slightly out of focus — a sewing machine on a folding table, a shelf with "
            "fabric bolts and thread spools, a small framed prayer or religious image on the wall, "
            "a rosary hanging from a pushpin, stacked plastic bins, a plain white wall — personal "
            "and modest. " + REAL
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
    print(f"CA Women Latina Personas — 4 women ages 42–50 (nano-banana-2) → {OUT}\n")
    print("F1: Latina 45, East LA apartment courtyard (outdoor)")
    print("F2: Latina 42, Central Valley farm stand roadside (outdoor)")
    print("F3: Latina 48, neighborhood beauty salon (indoor)")
    print("F4: Latina 50, home sewing room / spare bedroom (indoor)\n")

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
