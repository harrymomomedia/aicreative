"""Poyo.ai client — Veo 3.1 Fast at $0.10/clip flat (cheaper than KIE for Veo3).

Endpoint:  POST https://api.poyo.ai/api/generate/submit  → returns {data.task_id}
Polling:   GET  https://api.poyo.ai/api/generate/status/{task_id}
              status: not_started | running | finished | failed
              files: [{file_url, file_type}]   (when finished)

Models (8s fixed duration):
  veo3.1-fast     — fast, supports text-to-video AND image-to-video
  veo3.1-lite     — text-to-video ONLY (no image_urls)
  veo3.1-quality  — high quality, supports image-to-video, NO reference mode

generation_type (image-to-video):
  frame      — first image = start frame, second image (optional) = end frame
  reference  — up to 3 images as style/subject reference (NOT supported by quality)
  (omit to let Poyo infer from image count)
"""
import os, time, requests, pathlib
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("POYO_API_KEY")
if not KEY:
    raise RuntimeError("POYO_API_KEY not set in .env")

BASE = "https://api.poyo.ai/api"
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}


def _poll(task_id, label="Poyo", interval=5, timeout=600):
    """Poll status endpoint until finished or failed. Returns the data dict."""
    t0 = time.time()
    while True:
        if time.time() - t0 > timeout:
            raise TimeoutError(f"{label} task {task_id} timed out after {timeout}s")
        r = requests.get(f"{BASE}/generate/status/{task_id}", headers=HEADERS)
        body = r.json()
        data = body.get("data") or {}
        status = data.get("status")
        progress = data.get("progress", 0)
        if status == "finished":
            return data
        if status == "failed":
            raise RuntimeError(f"{label} task {task_id} failed: {data.get('error_message')}")
        print(f"  {label} {task_id[:30]}… {status} ({progress}%)", flush=True)
        time.sleep(interval)


def generate_veo(
    prompt,
    image_urls=None,
    aspect_ratio="9:16",
    resolution="720p",
    model="veo3.1-fast",
    generation_type=None,
):
    """Generate a Veo 3.1 video on Poyo. Returns {status, urls, raw}.

    aspect_ratio: '16:9' | '9:16'
    resolution:   '720p' | '1080p' | '4k'
    generation_type: 'frame' | 'reference' | None (auto)
    """
    inp = {
        "prompt": prompt,
        "duration": 8,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
    }
    if image_urls:
        inp["image_urls"] = image_urls
    if generation_type:
        inp["generation_type"] = generation_type
    payload = {"model": model, "input": inp}

    r = requests.post(f"{BASE}/generate/submit", headers=HEADERS, json=payload)
    body = r.json()
    if r.status_code != 200 or body.get("code") != 200:
        return {"status": "failed", "urls": [], "raw": body}
    task_id = (body.get("data") or {}).get("task_id")
    if not task_id:
        return {"status": "failed", "urls": [], "raw": body}
    print(f"  Poyo taskId: {task_id}", flush=True)

    data = _poll(task_id, label=f"Poyo[{model}]")
    urls = [f.get("file_url") for f in data.get("files", []) if f.get("file_url")]
    return {"status": "success" if urls else "failed", "urls": urls, "raw": data}


def download(url, dest):
    """Stream-download a URL to dest path."""
    pathlib.Path(dest).parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=1 << 16):
            f.write(chunk)
    print(f"  Saved: {dest} ({pathlib.Path(dest).stat().st_size // 1024}KB)", flush=True)
    return dest
