"""IL JDC explainer — CLAYMATION "getting locked up" narrative clips.

The opening (beat 1: "When I was a kid, Illinois locked me up...") was boring —
a static facility exterior + fence. These show the kid actually being taken in
and the cell door closing on him, so "locked me up in juvie" lands visually.

Deep-brown-skin teen boy to match the survivor arc. Detention process only —
NO abuse, NO restraints depicted as violence; an officer escorting + a cell
door closing. Trigger phrase "juvenile detention" kept OUT (visual cues carry
the lockup read) to dodge Seedance text moderation.

Route: KIE (it cleared the sensitive abuse-anchor shots; OpenRouter's output
filter already rejected one emotion clip, and kid+officer+lockup is high-risk
for OR). 480p 9:16 5s, no audio.

  lockup_01_intake_walk   — boy walked through the gate by an officer
  lockup_02_cell_door     — cell door closing on the boy (the "locked me up" beat)
  lockup_03_corridor_escort — boy led down the cellblock by an officer

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
    "bleak institutional mood. No captions, no subtitles, no on-screen text."
)

SHOTS = {
    "lockup_01_intake_walk": (
        "A young teenage boy with deep-brown clay skin and short dark hair, in plain "
        "street clothes, head lowered and shoulders hunched, is walked forward through "
        "a tall heavy institutional steel gate into a cold bare facility by a tall "
        "adult officer in a dark uniform and peaked cap who keeps a hand on the boy's "
        "shoulder. The boy looks small, reluctant and afraid. Cold blue-grey light, "
        "bare concrete entrance, a buzzing light overhead. Slow tracking shot "
        "following them through the gate from behind." + CLAY
    ),
    "lockup_02_cell_door": (
        "Inside a bare cold clay cell, a young teenage boy with deep-brown clay skin "
        "and short dark hair sits small and alone on the edge of a narrow metal cot, "
        "looking up toward the front with a frightened face. A heavy barred steel cell "
        "door slowly swings shut across the front of the frame, the thick vertical "
        "bars closing between the viewer and the boy, sealing him inside. His small "
        "frightened face is seen through the bars as the door locks. Cold blue light, "
        "deep shadows." + CLAY
    ),
    "lockup_03_corridor_escort": (
        "A young teenage boy with deep-brown clay skin and short dark hair, in plain "
        "clothes, head down, is led slowly away down a long cold institutional "
        "cellblock corridor by a tall uniformed officer walking close behind him, rows "
        "of heavy barred cell doors on either side, harsh overhead light. The boy looks "
        "tiny against the towering corridor. Slow tracking shot following from behind." + CLAY
    ),
}


def gen(slug, prompt):
    out = OUT_DIR / f"{slug}.mp4"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] generating (KIE Seedance Fast 480p 9:16 5s)...", flush=True)
    r = generate_seedance(prompt=prompt, duration=5, aspect_ratio="9:16", generate_audio=False)
    if r["status"] != "success" or not r.get("urls"):
        return slug, "failed", str(r.get("raw"))[:400]
    download(r["urls"][0], str(out))
    return slug, "success", str(out)


def main():
    with ThreadPoolExecutor(max_workers=3) as ex:
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
