#!/usr/bin/env python3
"""Minimal OpusClip API client — upload a LOCAL video, caption it with a brand template
(skip the clipping pass), poll, and download the rendered result.

Flow (per https://help.opus.pro/api-reference):
  1. POST /api/upload-links {"video":{"usecase":"LocalUpload"}}      -> {url, uploadId}
  2. POST <url>  header x-goog-resumable:start, Content-Length:0     -> Location header (GCS session)
  3. PUT  <location>  Content-Type: application/octet-stream + bytes -> uploads file to GCS
  4. POST /api/clip-projects {videoUrl:uploadId, curationPref:{skipCurate:true}, brandTemplateId}
  5. GET  /api/exportable-clips?projectId=...                        -> clips[].uriForExport

Key is read from .env (OPUSCLIP_API_KEY) — never hardcoded.

CLI:
  opusclip_client.py caption <in.mp4> <brandTemplateId> <out.mp4>
  opusclip_client.py poll <projectId> [<out.mp4>]
"""
import os, sys, time, json, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("/Users/harry/aicreative/.env")
BASE = "https://api.opus.pro/api"
KEY = os.environ["OPUSCLIP_API_KEY"]
H = {"Authorization": f"Bearer {KEY}", "Accept": "application/json", "Content-Type": "application/json"}


def upload_local(path):
    """Steps 1-3: returns the uploadId to pass as videoUrl."""
    r = requests.post(f"{BASE}/upload-links", headers=H,
                      json={"video": {"usecase": "LocalUpload"}}, timeout=60)
    r.raise_for_status()
    j = r.json()
    url, upload_id = j["url"], j["uploadId"]
    print(f"  upload-link uploadId={upload_id}", flush=True)
    # init resumable session
    r2 = requests.post(url, headers={"x-goog-resumable": "start", "Content-Length": "0"}, timeout=60)
    if r2.status_code not in (200, 201):
        raise RuntimeError(f"resumable init failed {r2.status_code}: {r2.text[:300]}")
    location = r2.headers.get("Location") or r2.headers.get("location")
    if not location:
        raise RuntimeError(f"no Location header; headers={dict(r2.headers)}")
    # PUT bytes
    data = Path(path).read_bytes()
    r3 = requests.put(location, headers={"Content-Type": "application/octet-stream"}, data=data, timeout=600)
    if r3.status_code not in (200, 201):
        raise RuntimeError(f"GCS PUT failed {r3.status_code}: {r3.text[:300]}")
    print(f"  uploaded {len(data)//1024} KB -> GCS", flush=True)
    return upload_id


def create_project(video_ref, brand_template_id, skip_curate=True, aspect="portrait", title=None):
    body = {
        "videoUrl": video_ref,
        "curationPref": {"skipCurate": skip_curate, "genre": "Auto"},
        "renderPref": {"layoutAspectRatio": aspect},
        "importPref": {"sourceLang": "auto"},
        "brandTemplateId": brand_template_id,
    }
    if title:
        body["uploadedVideoAttr"] = {"title": title}
    r = requests.post(f"{BASE}/clip-projects", headers=H, json=body, timeout=120)
    print(f"  create-project HTTP {r.status_code}", flush=True)
    try:
        j = r.json()
    except Exception:
        raise RuntimeError(f"non-JSON create response: {r.text[:400]}")
    print("  create response:", json.dumps(j)[:600], flush=True)
    r.raise_for_status()
    # projectId field name not documented — probe common shapes
    pid = (j.get("projectId") or j.get("id") or j.get("project", {}).get("id")
           or j.get("data", {}).get("projectId") or j.get("data", {}).get("id"))
    return pid, j


def get_exportable(project_id):
    r = requests.get(f"{BASE}/exportable-clips", headers=H, params={"projectId": project_id}, timeout=60)
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}: {r.text[:200]}"
    return r.json(), None


def poll(project_id, out=None, every=20, timeout=1800):
    t0 = time.time()
    while time.time() - t0 < timeout:
        data, err = get_exportable(project_id)
        if err:
            print(f"  poll: {err}", flush=True)
        else:
            clips = data if isinstance(data, list) else data.get("clips") or data.get("data") or []
            if clips:
                # find an export uri
                c = clips[0]
                uri = c.get("uriForExport") or c.get("exportUrl") or c.get("videoUrl")
                status = c.get("status") or (data.get("status") if isinstance(data, dict) else None)
                print(f"  poll: {len(clips)} clip(s) status={status} export={'yes' if uri else 'no'}", flush=True)
                if uri:
                    if out:
                        Path(out).write_bytes(requests.get(uri, timeout=600).content)
                        print(f"  downloaded -> {out}", flush=True)
                    return uri
            else:
                print(f"  poll: not ready ({int(time.time()-t0)}s)", flush=True)
        time.sleep(every)
    raise TimeoutError(f"project {project_id} not done in {timeout}s")


def caption(in_path, brand_template_id, out_path):
    print(f"[opusclip] {Path(in_path).name}  template={brand_template_id}", flush=True)
    upload_id = upload_local(in_path)
    pid, _ = create_project(upload_id, brand_template_id, skip_curate=True,
                            title=Path(in_path).stem)
    print(f"  projectId={pid}", flush=True)
    if not pid:
        raise RuntimeError("could not extract projectId from create response (see above)")
    return poll(pid, out=out_path)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "caption":
        caption(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "poll":
        poll(sys.argv[2], out=sys.argv[4] if len(sys.argv) > 4 else None)
    else:
        print("usage: caption <in> <templateId> <out>  |  poll <projectId> [<out>]")
