"""Generate 6 news-realistic JDC/prison scene backdrops via gpt-image-2.

These should look like actual news b-roll — documentary realism, real lighting,
authentic environments. NOT cinematic / stylized.

Output: outputs/illinois_jdc_urban_peer/news_storyboard/scene_{N}_{slug}.png
1024x1536 portrait, quality=medium (faster + still photo-real enough).
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from openai_image import generate_image

OUT_DIR = Path("outputs/illinois_jdc_urban_peer/news_storyboard")

COMMON_NEWS_STYLE = (
    "Photoreal news b-roll cinematography. Shot like genuine local-news investigative footage "
    "or a 20/20 / Frontline-style documentary segment. Natural color grading, real-world "
    "lighting (no dramatic Hollywood key-light), slight handheld feel, slight grain. "
    "Documentary realism, not stylized, not glossy. "
    "Looks like it was shot on a news ENG camera or DSLR with broadcast-news look. "
    "NO on-screen text, NO lower-third chyrons, NO news graphics, NO watermarks, NO logos."
)

PROMPTS = {
    "1_press_conference": (
        "Medium shot of a Black adult man in his 30s, wearing a plain grey button-down shirt, "
        "standing at a small wooden podium with two microphones, speaking. Behind him "
        "out-of-focus: 2-3 attorneys in dark suits, plain blue conference-room backdrop with "
        "an American flag partially visible. Daylight diffused through windows on the right. "
        "His expression is solemn, weight of testimony. Vertical 9:16 framing. "
        + COMMON_NEWS_STYLE
    ),
    "2_lawyer_outside_courthouse": (
        "Wide medium shot of a Black male attorney in his 40s wearing a charcoal suit, "
        "standing on the marble steps outside a classical-architecture county courthouse "
        "(columns, limestone, American flag overhead), holding a thick manila case file. "
        "He is mid-sentence speaking to off-camera reporters. Slight wind moves his tie. "
        "Mid-afternoon natural daylight, slight backlight. Other people partially visible "
        "around the steps. Vertical 9:16 framing. "
        + COMMON_NEWS_STYLE
    ),
    "3_reporter_at_facility": (
        "Wide medium shot of a Latina female news reporter in her 30s wearing a professional "
        "navy blazer, holding a microphone with a small black mic-flag, standing outside a "
        "low beige institutional juvenile detention building with chain-link fence and razor "
        "wire behind her. She is mid-report, looking at the camera. Cold overcast daylight. "
        "A small news camera tripod and another crew member partially visible at the edge of "
        "frame. Vertical 9:16 framing. "
        + COMMON_NEWS_STYLE
    ),
    "4_empty_corridor_handheld": (
        "Long handheld push-in down an empty institutional juvenile detention corridor at "
        "mid-day. Painted cinderblock walls in pale beige with scuff marks. Heavy painted "
        "metal cell doors lining both sides, each with small reinforced glass window. Cold "
        "fluorescent overhead lighting flickers softly. Polished checkered linoleum floor "
        "reflects the lights. At the far end of the corridor, one cell door is partially "
        "open. Wide low-angle perspective. Vertical 9:16 framing. "
        + COMMON_NEWS_STYLE
    ),
    "5_survivor_silhouette": (
        "Medium shot of an adult Black man in his 30s sitting on a worn couch in his small "
        "modest apartment, back partially to camera, looking out the window at late-afternoon "
        "light. His face is in profile shadow — identity protected, not identifiable. He "
        "wears a plain grey t-shirt. Out-of-focus background: kitchen counter, family photo "
        "frame on the wall. Warm afternoon light comes through the window. Quiet, "
        "contemplative, emotional weight. Vertical 9:16 framing. "
        + COMMON_NEWS_STYLE
    ),
    "6_courtroom_interior": (
        "Wide shot from the back of a courtroom looking toward the judge's bench. Empty "
        "wooden gallery benches in the foreground, then two attorney tables, then the raised "
        "wooden judge's bench at the far end with an American flag and state flag behind it. "
        "Warm courtroom lighting from overhead fixtures, wooden paneling on the walls, "
        "carpeted floor. The courtroom is empty between sessions. Vertical 9:16 framing. "
        + COMMON_NEWS_STYLE
    ),
}


def gen(slug, prompt):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"scene_{slug}.png"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] generating...", flush=True)
    r = generate_image(
        prompt=prompt,
        out_path=str(out),
        size="1024x1536",
        quality="medium",
        n=1,
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
