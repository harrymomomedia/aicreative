"""OpenRouter video generation client.

Async pattern:
  POST /api/v1/videos  → 202 + {id, polling_url, status: "pending"}
  GET  /api/v1/videos/{id}  → poll until status terminal
  Download from the returned video URL when status == "completed"

Models we care about (per /api/v1/videos/models):
  bytedance/seedance-2.0-fast   — 480p/720p, 9:16 supported, 4-15s, first/last frame
  bytedance/seedance-2.0        — adds 1080p
  bytedance/seedance-1-5-pro    — cheapest token rate, 1080p
  kwaivgi/kling-v3.0-std/pro    — alt video models
  google/veo-3.1                — Veo via OpenRouter

Pricing (Seedance 2.0 Fast): $0.0000056 per video token; tokens = (h × w × dur × 24) / 1024.
e.g. 480×854 × 8s = ~$4.40/clip — pricier than KIE's $0.36-0.80 but matches user routing preference.
"""
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("OPENROUTER_API_KEY")
if not KEY:
    raise RuntimeError("OPENROUTER_API_KEY not set in .env")

BASE = "https://openrouter.ai/api/v1"
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

TERMINAL_STATES = {"completed", "succeeded", "failed", "cancelled", "error"}


def _poll(polling_url, label="Video", interval=5, timeout=900):
    """Poll status endpoint until terminal. Returns the final data dict."""
    t0 = time.time()
    while True:
        if time.time() - t0 > timeout:
            raise TimeoutError(f"{label} polling timed out after {timeout}s ({polling_url})")
        r = requests.get(polling_url, headers={"Authorization": f"Bearer {KEY}"})
        body = r.json()
        status = body.get("status")
        if status in TERMINAL_STATES:
            return body
        print(f"  {label} {body.get('id','?')[:20]}… {status}", flush=True)
        time.sleep(interval)


def generate_video(
    prompt,
    model="bytedance/seedance-2.0-fast",
    image_urls=None,
    last_frame_url=None,
    aspect_ratio="9:16",
    resolution="480p",
    size=None,
    duration=5,
    generate_audio=True,
    seed=None,
    provider=None,
    timeout=900,
):
    """Submit a video generation job and poll until terminal. Returns {status, urls, raw}.

    image_urls:      list of hosted URLs (single-image → first_frame; pass 1 URL)
                     or pass first/last via image_urls[0]=first, last_frame_url=last
    aspect_ratio:    '9:16' | '16:9' | '1:1' | etc.
    resolution:      '480p' | '720p' | '1080p'
    size:            optional explicit 'WxH' (e.g. '480x854') — overrides aspect_ratio+resolution
    duration:        int seconds (Seedance Fast: 4-15)
    generate_audio:  True for Seedance native audio
    """
    body = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "generate_audio": generate_audio,
    }
    if size:
        body["size"] = size
    else:
        body["aspect_ratio"] = aspect_ratio
        body["resolution"] = resolution
    if seed is not None:
        body["seed"] = seed
    if provider:
        body["provider"] = provider

    frame_images = []
    if image_urls:
        # first_frame
        frame_images.append({
            "image_url": {"url": image_urls[0]},
            "type": "image_url",
            "frame_type": "first_frame",
        })
    if last_frame_url:
        frame_images.append({
            "image_url": {"url": last_frame_url},
            "type": "image_url",
            "frame_type": "last_frame",
        })
    if frame_images:
        body["frame_images"] = frame_images

    r = requests.post(f"{BASE}/videos", headers=HEADERS, json=body)
    if r.status_code not in (200, 202):
        return {"status": "failed", "urls": [], "raw": r.json() if r.headers.get("Content-Type", "").startswith("application/json") else r.text}
    body = r.json()
    polling_url = body.get("polling_url")
    if not polling_url:
        return {"status": "failed", "urls": [], "raw": body}
    print(f"  OpenRouter[{model}] taskId: {body.get('id')}", flush=True)

    final = _poll(polling_url, label=f"OR[{model.split('/')[-1]}]", timeout=timeout)
    status = final.get("status")
    if status != "completed":
        return {"status": "failed", "urls": [], "raw": final}

    # OpenRouter returns the video URLs in `unsigned_urls` (auth-required GET)
    urls = []
    if isinstance(final.get("unsigned_urls"), list):
        urls = [u for u in final["unsigned_urls"] if isinstance(u, str)]
    # Fallback patterns (defensive — older responses)
    if not urls:
        if isinstance(final.get("video"), dict) and final["video"].get("url"):
            urls.append(final["video"]["url"])
        elif isinstance(final.get("video_url"), str):
            urls.append(final["video_url"])
        elif isinstance(final.get("url"), str):
            urls.append(final["url"])

    return {"status": "success" if urls else "failed", "urls": urls, "raw": final}


def download(url, dest):
    """Stream-download a URL to dest path."""
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, stream=True, headers={"Authorization": f"Bearer {KEY}"})
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=1 << 16):
            f.write(chunk)
    print(f"  Saved: {dest} ({Path(dest).stat().st_size // 1024}KB)", flush=True)
    return dest
