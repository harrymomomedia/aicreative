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
BASE = os.environ.get("ADMACHIN_API_BASE", "https://admachin.com/api/v1")
ACCT = "act_885970616544640"                       # YJE-23
CAMP = "120242151877070281"                        # WPA - Latina - HJ P1 (ACTIVE)
SRC_ADSET = "120248405890960281"                   # 5 - 54yr latina- 20-64 b300
PAGE = "451791144678410"
PIXEL = "1345276490863660"
LANDING = default_landing_url(WOMENS_PRISON_BASE)  # full {{ }} default UTM
DAILY_BUDGET = 100                                 # dollars/day (endpoint is $, $300 cap)
STAGE = json.load(open("outputs/wp_stage6_state.json"))
STATE_P = pathlib.Path("outputs/wp_launch_state.json")

# adset name -> [staged slugs] (2 unique scripts each)
ADSETS = [
    ("42 - interview street - 20-64",   ["voxpop-didyouknow", "niceone"]),
    ("43 - interview reframe - 20-64",  ["omni-500women", "relationship"]),
    ("44 - interview personal - 20-64", ["moved", "kids"]),
]

def hdr(idem=None):
    h = {"Authorization": f"Bearer {PAT}", "Content-Type": "application/json"}
    if idem: h["Idempotency-Key"] = idem
    return h
def gr(path, fields):
    r = requests.get(f"{BASE}/fb/graph-read", headers=hdr(), params={"path": path, "fields": fields}, timeout=30)
    r.raise_for_status(); return r.json()["data"]
def load(): return json.loads(STATE_P.read_text()) if STATE_P.exists() else {}
def save(s): STATE_P.write_text(json.dumps(s, indent=2))

def main():
    state = load()
    src = gr(f"/{SRC_ADSET}", "targeting,promoted_object,attribution_spec,billing_event,optimization_goal,pacing_type")
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
                "attribution_spec": src["attribution_spec"],
                "pacing_type": src.get("pacing_type", ["standard"]),
            }
            body = {"confirm": True, "ad_account_id": ACCT, "campaign_id": CAMP, "adset_params": ap}
            r = requests.post(f"{BASE}/fb/adsets", headers=hdr(f"wpl-adset-{name}"), json=body, timeout=120)
            if r.status_code >= 300:
                print(f"[{name}] ADSET FAIL {r.status_code}: {r.text[:300]}"); return
            d = r.json().get("data", r.json())
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
            r = requests.post(f"{BASE}/launches", headers=hdr(f"wpl-launch-{slug}"), json=body, timeout=180)
            if r.status_code >= 300:
                print(f"  [{slug}] LAUNCH FAIL {r.status_code}: {r.text[:300]}"); return
            d = r.json().get("data", r.json())
            st["launched"][slug] = d.get("id") or d.get("fb_ad_id"); save(state)
            print(f"  [{slug}] launched (PAUSED) -> {st['launched'][slug]}")
    print("\nLAUNCH COMPLETE — 3 adsets, 6 ads, ALL PAUSED. Activate in Meta when ready.")

if __name__ == "__main__":
    main()
