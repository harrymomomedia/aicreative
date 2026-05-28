"""
IL JDC Variation 5 — "Part Nobody Tells You" hook
Generate 5 Black male personas (outdoor, 9:16) aged 31–40.
Uses useapi.net Google Flow nano-banana-pro for high-quality portrait images.

Character: 31–40-year-old man, outside settings, UGC selfie style,
serious/grounded expression — someone who has been through something
and come out the other side.

5 persona variations:
  A: Urban bus stop / corner, 31yo, dark complexion
  B: Apartment complex exterior / parking lot, 35yo, medium-dark complexion
  C: Neighborhood park path, 38yo, deep brown complexion
  D: Side street / alley wall, 33yo, rich dark complexion
  E: Community center / rec center exterior, 40yo, warm brown complexion
"""
import os, sys, time, requests
from pathlib import Path

USEAPI_TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {USEAPI_TOKEN}", "Content-Type": "application/json"}
OUT = Path("outputs/il_jdc_v5_personas")
OUT.mkdir(exist_ok=True)

MODEL = "nano-banana-pro"

PERSONAS = [
    {
        "id": "A",
        "setting": "urban_bus_stop",
        "prompt": """Portrait photo. Man, deep dark-brown complexion, early 30s (31 years old), lean athletic build, very short natural fade cut, no beard. Standing outside at an urban bus stop — concrete shelter partially in frame, city street slightly out of focus behind him, overcast flat daylight. Dark navy hoodie unzipped over a plain white tee, dark jeans. Holding phone at chest height, selfie angle tilted slightly upward. Direct, unguarded gaze straight into the camera — heavy-eyed, watchful, the expression of someone who knows things and carries them quietly. Not angry. Just present and serious. Natural authentic face: visible pores on nose and cheeks, slight under-eye shadow, fine lines at the eye corners, faint asymmetry, dry lip texture. No beauty mode, no filter, no retouching, no studio lighting. Real UGC phone selfie energy. 9:16 vertical portrait.""",
    },
    {
        "id": "B",
        "setting": "apartment_complex_exterior",
        "prompt": """Portrait photo. Man, medium dark-brown complexion, mid-30s (35 years old), medium-stocky build, short natural twist-out hair with a taper fade, thin mustache and chin strap beard, well-maintained. Standing outside in front of a mid-rise apartment building exterior — pale brick facade and metal railing slightly out of focus behind him, overcast afternoon light, no harsh shadows. Olive-green Carhartt-style jacket over a dark crewneck, dark work pants. Phone held at chest level in selfie mode, camera tilted slightly upward. Eyes on the lens — steady, thoughtful, a measured look like he is choosing his words carefully. Authentic face: natural skin texture and pores, some unevenness around the jaw, natural brow shape, subtle eye bags. No studio, no ring light, no beauty filter. Genuine UGC self-portrait aesthetic. 9:16 vertical.""",
    },
    {
        "id": "C",
        "setting": "neighborhood_park",
        "prompt": """Portrait photo. Man, deep warm-brown complexion, late 30s (38 years old), medium build, low natural cut with a clean fade, small neat full beard with natural grey flecks at the chin, giving him authority. Standing on a park footpath — green grass and blurred park trees behind him, late afternoon overcast light, golden-grey sky. Dark grey zip-up fleece pullover, dark jogger pants. Phone held straight at stomach level tilted slightly upward, natural UGC selfie angle. Gaze direct into the lens — calm and grounded, the expression of a man who has made peace with hard things. No smile, no performance. Authentic: visible pores on cheeks and forehead, slight weathering at the eye corners, natural beard texture with grey, no retouching. Looks like a real front-camera self-portrait taken during a walk. 9:16 vertical portrait.""",
    },
    {
        "id": "D",
        "setting": "side_street_wall",
        "prompt": """Portrait photo. Man, rich dark-brown complexion, early-to-mid 30s (33 years old), lean muscular build, clean-shaved head, full short beard, sharp jawline. Standing against a painted concrete wall on a quiet side street — worn wall texture slightly out of focus, overcast diffused daylight, no dramatic shadows. Black crewneck sweatshirt, dark jeans. Phone held in one hand at mid-chest height, slightly angled upward — the natural selfie posture of a tall person. Eyes locked directly into the camera, expression resolute and still — carrying something heavy but not broken by it. Authentic skin: visible pore detail on nose and forehead, slight uneven skin tone, natural beard line, no filter, no beauty mode. Looks like a raw self-portrait shot on the street. 9:16 vertical portrait.""",
    },
    {
        "id": "E",
        "setting": "rec_center_exterior",
        "prompt": """Portrait photo. Man, warm medium-brown complexion, 40 years old, medium-heavyset build, very short natural hair almost shaved, full short beard, clean and well-groomed. Standing outside on the concrete steps of a community or recreation center — aged institutional brick building entrance slightly out of focus behind him, flat overcast light, muted afternoon sky. Heather-grey pullover hoodie, dark pants, simple clean look. Phone held at chest level tilted slightly upward. Looking directly into the lens with a calm, open, resolute expression — the look of someone who has something true to say and isn't in a rush to say it. Authentic: natural skin texture, visible pores around the nose and cheeks, slight under-eye lines, natural lip color, no beauty smoothing. Looks exactly like a real phone selfie taken before walking in somewhere. 9:16 vertical portrait.""",
    },
]


def generate_persona(p):
    first_path = OUT / f"persona_{p['id']}_{p['setting']}_v1.jpg"
    if first_path.exists():
        print(f"  Persona {p['id']}: already exists, skipping")
        return p["id"], [str(first_path)]

    payload = {
        "prompt": p["prompt"],
        "model": MODEL,
        "aspectRatio": "9:16",
    }
    print(f"  Persona {p['id']} ({p['setting']}): submitting …", flush=True)
    r = requests.post(
        "https://api.useapi.net/v1/google-flow/images",
        headers=HEADERS,
        json=payload,
        timeout=120,
    )
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Persona {p['id']} failed: {r.status_code} {r.text[:300]}")

    data = r.json()
    media_list = data.get("media", [])
    if not media_list:
        raise RuntimeError(f"Persona {p['id']}: no media in response: {list(data.keys())}")

    saved_paths = []
    for i, m in enumerate(media_list, start=1):
        fife_url = m.get("image", {}).get("generatedImage", {}).get("fifeUrl", "")
        media_id = m.get("image", {}).get("generatedImage", {}).get("mediaGenerationId", "")
        if not fife_url:
            print(f"    Persona {p['id']} v{i}: no fifeUrl, skipping")
            continue
        out_path = OUT / f"persona_{p['id']}_{p['setting']}_v{i}.jpg"
        r2 = requests.get(fife_url, timeout=60)
        r2.raise_for_status()
        with open(out_path, "wb") as f:
            f.write(r2.content)
        size = out_path.stat().st_size
        mid_path = OUT / f"persona_{p['id']}_{p['setting']}_v{i}_mediaId.txt"
        mid_path.write_text(media_id)
        print(f"  Persona {p['id']} v{i}: saved → {out_path.name} ({size//1024}KB)")
        saved_paths.append(str(out_path))

    return p["id"], saved_paths


if __name__ == "__main__":
    print(f"Generating 5 personas → {OUT}")
    print(f"Model: {MODEL} | AspectRatio: 9:16 portrait\n")

    results = {}
    for p in PERSONAS:
        try:
            pid, paths = generate_persona(p)
            results[pid] = paths
        except Exception as e:
            print(f"✗ Persona {p['id']} ERROR: {e}")

    print(f"\nCompleted: {len(results)}/5")
    for pid in sorted(results):
        for path in results[pid]:
            print(f"  Persona {pid}: {path}")
