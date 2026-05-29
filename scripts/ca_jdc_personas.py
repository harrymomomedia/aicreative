"""
CA JDC Personas — 6 UGC characters
3 Black/African American + 3 Hispanic/Latino
9:16 portrait via useapi.net Google Flow nano-banana-pro
Unique backgrounds: basketball court, front porch, painted wall,
                    residential backyard, urban park, neighborhood sidewalk
"""
import os, requests, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

USEAPI_TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {USEAPI_TOKEN}", "Content-Type": "application/json"}
OUT = Path("outputs/ca_jdc_personas")
OUT.mkdir(parents=True, exist_ok=True)

MODEL = "nano-banana-pro"

PERSONAS = [
    # ─── BLACK / AFRICAN AMERICAN ───────────────────────────────────────────
    {
        "id": "A",
        "label": "Black male 33 — basketball court",
        "prompt": (
            "RAW phone selfie photo. Man, 33 years old, medium-dark brown complexion, "
            "short natural low-fade haircut, thin beard trimmed close to the jaw. "
            "Arms crossed firmly at chest. Facing directly into the front camera, "
            "head-and-shoulders framing, no tilt. "
            "Heavy, serious gaze directly into the lens — the look of someone who has seen things. "
            "Zero smile, flat neutral mouth.\n\n"
            "BACKGROUND: outdoor public basketball court. Faded gray asphalt surface, "
            "painted court markings worn and cracked. Chain-link fence behind him, "
            "slightly out of focus. Late afternoon golden light from the left side. "
            "Clear sky, warm colors in the distance.\n\n"
            "WARDROBE: plain white crew-neck t-shirt, dark gray joggers. "
            "No jewelry, no chains.\n\n"
            "REALISM CRITICAL — must look like a real person's phone photo: "
            "Visible pores on nose and cheeks. Natural under-eye shadow. "
            "Slight uneven skin tone. Natural lip texture, slightly dry. "
            "Subtle facial asymmetry. Slight image grain from phone sensor. "
            "Mild front-camera wide-angle distortion. NOT studio-lit, NOT retouched, "
            "NOT beauty-filtered. Looks like he took this himself standing courtside.\n\n"
            "9:16 vertical portrait. No on-screen text, no captions, no watermarks."
        ),
    },
    {
        "id": "B",
        "label": "Black male 41 — front porch stoop",
        "prompt": (
            "RAW phone selfie photo. Man, 41 years old, deep dark-brown complexion, "
            "close-cropped hair with a clean taper, full short beard with visible gray "
            "hairs woven in at the chin and sides. "
            "Seated on the front steps of a weathered urban porch, leaning forward, "
            "elbows resting on knees, hands loosely clasped. "
            "Looking directly into the camera — calm, heavy, unhurried. "
            "No smile. The look of a man who has been through it and came out quieter.\n\n"
            "BACKGROUND: front porch of an older urban row house. "
            "Weathered concrete steps, peeling paint on a metal railing beside him, "
            "faded wooden door slightly visible behind. Dusk light — warm orange tones "
            "from the left, soft shadow on the right side of his face.\n\n"
            "WARDROBE: dark flannel shirt open over a white crew-neck undershirt, "
            "dark jeans. Nothing flashy.\n\n"
            "REALISM CRITICAL: Deep visible skin texture — pores enlarged on nose and forehead, "
            "natural sheen on cheeks. Beard showing individual strands, slight gray glint. "
            "Bags under the eyes, fine weathering lines at eye corners. "
            "Real lip texture, slight dryness. Slight facial asymmetry. "
            "Front-camera mild distortion. Grain from phone in low evening light. "
            "No beauty filter, no studio lighting, no ring light reflection.\n\n"
            "9:16 vertical portrait. No on-screen text, no captions, no watermarks."
        ),
    },
    {
        "id": "C",
        "label": "Black male 27 — painted exterior wall",
        "prompt": (
            "RAW phone selfie photo. Man, 27 years old, warm medium-brown complexion, "
            "low skin-fade haircut (very short on sides, slightly longer on top), "
            "light stubble on the jaw and upper lip — 3-5 days growth, patchy and natural. "
            "Standing with one shoulder leaning back against a painted concrete block wall. "
            "Arms loosely crossed at the waist. "
            "Direct gaze into the camera — controlled, quiet, holding something back. "
            "Flat mouth, no smile. Young but serious.\n\n"
            "BACKGROUND: exterior painted concrete block wall — muted olive-gray color, "
            "paint slightly scuffed and worn in patches. Side of an institutional or "
            "municipal building (school, rec center). Flat overcast daylight. "
            "Edge of a cracked asphalt parking lot barely visible at the bottom of frame.\n\n"
            "WARDROBE: black zip-up hoodie, hood down, slightly open at collar, "
            "plain dark jeans. Simple, clean.\n\n"
            "REALISM CRITICAL: Natural skin — visible pores, slight acne marks on cheek, "
            "uneven skin tone across forehead. Stubble showing individual hair follicles. "
            "No beauty filter, no retouching, no skin smoothing. "
            "Slight image noise from phone camera. Mild wide-angle front-cam distortion. "
            "Looks like he held the phone himself, standing against the wall.\n\n"
            "9:16 vertical portrait. No on-screen text, no captions, no watermarks."
        ),
    },
    # ─── HISPANIC / LATINO ──────────────────────────────────────────────────
    {
        "id": "D",
        "label": "Hispanic male 35 — residential backyard",
        "prompt": (
            "RAW phone selfie photo. Man, 35 years old, medium-brown warm skin tone, "
            "dark wavy hair (slightly grown out, natural), trimmed medium beard, "
            "dark eyes. Stocky, broad-shouldered build. "
            "Standing upright, arms loosely crossed or resting at sides. "
            "Looking directly into the camera, serious and steady. No smile. "
            "The look of a working man who chooses his words carefully.\n\n"
            "BACKGROUND: residential backyard. Weathered wood privacy fence behind him — "
            "gray-brown planks, slightly warped and sun-bleached. "
            "Sparse dry grass and hard dirt at the edges. One corner of a concrete block "
            "retaining wall visible at the left edge. Late afternoon California sunlight, "
            "warm and slightly harsh, casting soft shadows.\n\n"
            "WARDROBE: gray chambray work shirt with sleeves rolled up to the elbows, "
            "dark wash jeans, plain leather belt. Practical, no logo, no flash.\n\n"
            "REALISM CRITICAL: Natural skin showing sun weathering — slight tan line at "
            "the forearm, visible pores on nose and cheeks, real beard texture with "
            "individual hairs. Fine lines at the eyes. Slightly calloused hands faintly "
            "visible. No beauty filter, no retouching, no studio light. "
            "Phone camera grain. Mild wide-angle distortion. Authentic backyard selfie feel.\n\n"
            "9:16 vertical portrait. No on-screen text, no captions, no watermarks."
        ),
    },
    {
        "id": "E",
        "label": "Hispanic male 38 — urban park",
        "prompt": (
            "RAW phone selfie photo. Man, 38 years old, olive-tan skin tone, "
            "dark straight hair (short, slightly pushed back), dark mustache and "
            "short kept beard with slight silver strands. Medium build, lean face. "
            "Standing near a concrete park bench, one hand resting on the back of it. "
            "Direct gaze into the camera. Thoughtful, measured expression. "
            "No smile — the weight of knowing something important and choosing whether to share it.\n\n"
            "BACKGROUND: urban neighborhood park. Concrete path behind him, a weathered "
            "park bench. Trees in the middle distance — green leaves, dappled light. "
            "Low chain-link fence or hedge at the edge. Overcast afternoon light, "
            "soft and even. No dramatic shadows.\n\n"
            "WARDROBE: plain navy polo shirt (no logo), dark khaki pants. "
            "Simple, clean, slightly worn.\n\n"
            "REALISM CRITICAL: Visible skin texture — pores, slight unevenness, "
            "natural warm olive undertone. Beard showing real hair detail, slight gray glint. "
            "Fine lines around eyes and mouth corners. Natural eye whites, not retouched. "
            "No beauty filter, no ring light, no studio glow. "
            "Phone-camera noise and slight wide-angle distortion. Looks like a real guy "
            "at the park took a selfie.\n\n"
            "9:16 vertical portrait. No on-screen text, no captions, no watermarks."
        ),
    },
    {
        "id": "F",
        "label": "Hispanic male 29 — residential sidewalk",
        "prompt": (
            "RAW phone selfie photo. Man, 29 years old, medium warm-tan skin tone, "
            "short dark curly hair (tight, natural curl pattern), clean-shaven, "
            "dark eyebrows, sharp jawline. Slender to medium build. "
            "Standing upright on a residential sidewalk, arms relaxed at sides. "
            "Looking directly into the camera — serious, composed, not performing. "
            "Flat neutral mouth, no smile. Quiet urgency behind the eyes.\n\n"
            "BACKGROUND: residential sidewalk in a modest California neighborhood. "
            "Row of older single-family homes behind him — stucco exterior, small lawns, "
            "a parked older car at the curb. Concrete sidewalk. Slightly overcast midday "
            "light — bright but no harsh shadows. Neighborhood feels real and lived-in.\n\n"
            "WARDROBE: plain heather-gray crew-neck t-shirt, dark jeans. "
            "Nothing branded, nothing flashy.\n\n"
            "REALISM CRITICAL: Natural skin texture — pores on the nose, slight variation "
            "in tone. Curly hair showing real strand detail, not smoothed. "
            "Real eyebrow texture. Slight sweat sheen in midday warmth. "
            "No beauty filter, no retouching, no studio lighting. "
            "Phone front-camera grain and mild wide-angle distortion. "
            "Looks like a real selfie taken on the sidewalk in front of his neighborhood.\n\n"
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

    print(f"  ✓ Persona {pid}: {len(saved)} image(s) saved → {out_dir}")
    return pid, saved


if __name__ == "__main__":
    print(f"Generating {len(PERSONAS)} CA JDC personas → {OUT}\n")
    print("3 Black/African American + 3 Hispanic/Latino\n")

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
