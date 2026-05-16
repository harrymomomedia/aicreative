"""
useapi.net — RunwayML API v1

All video generation routes through one endpoint:
  POST https://api.useapi.net/v1/runwayml/videos/create

Polling:
  GET  https://api.useapi.net/v1/runwayml/tasks/{taskId}

Asset upload (images/video/audio used as references):
  POST https://api.useapi.net/v1/runwayml/assets/?name={name}
  Body: raw binary, Content-Type must match file type.
  Returns: { assetId, id, url, ... }

Supported models (exact IDs):
  seedance-2            Seedance 2.0, 4–15s, up to 11 image refs + 3 video refs
  kling-3.0-pro         Kling 3.0 Pro, 5/10/15s fixed steps
  kling-3.0-standard    Kling 3.0 Standard, 5/10/15s fixed steps
  kling-3.0-motion-control  Character animation (needs char image + perf video)
  kling-o3-pro          Kling O3 Pro
  kling-o3-standard     Kling O3 Standard
  kling-o3-4k           Kling O3 4K
  kling-2.6-pro         Kling 2.6 Pro
  kling-2.6-i2v         Kling 2.6 Image-to-Video
  gen4.5                Runway Gen-4.5, 2–10s
  gen4                  Runway Gen-4, 2–10s
  gen4-turbo            Runway Gen-4 Turbo, 2–10s
  veo-3.1               Veo 3.1, 4/6/8s — exploreMode NOT supported
  sora-2                Sora 2
  sora-2-pro            Sora 2 Pro
  wan-2.6-flash         Wan 2.6 Flash
  wan-2.2-animate       Wan 2.2 Animate
  happyhorse-1.0        HappyHorse 1.0

exploreMode=True (default) — Unlimited plan: skips credit deduction, lower priority queue.
  ~10 min total for Seedance/Gen-4.5 in explore (7-9 min queue + 1.5-4 min render).
  Gen-4 Turbo: ~1-2 min even in explore.
  NOT supported by veo-3.1.
Set USEAPI_EXPLORE=false in .env to use credits / higher priority queue.
"""
import mimetypes
import os
import pathlib
import time

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("USEAPI_TOKEN")
if not TOKEN:
    raise RuntimeError("USEAPI_TOKEN not set in .env")

_EXPLORE = os.getenv("USEAPI_EXPLORE", "true").lower() not in ("false", "0", "no")

BASE = "https://api.useapi.net/v1/runwayml"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

POLL_INTERVAL = 15
THROTTLE_WAIT = 30


# ─── Asset upload ─────────────────────────────────────────────────────

def upload_asset(source, name=None):
    """Upload a local file as a Runway asset. Returns assetId string.

    source: local file path (str or Path). Remote URLs are not accepted by this endpoint.
    name:   asset name sent to the API (defaults to filename).
    """
    source = pathlib.Path(source)
    asset_name = name or source.name
    mime = mimetypes.guess_type(str(source))[0] or "application/octet-stream"

    with open(source, "rb") as f:
        data = f.read()

    r = requests.post(
        f"{BASE}/assets/",
        params={"name": asset_name},
        headers={**HEADERS, "Content-Type": mime},
        data=data,
    )
    body = r.json()
    asset_id = body.get("assetId") or body.get("id")
    if not asset_id:
        raise RuntimeError(f"Asset upload failed: {body}")
    print(f"  Asset uploaded: {asset_id} ({source.name})", flush=True)
    return asset_id


# ─── Shared submit / poll ─────────────────────────────────────────────

def _poll(task_id, label="useapi", timeout=900):
    """Poll GET /tasks/{taskId} until SUCCEEDED or FAILED."""
    t0 = time.time()
    while True:
        if time.time() - t0 > timeout:
            raise TimeoutError(f"{label} task {task_id} timed out after {timeout}s")
        time.sleep(POLL_INTERVAL)
        r = requests.get(f"{BASE}/tasks/{task_id}", headers=HEADERS)
        body = r.json()
        # Response may be wrapped in a "task" key
        task = body.get("task") or body
        status = task.get("status", "?")
        progress = float(task.get("progressRatio") or 0)
        eta = task.get("estimatedTimeToStartSeconds")
        eta_str = f" eta={eta}s" if eta else ""
        print(f"  {time.strftime('%H:%M:%S')} {label} … {status} ({int(progress*100)}%){eta_str}", flush=True)
        if status == "SUCCEEDED":
            urls = [a["url"] for a in task.get("artifacts", []) if a.get("url")]
            return {"status": "success", "urls": urls, "raw": task}
        if status == "FAILED":
            return {"status": "failed", "urls": [], "failMsg": task.get("error", ""), "raw": task}


def _submit(payload, label, explore=None):
    """POST /videos/create, return poll result. explore defaults to module-level _EXPLORE."""
    if explore is None:
        explore = _EXPLORE
    payload["exploreMode"] = explore

    r = requests.post(f"{BASE}/videos/create", headers={**HEADERS, "Content-Type": "application/json"}, json=payload)
    if r.status_code == 429:
        raise RuntimeError(f"{label}: rate limited (429) — reduce concurrency or wait.")
    if r.status_code == 412:
        raise RuntimeError(f"{label}: insufficient credits (412).")
    body = r.json()
    # taskId is inside body.task on success
    task = body.get("task") or body
    task_id = task.get("taskId") or task.get("id")
    if not task_id:
        raise RuntimeError(f"{label} create failed ({r.status_code}): {body}")
    print(f"  {label} taskId: {task_id}", flush=True)
    return _poll(task_id, label=label)


# ─── Seedance ────────────────────────────────────────────────────────

def generate_seedance(
    prompt,
    duration=10,
    aspect_ratio="9:16",
    resolution="720p",
    audio=True,
    # Image references (upload local files before calling, or pass already-uploaded assetIds)
    image_asset_ids=None,    # list of assetIds — up to 11 style/subject refs
    start_frame_asset_id=None,  # assetId — literal first frame (i2v anchor)
    end_frame_asset_id=None,    # assetId — literal end frame (frame transition)
    # Convenience: local paths auto-uploaded
    start_frame_path=None,
    end_frame_path=None,
    image_paths=None,
    model="seedance-2",
    explore=None,
):
    """Seedance 2.0 via useapi.net RunwayML. Returns {status, urls, raw}.

    For the clip-1 anchor pattern:
      pass start_frame_path=<local jpg>  → auto-uploaded, used as startFrameAssetId.

    For style/subject refs:
      pass image_paths=[...] → each auto-uploaded as imageAssetId1…N (up to 11).
    """
    # Auto-upload convenience paths
    if start_frame_path and not start_frame_asset_id:
        start_frame_asset_id = upload_asset(start_frame_path)
    if end_frame_path and not end_frame_asset_id:
        end_frame_asset_id = upload_asset(end_frame_path)
    if image_paths and not image_asset_ids:
        image_asset_ids = [upload_asset(p) for p in image_paths[:11]]

    payload = {
        "model": model,
        "text_prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "audio": audio,
    }
    if start_frame_asset_id:
        payload["startFrameAssetId"] = start_frame_asset_id
    if end_frame_asset_id:
        payload["endFrameAssetId"] = end_frame_asset_id
    if image_asset_ids:
        for i, aid in enumerate(image_asset_ids[:11], start=1):
            payload[f"imageAssetId{i}"] = aid

    return _submit(payload, label="Seedance", explore=explore)


# ─── Kling ───────────────────────────────────────────────────────────

def generate_kling(
    prompt,
    duration=5,          # Kling 3.0 accepts 5, 10, or 15 only
    aspect_ratio="9:16",
    audio=True,
    image_asset_ids=None,        # list of assetIds
    start_frame_asset_id=None,
    end_frame_asset_id=None,
    start_frame_path=None,
    end_frame_path=None,
    image_paths=None,
    model="kling-3.0-standard",  # or kling-3.0-pro / kling-o3-pro / kling-2.6-pro
    explore=None,
):
    """Kling 3.0 / O3 / 2.6 via useapi.net RunwayML. Returns {status, urls, raw}.

    duration for Kling 3.0: must be 5, 10, or 15 (fixed steps, not free range).
    model options:
      kling-3.0-standard  (default)
      kling-3.0-pro
      kling-o3-standard / kling-o3-pro / kling-o3-4k
      kling-2.6-pro / kling-2.6-i2v
    """
    if start_frame_path and not start_frame_asset_id:
        start_frame_asset_id = upload_asset(start_frame_path)
    if end_frame_path and not end_frame_asset_id:
        end_frame_asset_id = upload_asset(end_frame_path)
    if image_paths and not image_asset_ids:
        image_asset_ids = [upload_asset(p) for p in image_paths[:11]]

    payload = {
        "model": model,
        "text_prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "audio": audio,
    }
    if start_frame_asset_id:
        payload["startFrameAssetId"] = start_frame_asset_id
    if end_frame_asset_id:
        payload["endFrameAssetId"] = end_frame_asset_id
    if image_asset_ids:
        for i, aid in enumerate(image_asset_ids[:11], start=1):
            payload[f"imageAssetId{i}"] = aid

    return _submit(payload, label=f"Kling[{model}]", explore=explore)


# ─── Runway Gen-4 ────────────────────────────────────────────────────

def generate_runway(
    prompt,
    duration=8,
    aspect_ratio="9:16",
    audio=True,
    seed=None,
    image_asset_ids=None,
    start_frame_asset_id=None,
    end_frame_asset_id=None,
    start_frame_path=None,
    end_frame_path=None,
    image_paths=None,
    model="gen4-turbo",   # or gen4 / gen4.5
    explore=None,
):
    """Runway Gen-4 / Gen-4 Turbo / Gen-4.5 via useapi.net. Returns {status, urls, raw}.

    duration: 2–10s for Gen-4 series.
    seed: int 1–4294967294 (Gen-4 series only).
    """
    if start_frame_path and not start_frame_asset_id:
        start_frame_asset_id = upload_asset(start_frame_path)
    if end_frame_path and not end_frame_asset_id:
        end_frame_asset_id = upload_asset(end_frame_path)
    if image_paths and not image_asset_ids:
        image_asset_ids = [upload_asset(p) for p in image_paths[:3]]

    payload = {
        "model": model,
        "text_prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "audio": audio,
    }
    if seed is not None:
        payload["seed"] = seed
    if start_frame_asset_id:
        payload["startFrameAssetId"] = start_frame_asset_id
    if end_frame_asset_id:
        payload["endFrameAssetId"] = end_frame_asset_id
    if image_asset_ids:
        for i, aid in enumerate(image_asset_ids[:3], start=1):
            payload[f"imageAssetId{i}"] = aid

    return _submit(payload, label=f"Runway[{model}]", explore=explore)


# ─── Download ────────────────────────────────────────────────────────

def download(url, dest):
    """Stream-download a video URL to dest path."""
    pathlib.Path(dest).parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=1 << 16):
            f.write(chunk)
    print(f"  Saved: {dest} ({pathlib.Path(dest).stat().st_size // 1024}KB)", flush=True)
    return dest
