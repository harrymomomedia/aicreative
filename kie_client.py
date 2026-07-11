"""
KIE.ai client for the 5 endpoints we use:

Video:
  generate_seedance(prompt, ...)      → bytedance/seedance-2-fast (480p)
  generate_kling(prompt, ...)         → kling-3.0/video (std = 720p)
  generate_veo(prompt, ...)           → veo3_fast (720p) — separate endpoint

Image:
  generate_gpt_image(prompt, ...)     → gpt-image-2-text-to-image / image-to-image
  generate_nano_banana(prompt, ...)   → nano-banana-2

Shared: upload_file, download, next_version.
"""
import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("KIE_API_KEY")
if not API_KEY:
    raise RuntimeError("KIE_API_KEY not set in .env")

BASE = "https://api.kie.ai"
UPLOAD_BASE = "https://kieai.redpandaai.co"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
AUTH_ONLY = {"Authorization": f"Bearer {API_KEY}"}

JOBS_CREATE = f"{BASE}/api/v1/jobs/createTask"
JOBS_POLL = f"{BASE}/api/v1/jobs/recordInfo"
VEO_CREATE = f"{BASE}/api/v1/veo/generate"
VEO_POLL = f"{BASE}/api/v1/veo/record-info"

POLL_INTERVAL = 10


# ─── Shared helpers ──────────────────────────────────────────────────

def upload_imgur(filepath):
    """Upload a local image to Imgur (anonymous, public, no auth needed by fetcher).

    Returns clean URL like https://i.imgur.com/<hash>.png.
    Use as fallback when catbox.moe is having issues.
    Imgur is highly reliable and works for KIE/Poyo Veo image_urls.

    NOTE: uses public Client-ID — has rate limits but fine for low-volume use.
    Register your own at https://api.imgur.com/oauth2/addclient if hitting limits.
    """
    headers = {"Authorization": "Client-ID 546c25a59c58ad7"}
    with open(filepath, "rb") as f:
        files = {"image": f}
        r = requests.post("https://api.imgur.com/3/image", headers=headers, files=files, timeout=60)
    body = r.json()
    if not body.get("success"):
        raise RuntimeError(f"Imgur upload failed: {body}")
    return body["data"]["link"]


def upload_catbox(filepath):
    """Upload a local file to catbox.moe (anonymous, no account, permanent URL).

    Returns clean URL like https://files.catbox.moe/<hash>.<ext>.
    Use this when KIE's own tempfile host is rate-limited (HTTP 429) — Veo's
    fetcher reads catbox URLs reliably without rate-limit issues.
    """
    with open(filepath, "rb") as f:
        files = {"fileToUpload": f}
        data = {"reqtype": "fileupload"}
        r = requests.post("https://catbox.moe/user/api.php", files=files, data=data, timeout=60)
    if r.status_code != 200 or not r.text.startswith("https://"):
        raise RuntimeError(f"Catbox upload failed: {r.status_code} {r.text[:200]}")
    return r.text.strip()


def upload_file(filepath, filetype=None):
    """Upload a local file, return a UNIQUE timestamped URL.

    Uses /api/file-stream-upload which returns a URL with a unique
    timestamp+hash path. This is REQUIRED to bypass Cloudflare per-URL
    rate-limiting on tempfile.redpandaai.co — KIE Veo's fetcher will hit
    HTTP 429 (retry-after 60s) if the same URL is requested too many times.

    Each call to upload_file() returns a NEW unique URL even for the same
    source file, which dodges the rate limit. Re-upload before each Veo
    submission rather than caching the URL across submissions.

    NOTE: file-base64-upload returns STABLE URLs (path-based, same per
    filename) — DO NOT USE for Veo image_urls. The stable URL gets 429'd
    permanently after the first few fetches.
    """
    with open(filepath, "rb") as f:
        files = {"file": (os.path.basename(filepath), f, filetype)} if filetype else {"file": f}
        data = {"uploadPath": "aicreative"}
        r = requests.post(f"{UPLOAD_BASE}/api/file-stream-upload", headers=AUTH_ONLY, files=files, data=data)
    body = r.json()
    url = body.get("data", {}).get("downloadUrl")
    if not url:
        raise RuntimeError(f"Upload failed: {body}")
    return url


def download(url, dest):
    if not url:
        return False
    r = requests.get(url, stream=True)
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"  Saved: {dest} ({os.path.getsize(dest) // 1024}KB)", flush=True)
    return True


def next_version(folder, prefix, ext="mp4"):
    Path(folder).mkdir(parents=True, exist_ok=True)
    existing = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith(f".{ext}")]
    return len(existing) + 1


# ─── Pollers ─────────────────────────────────────────────────────────

def _poll_jobs(task_id, label):
    """Poll the unified /jobs/recordInfo endpoint (Seedance, Kling, GPT Image, Nano Banana)."""
    while True:
        time.sleep(POLL_INTERVAL)
        r = requests.get(JOBS_POLL, headers=HEADERS, params={"taskId": task_id})
        body = r.json().get("data", {})
        state = body.get("state", "?")
        print(f"  {time.strftime('%H:%M:%S')} {label}: {state}", flush=True)
        if state == "success":
            urls = json.loads(body.get("resultJson") or "{}").get("resultUrls", [])
            return {"status": "success", "urls": urls, "raw": body}
        if state == "fail":
            return {"status": "failed", "urls": [], "failMsg": body.get("failMsg", ""), "raw": body}


def _poll_veo(task_id, label):
    """Poll Veo's separate endpoint. successFlag: 0 generating, 1 success, 2/3 failed."""
    while True:
        time.sleep(POLL_INTERVAL)
        r = requests.get(VEO_POLL, headers=HEADERS, params={"taskId": task_id})
        body = r.json().get("data", {})
        flag = body.get("successFlag")
        print(f"  {time.strftime('%H:%M:%S')} {label}: flag={flag}", flush=True)
        if flag == 1:
            resp = body.get("response", {}) or {}
            urls = resp.get("resultUrls") or resp.get("fullResultUrls") or []
            return {"status": "success", "urls": urls, "raw": body}
        if flag in (2, 3):
            return {"status": "failed", "urls": [], "failMsg": body.get("errorMessage", ""), "raw": body}


# ─── Video generators ────────────────────────────────────────────────

def generate_seedance(prompt, duration=10, aspect_ratio="9:16", ref_images=None, ref_videos=None, generate_audio=True):
    """Seedance 2 Fast at 480p. Defaults to vertical 9:16 for UGC."""
    payload_input = {
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "resolution": "480p",
        "generate_audio": generate_audio,
    }
    if ref_images:
        payload_input["reference_image_urls"] = ref_images
    if ref_videos:
        payload_input["reference_video_urls"] = ref_videos
    payload = {"model": "bytedance/seedance-2-fast", "input": payload_input}
    r = requests.post(JOBS_CREATE, headers=HEADERS, json=payload)
    body = r.json()
    task_id = (body.get("data") or {}).get("taskId")
    if not task_id:
        raise RuntimeError(f"Seedance create failed: {body}")
    print(f"  Seedance taskId: {task_id}", flush=True)
    return _poll_jobs(task_id, "Seedance")


def generate_kling(prompt, duration=5, aspect_ratio="9:16", image_urls=None,
                   sound=True, mode="pro", kling_elements=None, multi_shots=False,
                   multi_prompt=None):
    """Kling 3.0 video. duration is a string '3'..'15'.

    mode:           'std' (720p, cheaper) | 'pro' (better quality)
    image_urls:     list of URLs for the scene baseline / first-frame anchor (i2v)
    kling_elements: list of element dicts for the @element_name reference system.
                    Each: {"name": "element_X", "description": "...", "element_input_urls": [url1, url2]}
                    Up to 3 elements per task, 1-4 URLs per element.
                    Prompt references them as @element_X.
    multi_shots:    True to use multi-shot mode (then pass multi_prompt array).
    multi_prompt:   list of {"prompt": "...", "duration": N} dicts for multi-shot.
    """
    payload_input = {
        "prompt": prompt,
        "duration": str(duration),
        "aspect_ratio": aspect_ratio,
        "mode": mode,
        "sound": sound,
        "multi_shots": multi_shots,
    }
    if image_urls:
        payload_input["image_urls"] = image_urls
    if kling_elements:
        payload_input["kling_elements"] = kling_elements
    if multi_prompt:
        payload_input["multi_prompt"] = multi_prompt
    payload = {"model": "kling-3.0/video", "input": payload_input}
    r = requests.post(JOBS_CREATE, headers=HEADERS, json=payload)
    body = r.json()
    task_id = (body.get("data") or {}).get("taskId")
    if not task_id:
        raise RuntimeError(f"Kling create failed: {body}")
    print(f"  Kling taskId: {task_id}", flush=True)
    return _poll_jobs(task_id, "Kling")


def generate_veo(prompt, aspect_ratio="9:16", image_urls=None, mode=None, model="veo3_fast", resolution="720p"):
    """Veo on KIE. Uses /api/v1/veo/generate (separate endpoint).

    model:      'veo3_lite' = Veo 3.1 Lite (DEFAULT for this project per memory rule)
                'veo3_fast' = Veo 3.1 Fast (fallback only)
                'veo3'      = Veo 3.1 Quality (NEVER use — project rule)
                — pass the exact model id KIE expects.
    resolution: '720p' (default) | '1080p' | '4k'
    mode:       'IMAGE_2_VIDEO' = image_urls[0] as literal first frame (legacy Veo 3).
                'FIRST_AND_LAST_FRAMES_2_VIDEO' = anchor mode for Veo 3.1 (pass anchor twice).
                'REFERENCE_2_VIDEO' = images as style/subject ref.
                Default: TEXT_2_VIDEO if no images, REFERENCE_2_VIDEO if images.
    """
    payload = {
        "prompt": prompt,
        "model": model,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
    }
    if image_urls:
        payload["imageUrls"] = image_urls
        payload["generationType"] = mode or "REFERENCE_2_VIDEO"
    else:
        payload["generationType"] = "TEXT_2_VIDEO"
    r = requests.post(VEO_CREATE, headers=HEADERS, json=payload)
    body = r.json()
    task_id = (body.get("data") or {}).get("taskId")
    if not task_id:
        raise RuntimeError(f"Veo create failed: {body}")
    print(f"  Veo taskId: {task_id}", flush=True)
    return _poll_veo(task_id, "Veo")


# ─── Image generators ────────────────────────────────────────────────

def generate_gpt_image(prompt, image_urls=None, aspect_ratio="auto", resolution="2K"):
    """GPT Image 2. If image_urls given → image-to-image; else → text-to-image.
    aspect_ratio: auto | 1:1 | 9:16 | 16:9 | 4:3 | 3:4
    resolution:   1K | 2K | 4K  (1:1 can't be 4K; auto/unspecified → 1K only)
    """
    if image_urls:
        model = "gpt-image-2-image-to-image"
        payload_input = {"prompt": prompt, "image_urls": image_urls, "aspect_ratio": aspect_ratio, "resolution": resolution}
    else:
        model = "gpt-image-2-text-to-image"
        payload_input = {"prompt": prompt, "aspect_ratio": aspect_ratio, "resolution": resolution}
    payload = {"model": model, "input": payload_input}
    r = requests.post(JOBS_CREATE, headers=HEADERS, json=payload)
    body = r.json()
    task_id = (body.get("data") or {}).get("taskId")
    if not task_id:
        raise RuntimeError(f"GPT Image create failed: {body}")
    print(f"  GPT Image taskId: {task_id}", flush=True)
    return _poll_jobs(task_id, "GPTImage2")


def generate_nano_banana(prompt, image_urls=None, aspect_ratio=None):
    """Nano Banana 2 (Gemini 3.1 Flash Image). Pass image_urls for edit/composition.
    aspect_ratio: optional (e.g. "9:16") — passed through to the API when set."""
    payload_input = {"prompt": prompt}
    if image_urls:
        payload_input["image_urls"] = image_urls
    if aspect_ratio:
        payload_input["aspect_ratio"] = aspect_ratio
    payload = {"model": "nano-banana-2", "input": payload_input}
    r = requests.post(JOBS_CREATE, headers=HEADERS, json=payload)
    body = r.json()
    task_id = (body.get("data") or {}).get("taskId")
    if not task_id:
        raise RuntimeError(f"Nano Banana create failed: {body}")
    print(f"  NanoBanana taskId: {task_id}", flush=True)
    return _poll_jobs(task_id, "NanoBanana2")
