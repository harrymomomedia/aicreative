#!/usr/bin/env python3
"""Stage the 20 Depo-Provera image ads into AdMachin as DRAFTS (no launch).

For each ad: upload creative -> create headline copy -> create primary copy -> assemble ONE draft ad
under Tort / Depo Provera. Resumable via a state file (one writer). There is NO launch code in this
script by construction — it can only ever create drafts. Copy is the user-approved text from
inventory/depo_provera_ad_copy.md.

    .venv/bin/python scripts/depo_admachin_stage.py            # stage all (skip already-done)
    .venv/bin/python scripts/depo_admachin_stage.py --only quiz,stat
"""
import argparse
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import admachin_client as am  # noqa: E402

PROJECT_ID = "e15c60bd-95c2-47b9-9730-c29fb5325461"      # Tort
SUBPROJECT_ID = "9cfb5b76-1dd3-4e07-b037-2dda178ac266"   # Depo Provera
AD_TYPE = None   # 'ads_ad_type_allowed' DB check rejects free-text; subproject groups them
FINAL = pathlib.Path("outputs/depo_ads/final")
STATE = pathlib.Path("outputs/depo_ads/admachin_state.json")

TESTIMONIAL = (
    'When the doctor said "brain tumor," the room went silent. A meningioma. I kept asking — where '
    "did this come from? I did everything right.\n"
    "I was healthy. The one thing I'd done for years was the Depo shot, every three months. My doctor "
    "said it was the easy one. I trusted it.\n"
    "Nobody ever warned me it could do this. I found out later there were studies. They knew.\n"
    "I'm not the type to sue anybody. But women diagnosed with a meningioma after the shot may qualify "
    "for significant compensation — free and private just to check. So I did.\n"
    "If you have a meningioma and were ever on Depo-Provera, please, just see if you qualify. You're "
    "not alone.\n"
    "Attorney Advertising. Dramatization — not an actual client."
)
ADVERTORIAL = (
    "Thousands of women are being diagnosed with the same brain tumor — a meningioma. Here's the link "
    "doctors are now seeing.\n"
    "A meningioma grows in the lining of the brain. For years, women diagnosed with one were told it "
    "was just bad luck. Now researchers point to a shared cause: the Depo-Provera birth-control shot.\n"
    "A major study found women who used Depo for more than a year were up to 5× more likely to develop "
    "one. Some needed surgery. Some lost their vision. Most were never warned. A federal lawsuit is now "
    "underway against the manufacturer.\n"
    "If you've been diagnosed with a meningioma and you used Depo-Provera, you may qualify for "
    "significant compensation. It's free and confidential to check.\n"
    "Attorney Advertising."
)

# (n, slug, headline, primary) — verbatim from inventory/depo_provera_ad_copy.md
ADS = [
    (1, "quiz", "Meningioma + Depo? See If You Qualify",
     "Diagnosed with a brain tumor — a meningioma? If you were ever on the Depo-Provera shot, the two "
     "may be linked. Take our free 60-second quiz to see if you may qualify for significant "
     "compensation. Attorney Advertising."),
    (2, "criteria", "Do You Meet the Criteria?",
     "Diagnosed with a meningioma (brain tumor) and used Depo-Provera for a year or more? You may meet "
     "the criteria to file a claim. Checking is free and confidential and takes about a minute. You may "
     "qualify for significant compensation. Attorney Advertising."),
    (3, "stat", "Depo Linked to 5.6× Brain-Tumor Risk",
     "A meningioma diagnosis is hard enough. A major study found women who used the Depo-Provera shot "
     "for over a year were up to 5.6× more likely to develop one. If that's you, you may qualify for "
     "significant compensation — and it's free to check. Attorney Advertising."),
    (4, "everything_right", "So Where Did the Tumor Come From?",
     "You ate right. You worked out. You did everything right — and still ended up with a brain tumor. "
     "For thousands of women, the one thing in common was the Depo-Provera shot, now linked to "
     "meningioma. If you were diagnosed, you may qualify for significant compensation. It's free and "
     "confidential to find out. Attorney Advertising. Dramatization."),
    (5, "symptom", "Know the Signs of a Meningioma",
     "Headaches that won't quit. Blurred vision. Memory slips. Seizures. These can be signs of a "
     "meningioma — a brain tumor now linked to the Depo-Provera shot. If you've been diagnosed and once "
     "used Depo, you may qualify for significant compensation. Attorney Advertising."),
    (6, "authority", "We're Reviewing Depo Claims Now",
     "Diagnosed with a meningioma after using the Depo-Provera birth-control shot? Our team is reviewing "
     "claims for women across the country. The review is free and confidential, and you may qualify for "
     "significant compensation. Attorney Advertising. Dramatization."),
    (7, "native_post", "Were You On the Depo Shot?",
     "If you took the Depo shot and were later diagnosed with a meningioma (a brain tumor), the two may "
     "be linked — and you may qualify for significant compensation. It's free and confidential to "
     "check, and it only takes a minute. Attorney Advertising."),
    (8, "notice", "Depo-Provera Meningioma Legal Review",
     "LEGAL REVIEW: Claims involving meningioma (brain tumor) diagnoses following Depo-Provera use are "
     "now under review. If you used the injection and were later diagnosed, a free, confidential case "
     "review is available and you may qualify for significant compensation. No guarantee of outcome. "
     "Eligibility requirements apply. Attorney Advertising."),
    (9, "news_headline", "Birth-Control Shot Tied to Brain Tumors",
     "A common birth-control shot is being tied to brain tumors. Studies link Depo-Provera to "
     "meningioma, and women diagnosed are now filing claims nationwide. If you used Depo and were "
     "diagnosed with a meningioma, you may qualify for significant compensation. Attorney Advertising."),
    (10, "value", "A Diagnosis That Changes Everything",
     "A meningioma diagnosis changes everything. If you used the Depo-Provera shot before being "
     "diagnosed with this brain tumor, you may qualify for significant compensation. Free and "
     "confidential to check. Results not guaranteed; eligibility applies. Attorney Advertising."),
    (11, "testimonial", '"They Said It Was a Brain Tumor."', TESTIMONIAL),
    (12, "advertorial", "The Link Doctors Are Now Seeing", ADVERTORIAL),
    (13, "open_letter", "A Letter to Women With a Meningioma",
     "To every woman living with a meningioma: it may not be your fault, and it may not be a "
     "coincidence. The Depo-Provera shot has been linked to these brain tumors, and most women were "
     "never warned. If you were diagnosed after using Depo, you may qualify for significant "
     "compensation. It's free and private to find out. Attorney Advertising."),
    (14, "reddit", "Could Depo Have Caused My Meningioma?",
     '"Diagnosed with a meningioma — turns out my old birth control may have caused it?" Women who used '
     "Depo-Provera and were later diagnosed with this brain tumor are finding out they may qualify for "
     "significant compensation. Free and confidential to check. Attorney Advertising. Dramatization."),
    (15, "texts", "Were You On Depo for Years?",
     '"Wait… I was on Depo for years." Women are realizing the birth-control shot may be linked to their '
     "meningioma (brain tumor) diagnosis. If that's you, you may qualify for significant compensation. "
     "Free to check. Attorney Advertising."),
    (16, "faq", "Diagnosed Years Ago? You May Still Qualify",
     "Q: I used Depo years ago — is it too late? A: Not necessarily. If you were diagnosed with a "
     "meningioma (a brain tumor), you may still qualify for significant compensation — even years later. "
     "Checking is free and confidential. Attorney Advertising."),
    (17, "then_now", "From the Depo Shot to a Brain Tumor",
     "Then: years on the Depo shot, trusting it was safe. Now: a meningioma diagnosis and brain surgery. "
     "For thousands of women, the two are connected — and those diagnosed may qualify for significant "
     "compensation. Free and confidential to check. Attorney Advertising. Dramatization."),
    (18, "myth_fact", "Think It's Too Late? It May Not Be",
     "MYTH: it's been too long, there's nothing you can do. FACT: if you were diagnosed with a "
     "meningioma after using Depo-Provera, you may still qualify for significant compensation — even if "
     "it was years ago. Free to check. Attorney Advertising."),
    (19, "psa", "Depo-Provera Is Now Part of a Lawsuit",
     "Did you know? The Depo-Provera shot is now part of a federal lawsuit over brain tumors. Women "
     "diagnosed with a meningioma after using it may qualify for significant compensation. It's free "
     "and confidential to see if you qualify. Attorney Advertising."),
    (20, "referral", "Help Someone You Love Check",
     "Your mom. Your sister. Your best friend. If a woman you love was diagnosed with a meningioma (a "
     "brain tumor) and used Depo-Provera, you can help her take the first step. She may qualify for "
     "significant compensation, and it's free and confidential to check. Attorney Advertising. "
     "Dramatization."),
]


def load_state():
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def save_state(st):
    STATE.write_text(json.dumps(st, indent=2))


def stage_one(n, slug, headline, primary, st):
    rec = st.setdefault(slug, {})
    img = FINAL / f"{n:02d}_{slug}_4x5.png"
    if not img.is_file():
        return f"MISSING IMAGE {img}"

    if not rec.get("creative_id"):
        key = hashlib.sha256(f"{img.resolve()}|{img.stat().st_size}".encode()).hexdigest()[:32]
        cr = am.upload_creative(img, type="image", project_id=PROJECT_ID,
                                subproject_id=SUBPROJECT_ID, rating=None, idem_key=key)
        rec["creative_id"] = cr["id"]
        save_state(st)

    if not rec.get("headline_id"):
        h = am.create_ad_copy(headline, "headline", project_id=PROJECT_ID,
                              subproject_id=SUBPROJECT_ID, name=f"depo {slug} headline")
        rec["headline_id"] = h["id"]
        save_state(st)

    if not rec.get("primary_id"):
        p = am.create_ad_copy(primary, "primary_text", project_id=PROJECT_ID,
                              subproject_id=SUBPROJECT_ID, name=f"depo {slug} primary")
        rec["primary_id"] = p["id"]
        save_state(st)

    if not rec.get("ad_id"):
        ad = am.create_ad(rec["creative_id"], headline_id=rec["headline_id"],
                          primary_id=rec["primary_id"], ad_type=AD_TYPE,
                          project_id=PROJECT_ID, subproject_id=SUBPROJECT_ID)
        rec["ad_id"] = ad["id"]
        save_state(st)
    return rec["ad_id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    want = {s.strip() for s in args.only.split(",") if s.strip()}

    st = load_state()
    print(f"Staging into Tort / Depo Provera  (ad_type={AD_TYPE})  — DRAFTS ONLY, no launch\n")
    done = []
    for n, slug, headline, primary in ADS:
        if want and slug not in want:
            continue
        if st.get(slug, {}).get("ad_id"):
            print(f"[skip] {n:02d} {slug} -> ad {st[slug]['ad_id']}")
            done.append((slug, st[slug]["ad_id"]))
            continue
        try:
            ad_id = stage_one(n, slug, headline, primary, st)
            print(f"[ok]   {n:02d} {slug} -> ad {ad_id}")
            done.append((slug, ad_id))
        except am.AdMachinError as e:
            print(f"[ERR]  {n:02d} {slug} -> {e}")
        except Exception as e:
            print(f"[ERR]  {n:02d} {slug} -> {type(e).__name__}: {e}")

    print(f"\n==== {len(done)} draft ads staged ====")
    for slug, ad_id in done:
        print(f"  {slug:16s} {ad_id}")
    print(f"\nstate: {STATE}")


if __name__ == "__main__":
    main()
