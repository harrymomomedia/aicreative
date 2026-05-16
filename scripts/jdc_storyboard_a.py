"""Generate a single director's-deck storyboard sheet via gpt-image-2.

Matches the LUMI & MOCHI reference style: two-page spread layout.
LEFT page = character / cast sheet (persona A) with turnarounds, expressions, palette, items, location.
RIGHT page = numbered cuts with timecodes, rough sketches, camera + SFX notes.
Bottom footer: character / location / color references.

Output: outputs/illinois_jdc_urban_peer/storyboard_a.png  (1536x1024 landscape)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from openai_image import generate_image

PROMPT = """Professional director's-deck two-page storyboard spread for a 24-second vertical 9:16 social ad. Wide landscape layout, clean white paper background, magazine production-design aesthetic. EXACTLY like a professional anime/film pre-production document.

═══════ LEFT HALF — CHARACTER / CAST SHEET ═══════

Top-left header in bold black sans-serif: "URBAN PEER"  /  small subheader: "AGE 25 / CHICAGO"
Below header, a short bio block in small clean sans-serif: "Quiet but direct. A young man from the West Side who spent time in Illinois juvenile detention as a teen. Now speaking up — peer to peer."

CHARACTER ART (use the reference image — keep his face / waves / chinstrap / hoodie EXACT match):
- Large FULL-COLOR full-body render of the man on the left side, standing facing slightly to the right, hands relaxed at sides. He wears the same heather-grey pullover hoodie, dark jeans, white sneakers.
- To the right of the full-body: a small TURNAROUND row with three smaller renders labeled "BACK" / "SIDE" / "FRONT".
- A horizontal COLOR PALETTE row of 6 small rounded swatches labeled at the bottom: charcoal grey, heather grey, autumn-leaf brown, brick red, slate blue, off-white.
- An EXPRESSION SHEET — 6 thumbnail close-ups of his FACE arranged in 2 rows × 3 columns, each with a tiny caption underneath: "NEUTRAL", "INTENSE", "POINT AT CAM", "WEARY", "DETERMINED", "DROP IN".
- An "ITEMS & GADGETS" row at the bottom of the left half: 4 small icon-style sketches with labels — SMARTPHONE, GREY HOODIE, SMALL SILVER EARRING, SLIM WALLET.

═══════ RIGHT HALF — STORYBOARD ═══════

Top header in bold black sans-serif: "PROJECT: ILLINOIS JDC AD"  /  subheader in lighter weight: "Persona A / Urban Peer / Hyped CTA — 24 sec"  /  far right corner: "STORYBOARD"

Below the header, FIVE numbered storyboard rows stacked vertically. Each row is a wide horizontal strip with:
- Left column (~15% width): "CUT 1" big bold purple, timecode "0:00 - 0:04.0", duration "(4.0s)", and a short beat name in italic small grey.
- Middle column (~70% width): a wide rough PENCIL-AND-INK SKETCH panel in black-and-white, thin border, depicting the scene.
- Right column (~15% width): CAM angle label (e.g., "LOW ANGLE"), SFX label (e.g., "DIALOGUE"), BGM label (e.g., "HEARTBEAT KICK").

CUT 1 — 0:00 - 0:04.0 (4.0s) — HOOK
  Sketch: a uniformed guard escorting a teen in an orange jumpsuit down a long fluorescent-lit institutional hallway with checkered linoleum floor, doors lining the wall, deep one-point perspective.
  CAM: WIDE LOW / SFX: DIALOGUE / BGM: TENSION KICK

CUT 2 — 0:04.0 - 0:09.0 (5.0s) — CLAIM
  Sketch: exterior wide-angle of a grey concrete institutional building behind a tall chain-link fence topped with coiled razor wire, overcast sky, a single barred window visible.
  CAM: WIDE / SFX: NAT AMBIENCE / BGM: DRONE BUILD

CUT 3 — 0:09.0 - 0:14.0 (5.0s) — SCALE
  Sketch: close-up of a stack of cashier's checks fanned out beside a heavy wooden judge's gavel on a wooden desk, soft side light.
  CAM: ECU TOP-DOWN / SFX: PAPER RUSTLE / BGM: HIT

CUT 4 — 0:14.0 - 0:19.0 (5.0s) — VALIDATION
  Sketch: a survivor sitting with back to camera across a desk from an attorney in shirt and tie, soft daylight through a window on the right, attorney leaning forward listening.
  CAM: OTS / SFX: SOFT ROOM TONE / BGM: HOPE LIFT

CUT 5 — 0:19.0 - 0:24.0 (5.0s) — CTA
  Sketch: POV close-up of a hand holding a smartphone, thumb hovering over a bright green "SUBMIT" button on a qualification web form.
  CAM: POV ECU / SFX: PHONE TAP CLICK / BGM: RESOLVE

═══════ BOTTOM FOOTER — full width of the page ═══════

Three small reference rows side-by-side:
1. "CHARACTER & REFERENCE": 3 small thumbnails of the talent (the man from above) — front / side / 3-quarter.
2. "LOCATION / WORLD": 4 small thumbnails — Chicago brick three-flat, autumn leaves on sidewalk, chain-link fence, institutional hallway.
3. "COLOR & LOOK REFERENCE": 4 small mood-image thumbnails — overcast daylight, warm brick wall texture, autumn-leaf brown, cool slate-blue shadow.

═══════ STYLE NOTES ═══════

- The LEFT character art (full-body + turnaround + expression sheet) is FULL-COLOR PHOTO-REALISTIC, matching the reference image's face / waves / chinstrap / hoodie EXACTLY.
- The RIGHT storyboard panels are ROUGH BLACK-AND-WHITE PENCIL-AND-INK SKETCHES with light pencil shading. They look hand-drawn.
- All text is clean English sans-serif (Helvetica/Inter-style), neat hierarchy.
- White paper background, thin grey grid lines separating sections.
- NO Japanese text. NO logos. NO watermarks. NO extra captions beyond what is specified above.
- This single image should read as a real professional director's pre-production document — like an anime studio's "Project Sheet" for a music video or short film."""


def main():
    out_path = Path("outputs/illinois_jdc_urban_peer/storyboard_a.png")
    ref_path = Path("outputs/illinois_jdc_urban_peer/reference/1.png")

    print(f"reference: {ref_path}")
    print(f"out:       {out_path}")
    print("submitting to gpt-image-2 (image-to-image, 1536x1024 landscape)...")

    result = generate_image(
        prompt=PROMPT,
        out_path=str(out_path),
        image_paths=[str(ref_path)],
        size="1536x1024",
        quality="high",
        n=1,
    )

    if result["status"] != "success":
        print(f"FAILED: {result['raw'].get('error')}")
        return
    print(f"DONE → {result['paths'][0]}")


if __name__ == "__main__":
    main()
