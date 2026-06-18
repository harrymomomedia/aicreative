"""UGC testimonial personas for the tort IL JDC campaign (new single-person direct-address format).
5 candidates each for: #1 whistleblower (former facility STAFF, older/credible, racial variety),
#4 brother (Black man 30s-40s, protective), #5 cousin/Audy Home (Black man 30s-40s, survivor).
Direct-to-lens testimonial selfie in everyday UGC settings. KIE gpt-image-2, 2K, 9:16.
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, download as kie_download

STYLE = (
    " Photoreal candid UGC testimonial video selfie, shot on a front-facing phone camera held at "
    "arm's length at roughly eye level, the person looking and talking DIRECTLY INTO the lens like a "
    "real Facebook / TikTok testimonial. Vertical close-to-medium framing, head and shoulders, the "
    "face filling much of the frame. Natural everyday lighting. NOT a glamour or fashion shoot, NOT a "
    "celebrity portrait — an ordinary, everyday, relatable person with plain average features. Natural "
    "skin with visible pores, blemishes, uneven tone, slight under-eye shadows, imperfect teeth, no "
    "makeup, no beauty retouching, no filter, no skin smoothing. Shallow depth of field, background "
    "slightly out of focus. 9:16 vertical. NO on-screen text, NO captions, NO watermarks."
)

PERSONAS = {
    "whistleblower": [  # former juvenile-facility staff: older, credible, serious, direct
        ("whis1", "A Black man, age 52, short greying hair and a neat grey-flecked beard, medium-dark "
         "skin, sturdy build, wearing a plain dark-navy polo shirt. Sitting in the driver's seat of a "
         "parked car in daylight. Serious, weathered, credible — a former corrections officer who "
         "decided to finally talk, speaking plainly into the camera."),
        ("whis2", "A white man, age 50, greying buzzcut, clean-shaven with a heavy jaw, wearing a plain "
         "grey henley. Sitting at a kitchen table at home, plain wall behind. Tired, grave, "
         "matter-of-fact — an ex-staff member unburdening himself."),
        ("whis3", "A Black man, age 48, bald with a short salt-and-pepper goatee, glasses, average "
         "build, wearing a plain charcoal crew-neck. Sitting on a couch in a modest living room. Calm, "
         "serious, credible, looking directly into the lens."),
        ("whis4", "A Latino man, age 54, short dark hair greying at the temples and a thick mustache, "
         "wearing a plain olive button-up shirt. Standing in a plain home hallway. Solemn and careful, "
         "choosing his words — a former facility worker."),
        ("whis5", "A white man, age 55, thinning grey hair combed back and a short grey beard, lined "
         "weathered face, wearing a plain blue work polo. Sitting in a home office, plain wall behind. "
         "Heavy and regretful but resolved — an insider finally speaking."),
    ],
    "brother": [  # speaks FOR his abused younger brother
        ("bro1", "A Black man, age 38, short hair with a slightly receding hairline and a full beard "
         "flecked with grey, medium-brown skin, wearing a plain dark flannel over a tee. Sitting on a "
         "couch at home. Protective and controlled, jaw set, holding back anger as he speaks for his "
         "brother."),
        ("bro2", "A Black man, age 34, short fade and a neat goatee, deep-brown skin, wearing a plain "
         "grey t-shirt. Sitting in the driver's seat of a parked car. Serious and steady, looking into "
         "the lens, carrying his brother's story."),
        ("bro3", "A Black man, age 41, bald with a full short beard, average build, medium-brown skin, "
         "wearing a plain black henley. Standing in a kitchen. Heavy and protective, quiet anger held "
         "under control."),
        ("bro4", "A Black man, age 36, short twists and a thin beard, wearing a plain navy crew-neck. "
         "Sitting at a dining table, plain home behind. Earnest and pained but composed, telling what "
         "his brother can't."),
        ("bro5", "A Black man, age 39, short 360 waves and a chin-strap beard, sturdy build, wearing a "
         "plain maroon t-shirt. Sitting on a porch step in daylight. Grounded and protective, speaking "
         "direct into the lens."),
    ],
    "family": [  # cousin/peer survivor, Audy Home / Cook County
        ("fam1", "A Black man, age 35, short fade with a crisp line-up and a thin mustache, "
         "medium-brown skin, wearing a plain white t-shirt. Sitting on a couch in a modest apartment. "
         "Reflective and steady — an ordinary man telling the truth into the lens."),
        ("fam2", "A Black man, age 33, bald with light stubble, a bit heavyset, deep-brown skin, "
         "wearing a charcoal hoodie with the hood down. In the driver's seat of a parked car. Calm but "
         "heavy, looking directly at the camera."),
        ("fam3", "A Black man, age 40, short hair with a full beard, average build, wearing a plain "
         "heather-grey t-shirt. Standing in a small kitchen. Matter-of-fact and grounded — a survivor "
         "done being quiet."),
        ("fam4", "A Black man, age 31, short afro, clean-shaven with a small gap in his front teeth, "
         "wearing a plain olive t-shirt. Sitting at a kitchen table. Sincere and quiet, looking into "
         "the lens."),
        ("fam5", "A Black man, age 37, cornrows braided straight back and a thin beard, medium-brown "
         "skin, wearing a plain black t-shirt. Sitting on the edge of a bed in a plain room. Steady and "
         "reflective, telling it straight."),
    ],
}


def gen(concept, slug, desc):
    out = Path(f"outputs/illinois_jdc_tort_{concept}/reference")
    out.mkdir(parents=True, exist_ok=True)
    dst = out / f"{slug}.png"
    if dst.exists():
        return f"skip {slug}"
    try:
        res = generate_gpt_image(desc + STYLE, aspect_ratio="9:16", resolution="2K")
        urls = res.get("urls") or []
        if not urls:
            return f"FAIL {slug}: no url ({res.get('status')})"
        kie_download(urls[0], str(dst))
        return f"ok {slug}"
    except Exception as e:
        return f"ERR {slug}: {e}"


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    jobs = [(c, s, d) for c, lst in PERSONAS.items() if (not only or c == only) for s, d in lst]
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(gen, c, s, d) for c, s, d in jobs]
        for f in as_completed(futs):
            print(f.result(), flush=True)
