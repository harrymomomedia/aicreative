"""useapi.net google-flow client — FREE no-credit Veo 3.1 Lite (ultra-low-priority).

Model `veo-3.1-lite-low-priority` = free, no credit, ultra-low-priority queue (SLOW).
i2v persona lock via `startImage` (single first-frame). Preferred Veo Lite path; see
`feedback_veo_lite_free_path` memory + scripts/podcast_omni_produce.py (the original impl).

  from googleflow_client import upload_asset, generate_veo
  mgid = upload_asset("anchor.png")
  r = generate_veo("<prompt>", image_mgid=mgid, duration=8, seed=42)
  # r = {"status":"success"|"failed", "urls":[...], "raw":{...}}
"""
import os, time, requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

TOKEN = os.environ.get("USEAPI_TOKEN", "")
EMAIL = os.environ.get("GOOGLEFLOW_EMAIL", "flowmomomedia@gmail.com")
H = {"Authorization": f"Bearer {TOKEN}"}
BASE = "https://api.useapi.net/v1/google-flow"
MODEL = "veo-3.1-lite-low-priority"


def upload_asset(path, ctype="image/png"):
    """Upload a local image, return its mediaGenerationId (mgid)."""
    with open(path, "rb") as f:
        r = requests.post(f"{BASE}/assets/{requests.utils.quote(EMAIL)}",
                          headers={**H, "Content-Type": ctype}, data=f.read(), timeout=180)
    r.raise_for_status()
    m = r.json().get("mediaGenerationId")
    return m.get("mediaGenerationId") if isinstance(m, dict) else m


def generate_veo(prompt, image_path=None, image_mgid=None, duration=8, seed=None,
                 aspect_ratio="portrait", model=MODEL, attempts=3, ref_param="startImage"):
    """Generate one Veo clip on the free google-flow low-priority tier.

    Provide either image_path (auto-uploaded) or image_mgid for the i2v first-frame lock.
    duration must be 4/6/8. Returns {"status","urls","raw"}.
    """
    if image_mgid is None and image_path:
        image_mgid = upload_asset(image_path)
    last = None
    for a in range(1, attempts + 1):
        payload = {"prompt": prompt, "model": model,
                   "duration": duration, "count": 1,
                   # DATA-DRIVEN order (GET /accounts/captcha-stats, 2026-07-08, n=10k):
                   # CapSolver 39.6% > YesCaptcha 33.5% > AntiCaptcha 23.8%; UserProvided 93.4%
                   # (captchaToken is the escalation path). Repeats allowed (max 10); zero-balance
                   # providers ABORT the attempt so SolveCaptcha is excluded. String, not array;
                   # mutually exclusive with captchaRetry.
                   "captchaOrder": "CapSolver,YesCaptcha,AntiCaptcha,CapSolver,YesCaptcha,AntiCaptcha,CapSolver,YesCaptcha,CapSolver,YesCaptcha",
                   "seed": (seed if seed is not None else (abs(hash(prompt)) % 9000)) + a * 31}
        if aspect_ratio:  # omit to let I2V inherit the input image's aspect (free tier can't OVERRIDE aspect)
            payload["aspectRatio"] = aspect_ratio
        if image_mgid:
            payload[ref_param] = image_mgid
        try:
            g = requests.post(f"{BASE}/videos", headers={**H, "Content-Type": "application/json"},
                              json=payload, timeout=900)
            gj = g.json()
            last = gj
            if g.status_code == 200 and gj.get("media"):
                urls = [m["videoUrl"] for m in gj["media"] if m.get("videoUrl")]
                if urls:
                    return {"status": "success", "urls": urls, "raw": gj}
            else:
                try:
                    reason = gj["response"]["media"][0]["mediaMetadata"]["mediaStatus"].get("failureReasons")
                except Exception:
                    reason = str(gj.get("error") or gj)[:120]
                print(f"  [googleflow] attempt {a} failed: {reason}", flush=True)
        except Exception as e:
            last = str(e)
            print(f"  [googleflow] attempt {a} exc: {str(e)[:120]}", flush=True)
        time.sleep(6)
    return {"status": "failed", "urls": [], "raw": last}


def download(url, dest):
    r = requests.get(url, timeout=300); r.raise_for_status()
    with open(dest, "wb") as f:
        f.write(r.content)
    return dest
