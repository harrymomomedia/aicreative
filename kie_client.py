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

def upload_file(filepath, filetype=None):
    """Upload a local file, return a public URL valid for 3 days."""
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


def generate_kling(prompt, duration=5, aspect_ratio="9:16", image_urls=None, sound=True):
    """Kling 3.0 at std (720p). duration is a string '3'..'15'."""
    payload_input = {
        "prompt": prompt,
        "duration": str(duration),
        "aspect_ratio": aspect_ratio,
        "mode": "std",
        "sound": sound,
    }
    if image_urls:
        payload_input["image_urls"] = image_urls
    payload = {"model": "kling-3.0/video", "input": payload_input}
    r = requests.post(JOBS_CREATE, headers=HEADERS, json=payload)
    body = r.json()
    task_id = (body.get("data") or {}).get("taskId")
    if not task_id:
        raise RuntimeError(f"Kling create failed: {body}")
    print(f"  Kling taskId: {task_id}", flush=True)
    return _poll_jobs(task_id, "Kling")


def generate_veo(prompt, aspect_ratio="9:16", image_urls=None):
    """Veo 3 Fast at 720p. Uses /api/v1/veo/generate (separate endpoint).
    generationType inferred: TEXT_2_VIDEO if no images, else REFERENCE_2_VIDEO."""
    payload = {
        "prompt": prompt,
        "model": "veo3_fast",
        "aspect_ratio": aspect_ratio,
        "resolution": "720p",
    }
    if image_urls:
        payload["imageUrls"] = image_urls
        payload["generationType"] = "REFERENCE_2_VIDEO"
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


def generate_nano_banana(prompt, image_urls=None):
    """Nano Banana 2 (Gemini 3.1 Flash Image). Pass image_urls for edit/composition."""
    payload_input = {"prompt": prompt}
    if image_urls:
        payload_input["image_urls"] = image_urls
    payload = {"model": "nano-banana-2", "input": payload_input}
    r = requests.post(JOBS_CREATE, headers=HEADERS, json=payload)
    body = r.json()
    task_id = (body.get("data") or {}).get("taskId")
    if not task_id:
        raise RuntimeError(f"Nano Banana create failed: {body}")
    print(f"  NanoBanana taskId: {task_id}", flush=True)
    return _poll_jobs(task_id, "NanoBanana2")
