#!/usr/bin/env python3
"""Minimal Submagic API client — upload a LOCAL video, caption it with a Submagic template
(e.g. "Hormozi 3"), export, poll, and download the rendered result.

Flow (https://docs.submagic.co):
  1. POST /v1/projects/upload  (multipart: file, title, language, templateName, dictionary, ...)
        -> {id, status}  (project transcribes asynchronously)
  2. POST /v1/projects/{id}/export  (optional width/height/fps)  -> starts render
        (prerequisite: project must be transcribed / have words data)
  3. GET  /v1/projects/{id}  -> status in processing|transcribing|exporting|completed|failed
        when completed -> downloadUrl

Auth: header  x-api-key: sk-...   (read from .env, never hardcoded)

CLI:
  submagic_client.py templates
  submagic_client.py caption <in.mp4> <out.mp4> [templateName] [dict_csv]
"""
import os, sys, time, json, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("/Users/harry/aicreative/.env")
BASE = "https://api.submagic.co/v1"
KEY = os.environ["SUBMAGIC_API_KEY"]
AUTH = {"x-api-key": KEY}


def templates():
    return requests.get(f"{BASE}/templates", headers=AUTH, timeout=30).json()


def upload(path, title, template="Hormozi 3", language="en",
           dictionary=None, magic_zooms=False, magic_brolls=False, webhook=None):
    data = {"title": title[:100], "language": language, "templateName": template,
            "magicZooms": str(magic_zooms).lower(), "magicBrolls": str(magic_brolls).lower()}
    if dictionary:
        data["dictionary"] = json.dumps(dictionary)   # JSON-array string, max 100 items
    if webhook:
        data["webhookUrl"] = webhook
    with open(path, "rb") as fh:
        files = {"file": (Path(path).name, fh, "video/mp4")}
        r = requests.post(f"{BASE}/projects/upload", headers=AUTH, data=data, files=files, timeout=600)
    print(f"  upload HTTP {r.status_code}: {r.text[:300]}", flush=True)
    r.raise_for_status()
    j = r.json()
    return j.get("id") or j.get("projectId"), j


def get(pid):
    r = requests.get(f"{BASE}/projects/{pid}", headers=AUTH, timeout=60)
    r.raise_for_status()
    return r.json()


def export(pid, width=None, height=None, fps=None):
    body = {}
    if width:  body["width"] = width
    if height: body["height"] = height
    if fps:    body["fps"] = fps
    r = requests.post(f"{BASE}/projects/{pid}/export",
                      headers={**AUTH, "Content-Type": "application/json"}, json=body, timeout=120)
    return r.status_code, (r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text[:300]})


def caption(in_path, out_path, template="Hormozi 3", dictionary=None,
            magic_zooms=False, magic_brolls=False, every=15, timeout=1800):
    print(f"[submagic] {Path(in_path).name}  template={template!r}", flush=True)
    pid, _ = upload(in_path, Path(in_path).stem, template=template,
                    dictionary=dictionary, magic_zooms=magic_zooms, magic_brolls=magic_brolls)
    print(f"  projectId={pid}", flush=True)
    if not pid:
        raise RuntimeError("no project id in upload response")
    t0 = time.time(); exported = False
    while time.time() - t0 < timeout:
        p = get(pid); st = p.get("status")
        dl = p.get("downloadUrl")
        print(f"  status={st} download={'yes' if dl else 'no'} ({int(time.time()-t0)}s)", flush=True)
        if st == "failed":
            raise RuntimeError(f"project failed: {p.get('error') or p}")
        if st == "completed" and dl:
            Path(out_path).write_bytes(requests.get(dl, timeout=600).content)
            print(f"  DOWNLOADED -> {out_path} ({Path(out_path).stat().st_size//1024} KB)", flush=True)
            return p
        if not exported and st not in ("uploading", "exporting", "completed"):
            # transcription likely done -> trigger render. If too early, API 400s; we retry next loop.
            code, resp = export(pid)
            print(f"  export trigger HTTP {code}: {str(resp)[:200]}", flush=True)
            if code in (200, 201):
                exported = True
        time.sleep(every)
    raise TimeoutError(f"project {pid} not completed in {timeout}s")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "templates":
        print(json.dumps(templates(), indent=2))
    elif cmd == "caption":
        tmpl = sys.argv[4] if len(sys.argv) > 4 else "Hormozi 3"
        dic = sys.argv[5].split(",") if len(sys.argv) > 5 else None
        caption(sys.argv[2], sys.argv[3], template=tmpl, dictionary=dic)
    else:
        print("usage: templates | caption <in> <out> [templateName] [dict_csv]")
