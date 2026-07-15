"""Stage the 30 CA women's-prison image ads (jdcstyle20 + social10) to AdMachin as DRAFTS, then
they're ready for bulk_launch into WPA - Latina - HJ P1. Per ad: burn the Pulaski/Jones disclaimer
BAR onto the image -> upload creative -> create its own headline + primary copy (primary gets the
verbatim disclaimer appended) -> assemble ad. Resumable via a state file (ONE writer = this script).

  .venv/bin/python scripts/ccwf_launch30_stage.py            # stage all 30
  .venv/bin/python scripts/ccwf_launch30_stage.py --only j01_newspaper,s04_groupchat
  .venv/bin/python scripts/ccwf_launch30_stage.py --ids      # just print slug -> ad_id (for launch)
"""
import argparse, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import admachin_client as am
from caption_styled import DEFAULT_DISCLAIMER
from burn_disclaimer_image import burn as burn_disc

PROJECT = "e15c60bd-95c2-47b9-9730-c29fb5325461"        # Tort
SUBPROJECT = "acf1b974-9721-488b-a4e0-ffe0664070c5"     # Women's Prison
BASE = ROOT / "outputs/ccwf_women"
STATE = BASE / "launch30_stage.json"

# (slug, batch-dir, headline, primary)  — primary as approved in chat; disclaimer appended at stage.
COPY = [
 ("j01_newspaper","jdcstyle20","California women's prisons face abuse lawsuits",
  "For years, women in California's prisons were sexually abused by the staff who were supposed to keep them safe — and now survivors are coming forward. If a guard, officer, or staff member sexually abused you at Chowchilla (CCWF), Valley State, CIW (Chino), or Folsom, you may qualify for significant potential compensation. You don't need a police report, it doesn't matter how long ago it was, and it's completely confidential. A private case review is free and takes about two minutes. 👉 Tap below to check if you qualify."),
 ("j02_tv_broadcast","jdcstyle20","Women allege staff sexual abuse in CA prisons",
  "Women across California's prisons are speaking out about staff sexual abuse — and you're not alone. If a staff member sexually abused you while you were incarcerated at a California women's prison, you may qualify for significant potential compensation. No police report needed. No deadline. 100% confidential and free. 👉 Tap to see if you qualify in about two minutes."),
 ("j03_accountability","jdcstyle20","Lawsuits: CA failed to protect women inside",
  "Lawsuits allege that for years California failed to stop staff from sexually abusing women in its prisons. If a guard or staff member sexually abused you at Chowchilla, Chino, Valley State, or Folsom, you may qualify for significant potential compensation. It's free, confidential, and you never have to set foot in a courtroom. It doesn't matter how long ago it happened. 👉 Tap below to check, privately."),
 ("j04_explainer","jdcstyle20","What survivors should know",
  "If you were sexually abused by staff in a California women's prison, here's what you should know: you may qualify for significant potential compensation, you don't need a police report, there's no deadline even if it was decades ago, and it's 100% free and confidential. Nobody in your life has to know you checked. 👉 Tap below for a free, private case review."),
 ("j05_magazine","jdcstyle20","The reckoning inside CA's women's prisons",
  "For years, women said staff sexually abused them inside California's prisons — and that they were ignored. Now survivors are finally being heard. If this happened to you at Chowchilla, Valley State, CIW (Chino), or Folsom, you may qualify for significant potential compensation. There's no deadline, no police report required, and it's completely confidential. 👉 Tap below to see if you qualify — free, about two minutes."),
 ("j06_oped","jdcstyle20","They were ignored for years. Not anymore.",
  "For decades, women who reported being sexually abused by prison staff were met with silence. That's finally changing. If a staff member sexually abused you while you were incarcerated in a California women's prison, you may qualify for significant potential compensation — even if it happened years ago and you never told a soul. Free, confidential, no court. 👉 Tap to check privately."),
 ("j07_reddit","jdcstyle20","You're not the only one",
  "So many women are realizing they weren't the only one. If a guard or staff member sexually abused you at a California women's prison, you may qualify for significant potential compensation. You don't need a police report and it's completely confidential — no one in your life has to know. 👉 Tap below to see if you qualify."),
 ("j08_comments","jdcstyle20","You are not the only one",
  "Every day more women are realizing they weren't the only one. If a staff member sexually abused you inside a California women's prison, you may qualify for significant potential compensation. No police report needed, no deadline, and it's completely confidential. 👉 Tap below to check privately."),
 ("j09_google","jdcstyle20","If it happened to you, you're not alone",
  "If you've ever searched for answers about what happened to you behind bars, you're not the only one. Women sexually abused by staff in California's prisons — Chowchilla, Chino, Valley State, Folsom — may qualify for significant potential compensation. It's free, confidential, and there's no deadline. 👉 Tap to see if you qualify."),
 ("j10_native_post","jdcstyle20","Please read this",
  "If you were sexually abused by a staff member while you were in a California women's prison, please read this. You are not alone, and it was not your fault. You may qualify for significant potential compensation — it's free, private, and no one in your life has to know. There's no deadline and you don't need a police report. 👉 Tap below to check."),
 ("j11_definition","jdcstyle20","The law calls it abuse",
  "If a staff member used their authority to coerce you into sexual acts while you were in a California women's prison, the law calls it abuse — no matter what they called it at the time. You may qualify for significant potential compensation. Free, confidential, no police report, no deadline. 👉 Tap to check privately."),
 ("j12_calendar","jdcstyle20","There's no deadline",
  "It doesn't matter how long ago it was — there is no deadline to come forward. If a staff member sexually abused you in a California women's prison, you may qualify for significant potential compensation, even if it happened decades ago and you never reported it. Free and 100% confidential. 👉 Tap below to see if you qualify."),
 ("j13_voicemail","jdcstyle20","When you're ready to talk",
  "A lot of women are finally ready to talk about what happened to them inside. If a staff member sexually abused you at a California women's prison, you may qualify for significant potential compensation — whenever you're ready. It's free, confidential, and there's no deadline. 👉 Tap below to check, privately."),
 ("j14_stickynote","jdcstyle20","It wasn't your fault",
  "It wasn't your fault, and you can still come forward. If a staff member sexually abused you while you were in a California women's prison, you may qualify for significant potential compensation. It's free, completely private, and no one has to know. There's no deadline. 👉 Tap below to check."),
 ("j15_faq","jdcstyle20","Your questions, answered",
  "It was years ago — do you still qualify? Yes, there's no deadline. Never reported it? You don't need a police report. Worried someone will find out? It's 100% confidential. If a staff member sexually abused you in a California women's prison, you may qualify for significant potential compensation. 👉 Tap below for a free, private review."),
 ("j16_myth_fact","jdcstyle20","It's not too late",
  "Myth: it's been too long, nothing can be done. Fact: there's no deadline, and survivors are coming forward now. If a staff member sexually abused you in a California women's prison, you may qualify for significant potential compensation. Free, confidential, no court. 👉 Tap to see if you qualify."),
 ("j17_numbers","jdcstyle20","By the numbers",
  "Four California women's prisons named — Chowchilla, Chino, Valley State, and Folsom. Zero police reports required. No deadline to come forward. 100% free and confidential. If a staff member sexually abused you inside, you may qualify for significant potential compensation. 👉 Tap below to check privately."),
 ("j18_authority","jdcstyle20","Now reviewing claims",
  "Sexual-abuse claims from survivors of California's women's prisons — Chowchilla, Chino, Valley State, and Folsom — are now being reviewed. If a staff member sexually abused you, you may qualify for significant potential compensation. The case review is free, confidential, and takes about two minutes. 👉 Tap below to start."),
 ("j19_lovedone","jdcstyle20","For a woman you love",
  "Your mother. Your sister. Your friend. If a woman you love was sexually abused by staff while she was in a California women's prison, she may qualify for significant potential compensation. It's free, confidential, and there's no deadline — share this with her, or check on her behalf. 👉 Tap below to learn more."),
 ("j20_testimonial","jdcstyle20","I never told a soul — until now",
  "\"A guard did things to me at Chowchilla. I never told a soul — until now.\" If a staff member sexually abused you while you were incarcerated in a California women's prison, you are not alone, and it was not your fault. You may qualify for significant potential compensation. There's no deadline, no police report needed, and it's completely confidential. 👉 Tap below to see if you qualify — free and private."),
 ("s01_reddit_valley","social10","You're not alone",
  "If a guard or staff member sexually abused you at Valley State — or any California women's prison — you're not the only one. You may qualify for significant potential compensation. No police report needed, no deadline, completely confidential. 👉 Tap to check privately."),
 ("s02_reddit_90s","social10","It's not too late",
  "Even if it happened back in the 90s at CIW (Chino), it's not too late — there's no deadline. If a staff member sexually abused you in a California women's prison, you may qualify for significant potential compensation. Free and confidential. 👉 Tap to see if you qualify."),
 ("s03_forum_thread","social10","Coming forward, finally",
  "More women are coming forward after all these years — and they're being heard. If a staff member sexually abused you in a California women's prison, you may qualify for significant potential compensation. It's free, private, and there's no deadline. 👉 Tap below to check."),
 ("s04_groupchat","social10","Did you see this?",
  "Women are sharing this with each other for a reason. If a guard did something to you inside a California women's prison, you may qualify for significant potential compensation. It's free to check and completely confidential. 👉 Tap to see if you qualify."),
 ("s05_text_dm","social10","This might be about you",
  "Women who were sexually abused by staff in a California women's prison are getting help now. If that was you, you may qualify for significant potential compensation. It's confidential, free, and there's no deadline. 👉 Tap below to check privately."),
 ("s06_comments_notalone","social10","You are not alone",
  "Folsom. Chowchilla. Chino. Valley State. Women from California's prisons are realizing they weren't the only one. If a staff member sexually abused you inside, you may qualify for significant potential compensation — free and confidential. 👉 Tap to check."),
 ("s07_comments_privacy","social10","100% confidential",
  "Worried someone will find out? It's completely confidential — no one in your life has to know. If a staff member sexually abused you in a California women's prison, you may qualify for significant potential compensation. Free, private, no deadline. 👉 Tap below to check."),
 ("s08_advocate_dm","social10","When you're ready",
  "If a staff member sexually abused you while you were in a California women's prison, you may qualify for significant potential compensation. It's free, confidential, and takes about two minutes to check — whenever you're ready. 👉 Tap below to start, privately."),
 ("s09_comments_toolate","social10","Even decades later",
  "Thought it was too late? It's not — there's no deadline, even if it was over twenty years ago. If a staff member sexually abused you in a California women's prison, you may qualify for significant potential compensation. Free and confidential. 👉 Tap to see if you qualify."),
 ("s10_reviews","social10","Free, private, and heard",
  "Women who came forward say they finally felt heard — and that it was free and private, just like they were told. If a staff member sexually abused you in a California women's prison, you may qualify for significant potential compensation. No deadline, no police report. 👉 Tap below to check."),
]


def load_state():
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def save_state(st):
    STATE.write_text(json.dumps(st, indent=2, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--ids", action="store_true")
    args = ap.parse_args()
    st = load_state()

    if args.ids:
        for slug, *_ in COPY:
            print(f"{slug}\t{st.get(slug, {}).get('ad_id', '-')}")
        return

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    staged = done = 0
    for slug, d, headline, primary in COPY:
        if only and slug not in only:
            continue
        rec = st.setdefault(slug, {})
        if rec.get("ad_id"):
            print(f"[skip] {slug} -> ad {rec['ad_id'][:8]}", flush=True); done += 1; continue
        src = BASE / d / f"{slug}.png"
        if not src.exists():
            print(f"[MISS] {slug}: no image {src}", flush=True); continue
        disc = BASE / d / "final" / f"{slug}_disc.png"
        try:
            if not disc.exists():
                burn_disc(str(src), str(disc), style="bar")
            if not rec.get("creative_id"):
                cr = am.upload_creative(str(disc), type="image",
                                        project_id=PROJECT, subproject_id=SUBPROJECT)
                rec["creative_id"] = cr["id"]; save_state(st)
            if not rec.get("headline_id"):
                hc = am.create_ad_copy(headline, "headline",
                                       project_id=PROJECT, subproject_id=SUBPROJECT)
                rec["headline_id"] = hc["id"]; save_state(st)
            if not rec.get("primary_id"):
                full = primary + "\n\n" + DEFAULT_DISCLAIMER
                cp = am.create_ad_copy(full, "primary_text",
                                       project_id=PROJECT, subproject_id=SUBPROJECT)
                rec["primary_id"] = cp["id"]; save_state(st)
            a = am.create_ad(rec["creative_id"], headline_id=rec["headline_id"],
                             primary_id=rec["primary_id"],
                             project_id=PROJECT, subproject_id=SUBPROJECT)
            rec["ad_id"] = a["id"]; save_state(st)
            staged += 1
            print(f"[ok]   {slug} -> ad {a['id']}", flush=True)
        except Exception as e:
            print(f"[FAIL] {slug}: {type(e).__name__}: {str(e)[:200]}", flush=True)
            save_state(st)
        time.sleep(0.3)
    print(f"\n=== staged {staged} new, {done} already done, {len(COPY)} total ===", flush=True)


if __name__ == "__main__":
    main()
