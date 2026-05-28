"""
IL JDC Variation 5 — Persona Set B
5 new personas, 1 image each, no phone in hands.
Mix of close-up and medium shots, varied styles.
Uses useapi.net Google Flow nano-banana-pro.
"""
import os, requests
from pathlib import Path

USEAPI_TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {USEAPI_TOKEN}", "Content-Type": "application/json"}
OUT = Path("outputs/il_jdc_v5_personas_b")
OUT.mkdir(exist_ok=True)

MODEL = "nano-banana-pro"

PERSONAS = [
    {
        "id": "F",
        "setting": "front_stoop_closeup",
        "prompt": """CLOSE-UP portrait photo. Man, medium dark-brown complexion, early 30s (34 years old), lean build, short natural low-cut fade, thin beard, sharp features. Sitting on the concrete front steps of a brownstone — framing is tight from mid-chest up, worn stone steps partially visible at shoulders. Overcast flat daylight, soft shadows. Dark olive crewneck. Arms resting loosely on his knees just below frame. Looking directly into the camera with a quiet, guarded expression — not angry, not performing. The stillness of someone deciding whether to speak. Face fills most of the frame. Natural skin: visible pores, slight discoloration under the eyes, dry lips, faint asymmetry, no beauty filter, no retouching. Looks like a real tight front-camera selfie, phone at arm's length, slightly below eye level. 9:16 vertical portrait.""",
    },
    {
        "id": "G",
        "setting": "brick_wall_arms_crossed",
        "prompt": """Medium portrait photo. Man, deep dark-brown complexion, late 30s (37 years old), stocky-muscular build, shaved head, full short beard with grey flecks, strong jaw. Standing with his back against a worn red brick wall — brick texture sharp behind him, slightly blurred at the edges. Flat overcast afternoon light. Black zip-up hoodie over a dark tee, dark jeans. Arms crossed at his chest, weight shifted slightly to one side. Head tilted down just a fraction, eyes steady and direct into the lens — the posture of a man who has made a decision and is standing in it. Natural authentic face: deep skin texture, visible lines between the brows, slight shine on the forehead, natural beard. No studio, no filter. Looks like someone stepped outside and took this themselves. 9:16 vertical portrait.""",
    },
    {
        "id": "H",
        "setting": "storefront_hands_in_pockets",
        "prompt": """Medium-wide portrait photo. Man, warm brown complexion with golden undertones, early 30s (32 years old), slim build, medium-length locs pulled back loosely, light goatee, relaxed posture. Standing outside a closed neighborhood storefront — faded awning edge and painted brick wall slightly out of focus behind him, overcast afternoon light. Rust-orange puffer vest over a dark long-sleeve, dark pants. Both hands tucked into pants pockets, weight on one foot — natural at-ease posture. Looking directly into the lens, expression calm and open but carrying something — the soft-eyed look of someone who has been thinking about something for a long time. Natural: visible skin texture, pores on nose bridge, natural lip color, light stubble texture. Real UGC front-camera portrait. 9:16 vertical.""",
    },
    {
        "id": "I",
        "setting": "industrial_wall_closeup",
        "prompt": """Tight portrait photo. Man, rich dark-brown complexion, 40 years old, medium build, very close-cropped natural hair nearly shaved, full short beard, strong jaw, weathered face. Framing from mid-chest up — face fills most of the frame, grey painted concrete wall softly blurred behind him. Diffused flat overcast light, no harsh shadows, slight natural skin texture visible. Dark crewneck just visible at the bottom of frame. Arms at sides, not in frame. Direct gaze into the lens, expression still and grounded — the quiet authority of a man who has lived through something and come out standing. Authentic skin: prominent pores, visible lines at the eye corners, slight unevenness on the cheeks, natural grey flecks in the beard, no filter, no retouching, no beauty mode. Looks like a real phone portrait shot close. 9:16 vertical.""",
    },
    {
        "id": "J",
        "setting": "residential_sidewalk_3quarter",
        "prompt": """Medium portrait photo. Man, deep warm-brown complexion, mid-30s (36 years old), medium-athletic build, short natural coils with a taper fade, no beard — clean-shaven, angular jawline. Standing on a quiet residential sidewalk — modest houses and a parked car softly blurred in the background, muted grey afternoon sky. Heather-brown thermal long-sleeve, dark work pants. Turned slightly three-quarters toward camera, one hand in his front pocket, other arm relaxed at his side. Looking into the lens with a steady, unsmiling expression — not confrontational, just measured. The look of someone choosing their words. Natural face: visible pores, slight discoloration around the mouth, natural brow texture, clean shave with visible follicle texture. Phone-camera quality. No studio, no filter. 9:16 vertical portrait.""",
    },
]


def generate_persona(p):
    out_path = OUT / f"persona_{p['id']}_{p['setting']}.jpg"
    if out_path.exists() and out_path.stat().st_size > 50_000:
        print(f"  Persona {p['id']}: already exists, skipping")
        return p["id"], str(out_path)

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

    # Take only the first result — 1 image per persona
    m = media_list[0]
    fife_url = m.get("image", {}).get("generatedImage", {}).get("fifeUrl", "")
    media_id = m.get("image", {}).get("generatedImage", {}).get("mediaGenerationId", "")
    if not fife_url:
        raise RuntimeError(f"Persona {p['id']}: no fifeUrl in first result")

    r2 = requests.get(fife_url, timeout=60)
    r2.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r2.content)
    mid_path = OUT / f"persona_{p['id']}_{p['setting']}_mediaId.txt"
    mid_path.write_text(media_id)
    size = out_path.stat().st_size
    print(f"  Persona {p['id']}: saved → {out_path.name} ({size//1024}KB)")
    return p["id"], str(out_path)


if __name__ == "__main__":
    print(f"Generating {len(PERSONAS)} personas → {OUT}")
    print(f"Model: {MODEL} | 1 image per persona | no phone in hands\n")

    results = {}
    for p in PERSONAS:
        try:
            pid, path = generate_persona(p)
            results[pid] = path
        except Exception as e:
            print(f"✗ Persona {p['id']} ERROR: {e}")

    print(f"\nCompleted: {len(results)}/{len(PERSONAS)}")
    for pid in sorted(results):
        print(f"  Persona {pid}: {results[pid]}")
