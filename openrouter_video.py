"""
OpenRouter Video Generation API

Submit:  POST https://openrouter.ai/api/v1/videos
Poll:    GET  https://openrouter.ai/api/v1/videos/{id}
Models:  GET  https://openrouter.ai/api/v1/videos/models

Useful models and per-second pricing (8s clip cost in parens):
  google/veo-3.1-fast       $0.10/s audio, $0.08/s no-audio  (→ $0.80 / $0.64)
  google/veo-3.1-lite       $0.05/s audio, $0.03/s no-audio  (→ $0.40 / $0.24)  ← cheapest Veo
  google/veo-3.1            $0.40/s audio  (→ $3.20) — quality tier
  bytedance/seedance-2.0-fast  ~$0.053/clip at 480p 10s (token-based) ← pay-per-use option
  kwaivgi/kling-v3.0-std    $0.084/s  — use useapi unlimited instead
  openai/sora-2-pro         $0.30–0.50/s

Primary use case here: google/veo-3.1-lite as a cheaper Veo alternative to Poyo.
  Poyo veo3.1-fast = $0.10 flat per 8s clip.
  OR veo-3.1-lite (no audio) = $0.24 per 8s clip → more expensive but different model tier.
  OR veo-3.1-lite (with audio) = $0.40 per 8s clip.
  → Keep Poyo as default Veo. Use OpenRouter for veo-3.1-lite when Poyo is down/slow.

frame_images field: list of {type, url} dicts.
  type: "first_frame" | "last_frame"
  url: publicly accessible image URL
"""
import os
import time
import requests
import pathlib
from dotenv import load_dotenv

load_dotenv()

# Default to ADCLI key; fall back to main key
TOKEN = os.getenv("OPENROUTER_ADCLI_KEY") or os.getenv("OPENROUTER_API_KEY")
if not TOKEN:
    raise RuntimeError("OPENROUTER_ADCLI_KEY or OPENROUTER_API_KEY not set in .env")

BASE = "https://openrouter.ai/api/v1"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

POLL_INTERVAL = 10


# ─── Poller ──────────────────────────────────────────────────────────

def _poll(job_id, label="OR", timeout=600):
    """Poll GET /videos/{id} until completed or failed."""
    t0 = time.time()
    while True:
        if time.time() - t0 > timeout:
            raise TimeoutError(f"{label} job {job_id} timed out after {timeout}s")
        time.sleep(POLL_INTERVAL)
        r = requests.get(f"{BASE}/videos/{job_id}", headers=HEADERS)
        body = r.json()
        status = body.get("status", "?")
        print(f"  {time.strftime('%H:%M:%S')} {label} {job_id[:20]}… {status}", flush=True)
        if status == "completed":
            urls = body.get("unsigned_urls") or []
            return {"status": "success", "urls": urls, "raw": body}
        if status == "failed":
            return {"status": "failed", "urls": [], "failMsg": body.get("error", ""), "raw": body}


def _submit(payload, label):
    r = requests.post(f"{BASE}/videos", headers=HEADERS, json=payload)
    if r.status_code == 429:
        raise RuntimeError(f"{label}: rate limited (429).")
    body = r.json()
    job_id = body.get("id")
    if not job_id:
        raise RuntimeError(f"{label} submit failed ({r.status_code}): {body}")
    print(f"  {label} jobId: {job_id}", flush=True)
    return _poll(job_id, label=label)


# ─── Veo 3.1 ─────────────────────────────────────────────────────────

def generate_veo(
    prompt,
    duration=8,
    resolution="720p",
    aspect_ratio="9:16",
    audio=True,
    first_frame_url=None,   # public image URL for i2v first-frame mode
    last_frame_url=None,
    model="google/veo-3.1-lite",   # cheaper tier; use google/veo-3.1-fast for quality
):
    """Veo 3.1 via OpenRouter. Returns {status, urls, raw}.

    model:
      google/veo-3.1-lite  — cheaper ($0.05/s audio, $0.03/s no-audio at 720p)
      google/veo-3.1-fast  — mid ($0.10/s audio, $0.08/s no-audio at 720p)
      google/veo-3.1       — quality ($0.40/s audio at 720p)

    duration: 4, 6, or 8s only.
    resolution: 720p | 1080p | 4K (4K only on fast/quality, not lite).

    Use Poyo (poyo_client.generate_veo) as the default Veo provider at $0.10/clip flat.
    Use this when Poyo is down or you specifically need veo-3.1-lite.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "generate_audio": audio,
    }
    frames = []
    if first_frame_url:
        frames.append({"type": "first_frame", "url": first_frame_url})
    if last_frame_url:
        frames.append({"type": "last_frame", "url": last_frame_url})
    if frames:
        payload["frame_images"] = frames

    return _submit(payload, label=f"OR[{model.split('/')[-1]}]")


# ─── Seedance (via OpenRouter — pay-per-use fallback) ─────────────────

def generate_seedance(
    prompt,
    duration=10,
    resolution="480p",
    aspect_ratio="9:16",
    audio=True,
    first_frame_url=None,
    last_frame_url=None,
    model="bytedance/seedance-2.0-fast",
):
    """Seedance 2.0 Fast via OpenRouter. ~$0.053/clip at 480p 10s (token-based).

    model: bytedance/seedance-2.0-fast (~$0.053/10s at 480p) | bytedance/seedance-2.0 (720p/1080p, costlier)
    resolution: 480p (default, cheapest) | 720p
    duration: 4–15s.

    Use useapi_client.generate_seedance for unlimited plan (flat monthly).
    Use this for pay-per-use / when useapi is down.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "generate_audio": audio,
    }
    frames = []
    if first_frame_url:
        frames.append({"type": "first_frame", "url": first_frame_url})
    if last_frame_url:
        frames.append({"type": "last_frame", "url": last_frame_url})
    if frames:
        payload["frame_images"] = frames

    return _submit(payload, label=f"OR[{model.split('/')[-1]}]")


# ─── Download ─────────────────────────────────────────────────────────

def download(url, dest):
    pathlib.Path(dest).parent.mkdir(parents=True, exist_ok=True)
    headers = {"Authorization": f"Bearer {TOKEN}"} if "openrouter.ai" in url else None
    r = requests.get(url, stream=True, headers=headers)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=1 << 16):
            f.write(chunk)
    print(f"  Saved: {dest} ({pathlib.Path(dest).stat().st_size // 1024}KB)", flush=True)
    return dest
