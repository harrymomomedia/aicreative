#!/usr/bin/env python3
"""Stage the 20 meningioma-only Depo ads into AdMachin as full DRAFT ads (no launch).
Per ad: upload creative -> headline copy -> primary copy -> assemble draft ad, Tort / Depo Provera.
Resumable own state file (keyed by global n). ad_type omitted (defaults "Image"). NO launch code.

    .venv/bin/python scripts/depo_meningioma_admachin_stage.py [--only <n,..>]
"""
import argparse
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import admachin_client as am  # noqa: E402
from depo_meningioma20_gen import ADS, dest_for  # noqa: E402

PROJECT_ID = "e15c60bd-95c2-47b9-9730-c29fb5325461"      # Tort
SUBPROJECT_ID = "9cfb5b76-1dd3-4e07-b037-2dda178ac266"   # Depo Provera
STATE = pathlib.Path("outputs/depo_ads/meningioma_admachin_state.json")


def load_state():
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def save_state(st):
    STATE.write_text(json.dumps(st, indent=2))


def stage_one(ad, st):
    key = str(ad["n"])
    rec = st.setdefault(key, {"slug": ad["slug"]})
    img = dest_for(ad)
    if not img.is_file():
        return "no-image"
    headline = ad["headline"]
    primary = ad["primary"]
    if not rec.get("creative_id"):
        ik = hashlib.sha256(f"{img.resolve()}|{img.stat().st_size}".encode()).hexdigest()[:32]
        cr = am.upload_creative(img, type="image", project_id=PROJECT_ID, subproject_id=SUBPROJECT_ID, idem_key=ik)
        rec["creative_id"] = cr["id"]; save_state(st)
    if not rec.get("headline_id"):
        h = am.create_ad_copy(headline, "headline", project_id=PROJECT_ID, subproject_id=SUBPROJECT_ID,
                              name=f"depo mening {ad['n']:02d} H")
        rec["headline_id"] = h["id"]; save_state(st)
    if not rec.get("primary_id"):
        p = am.create_ad_copy(primary, "primary_text", project_id=PROJECT_ID, subproject_id=SUBPROJECT_ID,
                              name=f"depo mening {ad['n']:02d} P")
        rec["primary_id"] = p["id"]; save_state(st)
    if not rec.get("ad_id"):
        a = am.create_ad(rec["creative_id"], headline_id=rec["headline_id"], primary_id=rec["primary_id"],
                         project_id=PROJECT_ID, subproject_id=SUBPROJECT_ID)
        rec["ad_id"] = a["id"]; save_state(st)
    return rec["ad_id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    want = {s.strip() for s in args.only.split(",") if s.strip()}
    ads = [a for a in ADS if not want or str(a["n"]) in want]
    st = load_state()
    print("Staging 20 meningioma-only ads into Tort / Depo Provera — DRAFTS, no launch\n")
    done = 0
    for ad in ads:
        if st.get(str(ad["n"]), {}).get("ad_id"):
            print(f"[skip] {ad['n']:02d} -> {st[str(ad['n'])]['ad_id']}"); done += 1; continue
        try:
            res = stage_one(ad, st)
            if res == "no-image":
                print(f"[wait] {ad['n']:02d} (no image)")
            else:
                print(f"[ok]   {ad['n']:02d} {ad['slug'][:24]} -> {res}"); done += 1
        except Exception as e:
            print(f"[ERR]  {ad['n']:02d} -> {type(e).__name__}: {e}")
    print(f"\n==== {done}/{len(ads)} staged ====\nstate: {STATE}")


if __name__ == "__main__":
    main()
