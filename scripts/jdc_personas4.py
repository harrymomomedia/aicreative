"""
JDC Personas — batch 4, 3 characters
Ages 31-39 | 2 close-up documentary + 1 in-car driver seat
9:16 portrait via useapi.net Google Flow nano-banana-pro
"""
import os, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

USEAPI_TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {USEAPI_TOKEN}", "Content-Type": "application/json"}
OUT = Path("outputs/jdc_personas4")
OUT.mkdir(parents=True, exist_ok=True)

MODEL = "nano-banana-pro"

PERSONAS = [
    # ─── CLOSE-UP 1 ─────────────────────────────────────────────────────────
    {
        "id": "O",
        "label": "male 34 — front porch steps, warm late-afternoon",
        "prompt": (
            "Close-up documentary portrait photograph, NOT a selfie. Camera on a tripod "
            "or held by another person at eye level — natural perspective, no selfie distortion. "
            "Man, 34 years old, medium-brown skin tone, short tapered fade with a slight curl "
            "texture on top (1-2 inches natural), thin groomed mustache connecting to a short "
            "chin strap beard, lean build visible in the jaw and neck. "
            "Tight close-up — face and upper chest fill the frame, chin near bottom, "
            "crown near the top. Head square to the camera. Eyes forward, direct, "
            "deliberate. Heavy gaze. Mouth closed and neutral — ZERO smile.\n\n"
            "BACKGROUND: Exterior of a modest residential front porch — weathered wood "
            "railing or painted brick step edge barely visible, slightly out of focus. "
            "Warm late-afternoon Chicago light coming from one side — golden-hour quality, "
            "soft directional light catching his cheekbone and jaw. Trees or porch overhang "
            "softening the background. Urban residential, lived-in feel.\n\n"
            "WARDROBE: Dark olive-green crewneck t-shirt, plain, no logos. "
            "Just visible at the collar at the base of frame.\n\n"
            "LIGHTING: Warm directional late-afternoon light from the side — "
            "natural golden quality, soft shadow on the opposite side of his face. "
            "No ring light, no flash, no studio fill. Real outdoor ambient.\n\n"
            "REALISM CRITICAL: Natural skin texture on medium-brown skin — visible pores "
            "on the nose and forehead, slight warmth in the late-afternoon light. "
            "Individual mustache and beard follicles visible. Real lip texture. "
            "Subtle facial asymmetry. No beauty filter, no retouching, no smoothing. "
            "Grain from a real camera sensor. Feels like a candid documentary portrait "
            "shot on a Chicago residential street in late afternoon.\n\n"
            "9:16 vertical portrait. No on-screen text, no captions, no watermarks."
        ),
    },
    # ─── CLOSE-UP 2 ─────────────────────────────────────────────────────────
    {
        "id": "P",
        "label": "male 37 — exterior wall, overcast midday",
        "prompt": (
            "Close-up documentary portrait photograph, NOT a selfie. Camera positioned at "
            "eye level by another person or on a tripod — standard lens perspective, "
            "no front-camera wide-angle distortion. "
            "Man, 37 years old, deep dark-brown skin tone, close-cropped natural hair "
            "(very short, even texture, clean fade at the sides), full medium beard "
            "(well-shaped, covering jaw and chin, individual strands visible), "
            "broad jaw, strong brow ridge, heavyset-solid build visible in the neck "
            "and shoulders. "
            "Tight close-up — face dominates the frame from chin to crown. "
            "Facing directly at the camera, chin very slightly lifted. "
            "Eyes open, direct, heavy. Not angry — certain. Mouth flat and closed. ZERO smile.\n\n"
            "BACKGROUND: Exterior wall of a community or public building — smooth painted "
            "concrete or stucco, muted gray-beige, slightly weathered. "
            "Flat overcast Midwest midday light — no harsh shadows, even diffused light. "
            "Just the wall, filling the background completely out of focus. Urban.\n\n"
            "WARDROBE: Dark gray zip-up track jacket, collar at the very bottom of frame. "
            "Plain, no logos.\n\n"
            "LIGHTING: Flat overcast daylight — even, diffused, no directional source. "
            "His deep skin tones are rich under the flat light. "
            "No ring light, no flash, no artificial fill.\n\n"
            "REALISM CRITICAL: Deep-skin texture in flat light — visible pores and natural "
            "skin sheen on the forehead and nose bridge, real beard strand detail, "
            "whites of the eyes with subtle warmth. Under-eye weight. "
            "No beauty filter, no retouching. Real sensor grain. "
            "Looks like a candid journalistic portrait — not a posed headshot.\n\n"
            "9:16 vertical portrait. No on-screen text, no captions, no watermarks."
        ),
    },
    # ─── IN-CAR / DRIVER SEAT ────────────────────────────────────────────────
    {
        "id": "Q",
        "label": "male 32 — driver seat, phone low, windshield light",
        "prompt": (
            "RAW phone photo. Man, 32 years old, warm medium-dark brown skin tone, "
            "low taper fade (very clean lines, sharp edge-up), thin mustache and "
            "light chin beard (4-5 days growth), lean athletic build. "
            "Sitting in the driver seat of a car, facing slightly toward the camera. "
            "Phone is mounted on the dashboard or held low near the steering wheel — "
            "camera angle is low, looking up slightly at his face. "
            "Both hands relaxed — one loosely on the steering wheel, one in his lap. "
            "Head slightly turned toward the phone. Direct, calm gaze into the lens. "
            "Neutral expression — flat mouth. ZERO smile.\n\n"
            "BACKGROUND: Interior of a parked car — driver seat, steering wheel visible "
            "in the lower foreground, dashboard edge visible. "
            "Large windshield in the background letting in soft, even NATURAL DAYLIGHT "
            "from outside — overcast or shade daylight, not direct harsh sun. "
            "Diffused bright light coming through the glass, illuminating his face "
            "from the front-above. "
            "Outside the windshield: soft blur of a residential street or parking lot. "
            "Interior is clean, unremarkable — a real everyday car interior, "
            "no luxury details.\n\n"
            "WARDROBE: Plain white t-shirt or light gray t-shirt. Clean, simple.\n\n"
            "LIGHTING: Natural soft daylight pouring through the windshield — "
            "bright but diffused, no harsh shadows, no ring light, no artificial fill. "
            "The light wraps around his face from the front, the way it does when "
            "someone is sitting in a parked car in the shade on a bright day.\n\n"
            "REALISM CRITICAL: Natural skin texture on warm-medium brown skin — "
            "slight forehead sheen from warmth inside the car, visible pores, "
            "real beard stubble with individual follicles. "
            "Slight wide-angle distortion from phone lens at low angle. "
            "Car interior shadows in the corners of the frame. "
            "Looks exactly like someone recording a voice note or video in their parked car. "
            "No beauty filter, no ring light, no post-processing.\n\n"
            "9:16 vertical portrait. No on-screen text, no captions, no watermarks."
        ),
    },
]


def generate_persona(p):
    pid = p["id"]
    out_dir = OUT / f"persona_{pid}"
    out_dir.mkdir(exist_ok=True)

    payload = {"prompt": p["prompt"], "model": MODEL, "aspectRatio": "9:16"}
    print(f"  Persona {pid} ({p['label']}): submitting …", flush=True)

    r = requests.post(
        "https://api.useapi.net/v1/google-flow/images",
        headers=HEADERS, json=payload, timeout=120,
    )
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Persona {pid}: HTTP {r.status_code} — {r.text[:300]}")

    data = r.json()
    media_list = data.get("media", [])
    if not media_list:
        raise RuntimeError(f"Persona {pid}: no media in response — {data}")

    saved = []
    for i, m in enumerate(media_list):
        fife_url = m.get("image", {}).get("generatedImage", {}).get("fifeUrl", "")
        media_id = m.get("image", {}).get("generatedImage", {}).get("mediaGenerationId", "")
        if not fife_url:
            continue
        out_path = out_dir / f"v{i+1}.jpg"
        r2 = requests.get(fife_url, timeout=60)
        r2.raise_for_status()
        with open(out_path, "wb") as f:
            f.write(r2.content)
        if media_id:
            (out_dir / f"v{i+1}_mediaId.txt").write_text(media_id)
        saved.append((out_path, media_id))
        print(f"    Persona {pid} v{i+1}: {out_path.stat().st_size//1024}KB saved")

    print(f"  ✓ Persona {pid}: {len(saved)} image(s) → {out_dir}")
    return pid, saved


if __name__ == "__main__":
    print(f"Generating {len(PERSONAS)} JDC personas (batch 4) → {OUT}\n")
    print("Ages 31-39 | 2 closeup documentary + 1 in-car driver seat\n")

    results = {}
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(generate_persona, p): p["id"] for p in PERSONAS}
        for fut in as_completed(futs):
            pid = futs[fut]
            try:
                pid, saved = fut.result()
                results[pid] = saved
                print(f"✓ Persona {pid} complete")
            except Exception as e:
                print(f"✗ Persona {pid} ERROR: {e}")

    print(f"\n{'='*50}")
    print(f"Completed: {len(results)}/{len(PERSONAS)} personas")
    for pid in sorted(results):
        for path, mid in results[pid]:
            print(f"  {pid} → {path}")
