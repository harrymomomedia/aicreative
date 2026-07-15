"""Stage the 20 IL JDC image ads to AdMachin as DRAFTS (no launch, no spend).
Per ad: upload creative -> create its primary_text copy -> assemble ad (reuse the proven headline
'TAP TO SEE IF YOU QUALIFY'). Resumable via a state file (skip anything already staged) so a re-run
or a transient error never double-creates. ONE writer only (this script) for the state file.

UGC 01-10 use their longform primaries; news 11-20 use their short primaries.

  .venv/bin/python scripts/il_jdc_imageads_stage.py            # stage all 20
  .venv/bin/python scripts/il_jdc_imageads_stage.py --only u1_survivor_confession,d6_news_failed
"""
import argparse, json, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import admachin_client as am
from il_jdc_image_ads import ADS as IMG_ADS
from il_jdc_news_ads import NEWS

PROJECT = "e15c60bd-95c2-47b9-9730-c29fb5325461"        # Tort
SUBPROJECT = "7f876467-8262-4647-91b1-d56574976079"     # IL JDC
HEADLINE_ID = "33205221-a2d0-4566-a132-f63452023344"    # "TAP TO SEE IF YOU QUALIFY" (reuse)
OUT = Path("outputs/il_jdc_image_ads")
STATE = OUT / "admachin_stage.json"

# 10 UGC longforms (type==ugc) + 10 news-article ads -> 20
UGC = [a for a in IMG_ADS if a.get("type") == "ugc"]
ADS20 = sorted(UGC + list(NEWS), key=lambda a: a["n"])


def load_state():
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def save_state(st):
    STATE.write_text(json.dumps(st, indent=2, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    only = {s.strip() for s in args.only.split(",") if s.strip()}
    st = load_state()
    done = staged = 0
    for ad in ADS20:
        slug = ad["slug"]
        if only and slug not in only:
            continue
        rec = st.setdefault(slug, {})
        if rec.get("ad_id"):
            print(f"[skip] {ad['n']:02d} {slug} -> ad {rec['ad_id'][:8]}", flush=True)
            done += 1
            continue
        path = OUT / f"{ad['n']:02d}_{slug}.png"
        if not path.exists():
            print(f"[MISS] {ad['n']:02d} {slug}: no image at {path}", flush=True)
            continue
        try:
            if not rec.get("creative_id"):
                cr = am.upload_creative(str(path), type="image",
                                        project_id=PROJECT, subproject_id=SUBPROJECT)
                rec["creative_id"] = cr["id"]
                save_state(st)
            if not rec.get("primary_id"):
                cp = am.create_ad_copy(ad["primary"], "primary_text",
                                       project_id=PROJECT, subproject_id=SUBPROJECT)
                rec["primary_id"] = cp["id"]
                save_state(st)
            a = am.create_ad(rec["creative_id"], headline_id=HEADLINE_ID,
                             primary_id=rec["primary_id"],
                             project_id=PROJECT, subproject_id=SUBPROJECT)
            rec["ad_id"] = a["id"]
            save_state(st)
            staged += 1
            print(f"[ok]   {ad['n']:02d} {slug} -> ad {a['id']}", flush=True)
        except Exception as e:
            print(f"[FAIL] {ad['n']:02d} {slug}: {type(e).__name__}: {str(e)[:160]}", flush=True)
            save_state(st)
        time.sleep(0.3)
    print(f"\n=== staged {staged} new, {done} already done, {len(ADS20)} total ===", flush=True)
    print(f"state: {STATE}")


if __name__ == "__main__":
    main()
