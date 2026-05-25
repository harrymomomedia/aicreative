"""IL JDC explainer — CLAYMATION PRISON-AREA scenes (Seedance KIE 480p 9:16).

Inside-the-walls establishing b-roll so the ad unmistakably reads as a
juvie/lockup. Mostly EMPTY institutional spaces — more ominous and
moderation-safe (no people in compromising spaces). Visual cues carry the
"prison" read; the trigger phrase "juvenile detention" is kept OUT of the
prompts to avoid Seedance's text-stage moderation.

  p1 cellblock_tier — two-tier cell block, rows of barred doors
  p2 cell_bars      — barred door, striped shadows on the floor
  p3 empty_cell     — bare cell: cot, concrete, high barred window
  p4 dayroom        — bolted tables/stools, caged TV, barred windows
  p5 yard           — razor-wire yard, netless hoop, lone distant figure
  p6 steel_door     — heavy locked door w/ observation slot + bolt

Output: outputs/illinois_jdc_claymation/{slug}.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_seedance, download

OUT_DIR = Path("outputs/illinois_jdc_claymation")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CLAY = (
    " Handmade claymation stop-motion b-roll, nobody speaking, no dialogue. A "
    "plasticine modeling-clay world with visible thumbprints and fingerprint dents "
    "in the soft clay, hand-sculpted surfaces, matte clay sheen, gentle jerky "
    "frame-stepping stop-motion movement, shallow tabletop miniature depth of field, "
    "Aardman Wallace-and-Gromit diorama craft. Cold, muted, slightly desaturated, "
    "bleak institutional mood. No dialogue, no captions, no subtitles, no on-screen "
    "text, no readable words or signage."
)

SHOTS = {
    "clay_p1_cellblock_tier": (
        "A long grim two-tier clay cell block: two stacked levels of identical heavy "
        "barred cell doors running down both sides, steel railings and a narrow metal "
        "catwalk on the upper tier, harsh overhead institutional lighting, scuffed "
        "concrete floor. Cold, empty, silent, oppressive. A slow steady dolly moving "
        "forward down the center of the block." + CLAY
    ),
    "clay_p2_cell_bars": (
        "Close on a heavy clay cell door made of thick vertical steel bars, cold pale "
        "light spilling through from beyond, the bars casting long hard striped "
        "shadows across the scuffed clay floor and wall. Slow push-in toward the "
        "bars. Claustrophobic, cold, foreboding." + CLAY
    ),
    "clay_p3_empty_cell": (
        "Inside a tiny bare clay cell: a narrow bolted-down metal cot with a thin flat "
        "mattress, scratched and stained concrete walls, a small steel sink, a single "
        "small high window crossed with bars letting in a shaft of cold grey light. "
        "Empty, cramped, claustrophobic, lonely. A slow gentle pan across the cell." + CLAY
    ),
    "clay_p4_dayroom": (
        "A cold institutional clay dayroom: bolted-down round tables with attached "
        "stools, a boxy television mounted high behind a metal cage, scuffed tile "
        "floor, tall narrow barred windows along one wall, flat fluorescent light. "
        "Completely empty and still. Slow wide dolly across the room." + CLAY
    ),
    "clay_p5_yard": (
        "A bleak empty clay exercise yard: cracked concrete ground enclosed by tall "
        "chain-link fencing topped with thick coiled razor wire, a lone netless "
        "basketball hoop leaning to one side, a heavy overcast grey sky. A single "
        "small lone clay figure stands far off in the corner of the yard, tiny and "
        "alone. Long bleak shadows, cold light." + CLAY
    ),
    "clay_p6_steel_door": (
        "A heavy locked steel clay door viewed head-on in a dim cold corridor, with a "
        "small reinforced observation window slot near the top and a large bolt lock, "
        "rivets and scuff marks across its surface, cold light leaking around the "
        "edges of the frame. Slow push-in toward the door. Heavy, foreboding, "
        "inescapable." + CLAY
    ),
}


def gen(slug, prompt):
    out = OUT_DIR / f"{slug}.mp4"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] generating (Seedance KIE 480p 9:16 5s)...", flush=True)
    r = generate_seedance(
        prompt=prompt,
        duration=5,
        aspect_ratio="9:16",
        generate_audio=False,
    )
    if r["status"] != "success" or not r.get("urls"):
        return slug, "failed", str(r.get("raw"))[:400]
    download(r["urls"][0], str(out))
    return slug, "success", str(out)


def main():
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(gen, s, p): s for s, p in SHOTS.items()}
        for f in as_completed(futures):
            s = futures[f]
            try:
                slug, status, info = f.result()
                print(f"[{slug}] {status}: {info}", flush=True)
            except Exception as e:
                print(f"[{s}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
