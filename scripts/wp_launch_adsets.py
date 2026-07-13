"""Launch the 6 women's-prison interview drafts into YJE-23 / WPA - Latina - HJ P1 as 3 NEW adsets
(2 ads each), duplicating the '5 - 54yr latina- 20-64 b300' targeting but with NO bid cap and
$100/day. Everything lands PAUSED (AdMachin launch always lands paused — no spend until activated
in Meta). Full default JusticeCovered UTM appended to landing_url. Resumable state file.

Reads staged draft ids from outputs/wp_stage6_state.json (must exist).
"""
import os, json, pathlib, requests, sys
from dotenv import load_dotenv
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from admachin_utm import default_landing_url, WOMENS_PRISON_BASE
load_dotenv()

PAT = os.environ["ADMACHIN_PAT"]
BASE = os.getenv("ADMACHIN_API_BASE", "https://admachin.com").rstrip("/") + "/api/v1"
ACCT = "act_885970616544640"                       # YJE-23
CAMP = "120242151877070281"                        # WPA - Latina - HJ P1 (ACTIVE)
SRC_ADSET = "120248405890960281"                   # 5 - 54yr latina- 20-64 b300
PAGE = "451791144678410"
PIXEL = "1345276490863660"
LANDING = default_landing_url(WOMENS_PRISON_BASE)  # full {{ }} default UTM
DAILY_BUDGET = 100                                 # dollars/day (endpoint is $, $300 cap)
STAGE = json.load(open("outputs/wp_stage6_state.json"))
STATE_P = pathlib.Path("outputs/wp_launch_state_v2.json")   # v2 = corrected manual-placement run
KEY = "wpl2"                                                # fresh idempotency namespace

# MANUAL placements, Audience Network OFF (verified accepted by the create endpoint 2026-07-12).
# Setting these EXPLICITLY is what keeps Audience Network off — dropping the block flips the adset
# to Advantage+ automatic (which includes Audience Network). The endpoint rejects the source's
# newer edge positions (threads/biz_disco_feed/facebook_reels_overlay/profile_feed/notification/
# explore_home/ig_search), so those are omitted; the platform selection (no audience_network) holds.
MANUAL_PLACEMENTS = {
    "publisher_platforms": ["facebook", "instagram", "messenger"],   # NO audience_network
    "device_platforms": ["mobile", "desktop"],
    "facebook_positions": ["feed", "right_hand_column", "instream_video", "marketplace",
                            "story", "search", "facebook_reels"],
    "instagram_positions": ["stream", "story", "reels"],
    "messenger_positions": ["story"],
}

# adset name -> [staged slugs] (2 unique scripts each). 45/46/47 so they don't collide with the
# earlier (wrong, Advantage+) 42/43/44 adsets, which must be deleted in Meta UI.
ADSETS = [
    ("45 - interview street - 20-64",   ["voxpop-didyouknow", "niceone"]),
    ("46 - interview reframe - 20-64",  ["omni-500women", "relationship"]),
    ("47 - interview personal - 20-64", ["moved", "kids"]),
]

import time
def hdr(idem=None):
    h = {"Authorization": f"Bearer {PAT}", "Content-Type": "application/json"}
    if idem: h["Idempotency-Key"] = idem
    return h
def _req(method, url, *, params=None, json_body=None, idem=None, tries=8):
    """Robust JSON request — the API gateway intermittently serves the SPA (HTML) on 200; retry
    until we get JSON. POSTs carry an Idempotency-Key so a retry dedups instead of double-creating."""
    last = None
    for attempt in range(tries):
        r = requests.request(method, url, headers=hdr(idem), params=params, json=json_body, timeout=120)
        ct = r.headers.get("content-type", "")
        if "application/json" in ct and r.text.strip():
            return r.status_code, r.json()
        last = f"status {r.status_code} ct={ct[:24]} body={r.text[:80]!r}"
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"{method} {url} never returned JSON: {last}")
def gr(path, fields):
    _, d = _req("GET", f"{BASE}/fb/graph-read", params={"path": path, "fields": fields})
    return d["data"]
def load(): return json.loads(STATE_P.read_text()) if STATE_P.exists() else {}
def save(s): STATE_P.write_text(json.dumps(s, indent=2))

def main():
    state = load()
    src = gr(f"/{SRC_ADSET}", "targeting,promoted_object,attribution_spec,billing_event,optimization_goal,pacing_type")
    # Duplicate the AUDIENCE (geo/age/gender/etc.) from source, but SET placements explicitly to the
    # verified manual set (Audience Network OFF). Removing the source's newer edge positions is fine;
    # the platform selection is what matters and it keeps Audience Network off.
    tg = src["targeting"]
    for k in ("publisher_platforms", "device_platforms", "threads_positions",
              "facebook_positions", "instagram_positions", "messenger_positions"):
        tg.pop(k, None)
    tg.update(MANUAL_PLACEMENTS)
    for name, slugs in ADSETS:
        st = state.setdefault(name, {})
        # 1. create the adset (PAUSED, no bid cap, $100/day) — duplicate targeting
        if "adset_id" not in st:
            ap = {
                "name": name,
                "daily_budget": DAILY_BUDGET,
                "billing_event": src["billing_event"],
                "optimization_goal": src["optimization_goal"],
                "bid_strategy": "LOWEST_COST_WITHOUT_CAP",       # <- no $300 cap
                "targeting": src["targeting"],
                "promoted_object": src["promoted_object"],
                "pacing_type": src.get("pacing_type", ["standard"]),
            }
            body = {"confirm": True, "ad_account_id": ACCT, "campaign_id": CAMP, "adset_params": ap}
            code, resp = _req("POST", f"{BASE}/fb/adsets", json_body=body, idem=f"{KEY}-adset-{name}")
            if code >= 300:
                print(f"[{name}] ADSET FAIL {code}: {resp}"); return
            d = resp.get("data", resp)
            st["adset_id"] = d.get("id") or d.get("adset_id") or d.get("fb_adset_id"); save(state)
            print(f"[{name}] adset {st['adset_id']} created (PAUSED)")
        # 2. launch its 2 ads (land PAUSED) with full-UTM landing_url
        st.setdefault("launched", {})
        for slug in slugs:
            if slug in st["launched"]:
                print(f"  [{slug}] already launched -> {st['launched'][slug]}"); continue
            ad_id = STAGE[slug]["ad_id"]
            body = {"confirm": True, "ad_id": ad_id, "ad_account_id": ACCT, "campaign_id": CAMP,
                    "adset_id": st["adset_id"], "page_id": PAGE, "cta_type": "LEARN_MORE",
                    "landing_url": LANDING, "pixel_id": PIXEL, "event_type": "LEAD"}
            code, resp = _req("POST", f"{BASE}/launches", json_body=body, idem=f"{KEY}-launch-{slug}")
            if code >= 300:
                print(f"  [{slug}] LAUNCH FAIL {code}: {resp}"); return
            d = resp.get("data", resp)
            st["launched"][slug] = d.get("id") or d.get("fb_ad_id"); save(state)
            print(f"  [{slug}] launched (PAUSED) -> {st['launched'][slug]}")
    print("\nLAUNCH COMPLETE — 3 adsets, 6 ads, ALL PAUSED. Activate in Meta when ready.")

if __name__ == "__main__":
    main()
