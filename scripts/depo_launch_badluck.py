#!/usr/bin/env python3
"""Launch the 2 Bad Luck ads into a NEW adset "42" duplicated from adset 41 (YJE-23,
Depo - Pulaski HJ campaign), $100/day. Same targeting/optimization as adset 41.

⚠ --go SPENDS REAL MONEY on Facebook. Default is validate-only (no spend).
Default UTM: NOT overridden — the API's default {{ }} template + am_mb={{media_buyer_code}} applies.

Run:
  .venv/bin/python scripts/depo_launch_badluck.py            # validate only
  .venv/bin/python scripts/depo_launch_badluck.py --go       # LAUNCH (real spend)
"""
import sys, json, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from admachin_client import _post

# Bad Luck ads (from outputs/depo_admachin_stage.json)
AD_IDS = [
    "c2d189d3-4cbe-4207-b139-4a5ac1e1591f",  # badluck_stacked
    "0c312659-84d1-406f-bfe8-a111f7d96671",  # badluck_cut
]

# YJE-23 / Depo - Pulaski HJ  (discovered via read-only FB calls)
AD_ACCOUNT_ID = "act_885970616544640"
CAMPAIGN_ID   = "120251695982040281"        # "Depo - Pulaski HJ"
SOURCE_ADSET  = "120252846958710281"        # adset "41" (ACTIVE, $400/day)
CONNECTION_ID = "aa0e3d4d-9880-4ffc-b796-5e0a80227c39"
PAGE_ID       = "451791144678410"           # "Justice Covered"
CTA_TYPE      = "LEARN_MORE"
LANDING_URL   = "https://depop.justicecovered.com/"

def bulk_body(confirm=False):
    # /launches/bulk: ad_grouping = list of ad-id groups; each group -> one duplicated adset.
    # Both Bad Luck ads go into ONE new adset "42" -> single group.
    # use_create_from_source=True clones adset 41's full targeting/optimization via Meta
    # (so we do NOT hand-specify targeting; it mirrors 41 exactly). daily_budget in DOLLARS (max 300).
    # utm_template OMITTED -> API default {{ }} template + am_mb={{media_buyer_code}} applies.
    b = {
        "ad_grouping": [AD_IDS],
        "source_adset_id": SOURCE_ADSET,
        "ad_account_id": AD_ACCOUNT_ID,
        "campaign_id": CAMPAIGN_ID,
        "page_id": PAGE_ID,
        "cta_type": CTA_TYPE,
        "landing_url": LANDING_URL,
        "connection_id": CONNECTION_ID,
        "daily_budget": 100,
        "adset_names": ["42"],
        "use_create_from_source": True,
    }
    if confirm:
        b["confirm"] = True
    return b

def validate():
    # Core-object validation (page/campaign/source-adset/token) via /launches/validate.
    vb = {
        "ad_ids": AD_IDS, "ad_set_mode": "duplicate", "use_create_from_source": True,
        "source_adset_id": SOURCE_ADSET, "campaign_id": CAMPAIGN_ID, "ad_account_id": AD_ACCOUNT_ID,
        "connection_id": CONNECTION_ID, "page_id": PAGE_ID, "cta_type": CTA_TYPE,
        "landing_url": LANDING_URL, "daily_budget": 100,
        "new_adset_params": {
            "name": "42", "daily_budget": 100, "billing_event": "IMPRESSIONS",
            "optimization_goal": "OFFSITE_CONVERSIONS", "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
            "promoted_object": {"pixel_id": "847793330973723", "custom_event_type": "LEAD", "smart_pse_enabled": False},
            "attribution_spec": [{"event_type": "CLICK_THROUGH", "window_days": 7}],
            "targeting": {
                "age_max": 65, "age_min": 30,
                "excluded_geo_locations": {"regions": [{"key": "3847", "name": "California", "country": "US"}],
                                           "location_types": ["home", "recent"]},
                "genders": [2], "geo_locations": {"countries": ["US"], "location_types": ["home", "recent"]},
                "brand_safety_content_filter_levels": ["FACEBOOK_RELAXED"],
                "targeting_automation": {"advantage_audience": 0, "individual_setting": {"age": 0, "gender": 0}},
                "publisher_platforms": ["facebook", "instagram", "messenger"],
                "facebook_positions": ["feed", "right_hand_column", "instream_video", "marketplace",
                                       "story", "search", "facebook_reels"],
                "instagram_positions": ["stream", "story", "explore", "reels", "profile_feed", "ig_search"],
                "device_platforms": ["mobile", "desktop"], "messenger_positions": ["story"],
            },
        },
    }
    r = _post("/launches/validate", json=vb)
    ok = r.get("passed")
    print(f"VALIDATE passed={ok}")
    for c in r.get("checks", []):
        if not c.get("passed"):
            print("  FAIL", c["check"], "-", c["message"])
    return ok

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--go", action="store_true", help="LAUNCH for real (spends money)")
    a = ap.parse_args()
    if not validate():
        print("\nValidation FAILED — not launching.")
        sys.exit(1)
    print("\nAll checks passed.")
    if not a.go:
        print("Validate-only. Re-run with --go to launch (real spend).")
        return
    print("\n⚠ LAUNCHING via /launches/bulk (real spend) ...")
    r = _post("/launches/bulk", json=bulk_body(confirm=True), idem_key="launch-badluck-adset42")
    print(json.dumps(r, indent=2)[:4000])

if __name__ == "__main__":
    main()
