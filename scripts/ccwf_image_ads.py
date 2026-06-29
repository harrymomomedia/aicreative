"""FB IMAGE ads for the CA women's-prison (Chowchilla/CCWF/CIW) campaign — 10 distinct concepts.
NO text in the image (primary + headline carry the story). Direct, literal visuals that instantly
read "women's prison survivor / claim" — no metaphor. img01 is the testimonial-post pairing for the
winner script (candid selfie persona = the 'author' of the testimonial primary).
gpt-image-2 via KIE, 2K, 3:4 (crops clean to FB 4:5).

  python scripts/ccwf_image_ads.py
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, download as kie_download

REAL = (
    " Photoreal candid documentary photo, ordinary everyday working-class realism, natural light, "
    "real skin with visible pores, fine lines, uneven tone, no makeup, no beauty retouching, no "
    "filter, no glamour. NOT a stock photo look, NOT cinematic, NOT stylized. Looks like a real "
    "photo from a phone or a news photographer. NO on-screen text, NO captions, NO watermarks, "
    "NO readable signage or documents (any paper or signs are blurred/illegible)."
)

CONCEPTS = [
    ("img01_testimonial_selfie",
     "A weathered Latina woman in her mid 40s, dark hair pulled back with grey streaks, thin drawn "
     "eyebrows, small gold hoops, a faded tattoo on her neck, wearing a plain black tank top, taking "
     "a candid arm's-length phone selfie at her kitchen table in the evening, looking straight into "
     "the lens with a serious, composed expression. Looks exactly like the profile photo on a real "
     "Facebook testimonial post."),
    ("img02_release_gate",
     "A Latina woman in her 40s in plain street clothes standing just outside a tall prison gate "
     "with razor-wire fencing behind her, holding a clear plastic bag of belongings, flat morning "
     "light, looking off past the camera. Reads instantly as the day she was released."),
    ("img03_facility_exterior",
     "News-photographer shot of a California women's state prison exterior at midday: long beige "
     "concrete buildings, tall chain-link fence topped with coils of razor wire, a guard tower, dry "
     "Central Valley flat land and haze in the background. No people. Shot like AP news b-roll."),
    ("img04_bunk",
     "A Latina woman in her 30s wearing a plain beige institutional uniform sitting alone on the "
     "edge of a lower bunk in a small concrete cell, elbows on knees, looking down at the floor, "
     "harsh fluorescent light. Documentary realism, somber, nothing graphic."),
    ("img05_lawyer_consult",
     "Over-the-shoulder shot across a modest law-office desk: a weathered Latina woman in her 40s "
     "in a plain hoodie speaking seriously to a middle-aged attorney in a suit jacket, manila "
     "folders and a yellow legal pad on the desk (all paper blurred/illegible), warm office light. "
     "Reads as her filing her claim."),
    ("img06_survivors_group",
     "Five women of different ages 30s-60s, mixed Latina and white, weathered everyday faces, plain "
     "clothes, standing together shoulder to shoulder on a sidewalk in front of a courthouse, "
     "serious composed expressions, late-afternoon light. Reads as survivors coming forward "
     "together. Documentary news photo."),
    ("img07_phone_call",
     "A weathered Latina woman in her 50s at a kitchen table on a phone call, pressing the phone to "
     "her ear with both hands, eyes closed mid-sentence, a small notepad and pen in front of her "
     "(paper blank/illegible), soft window light. Reads as the moment she finally made the call."),
    ("img08_corridor",
     "Documentary ENG-camera shot down an empty women's prison cell-block corridor: rows of pale "
     "steel cell doors, polished concrete floor reflecting fluorescent strip lights, no people. "
     "Cold institutional realism, like investigative news footage."),
    ("img09_fence_hands",
     "Close-up of a woman's weathered hands with small faded tattoos gripping chain-link fence from "
     "the inside, beige institutional uniform sleeve visible, a blurred prison yard behind, harsh "
     "daylight. Face not visible. Direct, instantly readable as a woman incarcerated."),
    ("img10_paperwork",
     "A Latina woman in her 40s at home opening a thick manila envelope of legal paperwork at her "
     "kitchen table, pages in her hands (all text blurred/illegible), reading intently with a "
     "serious expression, morning light. Reads as her claim documents arriving."),
    # --- batch 2: prison-forward + old incarceration photos + her-life-now (2026-06-13) ---
    ("img11_visit_room_photo",
     "An aged early-2000s printed snapshot: a Latina woman in her 30s wearing a plain pale-blue "
     "chambray prison uniform (no printed lettering visible) posing stiffly in a prison visitation "
     "room in front of a painted tropical-beach mural backdrop, direct on-camera flash, slight film "
     "grain, faded colors, soft focus — the classic prison visit-room photo kept in a shoebox."),
    ("img12_yard_polaroid",
     "An aged faded snapshot photo: two Latina women in their 30s in plain pale-blue prison "
     "uniforms and denim (no printed lettering visible) standing side by side in a prison yard, "
     "arms crossed, chain-link fence and razor wire behind them, harsh midday sun, direct flash "
     "look, film grain, slightly washed-out 2000s colors — an old photo from when they were inside."),
    ("img13_phone_bank",
     "A Latina woman in her 40s in a plain pale-blue prison uniform standing at a row of steel "
     "wall-mounted prison phones in a concrete corridor, receiver pressed to her ear, head bowed, "
     "other phones empty beside her, harsh fluorescent light. Documentary realism, instantly reads "
     "as a women's prison phone bank."),
    ("img14_dayroom",
     "Documentary photo inside a women's prison dayroom: women in plain pale-blue uniforms seated "
     "at round steel tables bolted to the concrete floor, playing cards and talking quietly, "
     "high barred windows, fluorescent light, a guard station visible blurred in the background. "
     "News-photographer realism, nothing graphic."),
    ("img15_chow_line",
     "Documentary photo of a women's prison cafeteria line: women in plain pale-blue uniforms "
     "holding beige plastic trays moving along a steel serving counter, hairnetted server behind "
     "the glass, institutional tile and fluorescent light. Shot like investigative news footage."),
    ("img16_yard_walk",
     "Wide documentary shot of a California women's prison yard: a dozen women in plain pale-blue "
     "uniforms walking the dirt track in pairs, dry Central Valley ground, tall chain-link fence "
     "with razor-wire coils and a guard tower against a hazy sky. News ENG-camera realism."),
    ("img17_visit_hug",
     "An aged early-2000s printed snapshot: an incarcerated Latina mother in a plain pale-blue "
     "prison uniform kneeling to hug her young daughter in a prison visitation room, painted mural "
     "backdrop and vending machines behind, direct flash, film grain, faded warm colors — a "
     "treasured old visit photo."),
    ("img18_holding_old_photo",
     "A weathered Latina woman in her 50s at her kitchen table today, holding up an old faded "
     "printed snapshot of herself decades younger in a pale-blue prison uniform standing in a "
     "prison yard; her weathered hand and the aged photo in sharp focus, her face soft behind it, "
     "warm evening light. Then-and-now in a single frame."),
    ("img19_release_bus",
     "A Latina woman in her 40s sitting alone on a bench at a rural bus stop directly outside a "
     "prison's tall razor-wire fence, wearing plain grey sweats, a clear plastic bag of belongings "
     "beside her, flat early-morning light, looking down the empty road. Release day, documentary "
     "realism."),
    ("img20_night_shift",
     "A weathered Latina woman in her 40s in a fast-food work uniform and visor riding an empty "
     "late-night city bus home, leaning her head against the window, tired eyes open, reflections "
     "of street lights on the glass. Candid documentary realism — her life now, worn but holding "
     "on."),
]

OUT = Path("outputs/ccwf_women/image_ads")


def gen(slug, desc):
    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / f"{slug}.png"
    if dst.exists():
        return f"skip {slug}"
    try:
        res = generate_gpt_image(desc + REAL, aspect_ratio="3:4", resolution="2K")
        urls = res.get("urls") or []
        if not urls:
            return f"FAIL {slug}: {res.get('status')}"
        kie_download(urls[0], str(dst))
        return f"ok {slug}"
    except Exception as e:
        return f"ERR {slug}: {e}"


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(gen, s, d) for s, d in CONCEPTS]
        for f in as_completed(futs):
            print(f.result(), flush=True)
