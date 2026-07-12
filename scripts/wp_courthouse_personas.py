"""Shot-reverse-shot solo anchors for 'The Nice One' interview — male reporter + Black woman ~50
survivor, at a courthouse. Framed to face each other in the cut (reporter looks RIGHT, survivor
looks LEFT). gpt-image-2 t2i, 2K 9:16. 2 candidates each.
"""
import pathlib, concurrent.futures as cf, requests
from kie_client import generate_gpt_image

OUT = pathlib.Path("outputs/wp_interview2/reference"); OUT.mkdir(parents=True, exist_ok=True)
REAL = ("Photoreal candid documentary photo (NOT glamour, NOT a fashion shoot, NOT a celebrity "
        "portrait) — an ordinary real person, plain average features, natural skin with visible "
        "pores, fine lines, uneven tone, no makeup, no beauty retouching, no filter. Overcast "
        "natural daylight outside a courthouse: worn stone steps and columns of a civic government "
        "building softly out of focus behind. Waist-up, documentary framing.")

REPORTER = ("A male local news field reporter, early-to-mid 30s, medium-brown skin, short neat dark "
            "hair, light stubble, plain dark button-down shirt, holding a black foam-windscreen "
            "handheld microphone out toward the RIGHT side of the frame, looking to HIS RIGHT at an "
            "off-camera person he is interviewing, attentive and calm. " + REAL)
SURVIVOR = ("A Black woman, about 50, weathered and dignified. Round full face, deep-brown skin with "
            "visible pores and fine lines, tired but steady eyes, short natural hair greying at the "
            "temples, a small gold hoop earring, plain dark top under a worn cardigan. Looking to "
            "HER LEFT at an off-camera interviewer, mid-conversation, serious and candid. A black "
            "foam microphone tip enters from the LEFT edge of the frame toward her. " + REAL)

JOBS = {"reporter_a": REPORTER, "reporter_b": REPORTER,
        "survivor_a": SURVIVOR, "survivor_b": SURVIVOR}

def gen(name, prompt):
    r = generate_gpt_image(prompt, aspect_ratio="9:16", resolution="2K")
    if r.get("status") == "success" and r.get("urls"):
        dst = OUT / f"{name}.png"; dst.write_bytes(requests.get(r["urls"][0], timeout=120).content)
        return name, str(dst)
    return name, f"FAIL {str(r.get('raw'))[:120]}"

with cf.ThreadPoolExecutor(max_workers=4) as ex:
    for name, res in ex.map(lambda kv: gen(*kv), JOBS.items()):
        print(f"[done] {name} -> {res}")
print("ALL DONE")
