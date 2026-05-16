"""Generate 6 news-realistic JDC backdrops — ALL with inmates + guards in the prison.

Documentary news b-roll energy. Real-world authenticity. NO press conferences,
NO courtrooms, NO exteriors only — every scene shows inmates (teens in orange)
and guards interacting inside the facility.

Output: outputs/illinois_jdc_urban_peer/news_storyboard/inmate_{N}_{slug}.png
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from openai_image import generate_image

OUT_DIR = Path("outputs/illinois_jdc_urban_peer/news_storyboard")

COMMON = (
    "Photoreal news b-roll, shot like a 20/20 / Frontline / PBS Newshour documentary "
    "segment. Natural color grading, documentary handheld feel with slight grain. "
    "Cold institutional fluorescent lighting. Real-world textures: scuffed cinderblock "
    "walls, polished checkered linoleum floor, painted metal doors. NOT cinematic, "
    "NOT stylized — looks like genuine news investigative footage. "
    "All teenagers in orange jumpsuits are male, mix of Latino and African-American, "
    "ages depicted as older teens (16-17 looking). Faces shown but not in tight close-up — "
    "documentary middle/wide framing keeps identities partially obscured by angle or distance. "
    "NO on-screen text, NO captions, NO chyrons, NO watermarks, NO logos."
)

PROMPTS = {
    "inmate1_line_walk": (
        "News b-roll wide shot looking down a long fluorescent-lit institutional corridor. "
        "Line of 6 teenage boys in orange jumpsuits walking single-file in the center of the "
        "corridor, hands clasped behind their backs. One uniformed adult guard walks at the "
        "front of the line, another uniformed adult guard walks at the back. Cold fluorescent "
        "overhead lights, polished checkered tile, painted cell doors lining both sides. "
        "Camera handheld documentary, slight shake, deep one-point perspective. "
        + COMMON
    ),
    "inmate2_dayroom_watch": (
        "News b-roll medium-wide shot of an institutional dayroom. 4 teenage boys in orange "
        "jumpsuits sit on bolted-down metal stools at a steel table, looking down or at each "
        "other. One uniformed adult guard stands at the doorway with arms crossed, watching. "
        "Plain concrete-block walls painted beige, a single barred window high on the wall "
        "letting in cold daylight, polished tile floor, a wall-mounted phone in the background. "
        "Documentary handheld with slight shake. "
        + COMMON
    ),
    "inmate3_intake_photo": (
        "News b-roll medium shot of a juvenile detention intake booking area. A teenage boy in "
        "an orange jumpsuit stands flat against a white height-chart wall (numbered horizontal "
        "lines), facing forward. A uniformed adult guard stands behind a tripod-mounted "
        "digital camera, mid-photograph. A second guard at a counter to the right holds a "
        "clipboard. Harsh fluorescent overhead lighting, fingerprint scanner on the counter. "
        "Documentary handheld with slight shake, real broadcast-news feel. "
        + COMMON
    ),
    "inmate4_cafeteria_lines": (
        "News b-roll wide shot of an institutional cafeteria. Long rows of bolted-down "
        "stainless-steel tables and benches. About 12 teenage boys in orange jumpsuits seated "
        "at the tables eating from plastic trays. Two uniformed adult guards walk slowly "
        "between the rows, hands behind backs, watching. Overhead industrial fluorescents, "
        "scuffed beige walls, polished tile reflecting the cold light. Wide depth showing the "
        "scale of the room. Documentary handheld. "
        + COMMON
    ),
    "inmate5_yard_outside": (
        "News b-roll wide shot of an institutional outdoor exercise yard. A tall chain-link "
        "fence topped with coiled razor wire surrounds a concrete yard with painted "
        "basketball lines. About 8 teenage boys in orange jumpsuits scattered around — some "
        "sitting on a concrete bench, two leaning on the fence, one walking. A single "
        "uniformed adult guard stands in the corner watching. Overcast grey sky, low concrete "
        "institutional buildings visible behind the fence. Cold daylight, documentary "
        "handheld. "
        + COMMON
    ),
    "inmate6_pat_down": (
        "News b-roll medium shot of a teenage boy in an orange jumpsuit standing with hands "
        "flat against a cinderblock corridor wall, legs spread, while a uniformed adult guard "
        "pats him down with both hands at his waist (procedural search). Second uniformed "
        "guard stands a couple feet back, watching. Cold fluorescent corridor lighting, "
        "polished checkered tile, painted cell doors visible in the background. Documentary "
        "handheld, slight shake. Procedural moment, not violent. "
        + COMMON
    ),
}


def gen(slug, prompt):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"inmate_{slug}.png"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] generating...", flush=True)
    r = generate_image(
        prompt=prompt, out_path=str(out),
        size="1024x1536", quality="medium", n=1,
    )
    if r["status"] != "success":
        return slug, "failed", r["raw"].get("error", "unknown")
    return slug, "success", r["paths"][0]


def main():
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(gen, s, p): s for s, p in PROMPTS.items()}
        for f in as_completed(futures):
            s = futures[f]
            try:
                _, status, info = f.result()
                print(f"[{s}] {status}: {info}", flush=True)
            except Exception as e:
                print(f"[{s}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
