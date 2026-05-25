"""Replicate API client wrapper.

Async pattern via official `replicate` Python SDK.
Currently we use this for video matting (Robust Video Matting / RVM).

Models we care about:
  arielreplicate/robust_video_matting   — RVM, ~$0.05-0.15 per video, output green-screen / alpha-mask / foreground-mask
"""
import os
from pathlib import Path

import replicate
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not TOKEN:
    raise RuntimeError("REPLICATE_API_TOKEN not set in .env")

os.environ.setdefault("REPLICATE_API_TOKEN", TOKEN)


def run_rvm(input_video_url, output_type="green-screen"):
    """Submit to RVM, block until done. Returns the output video URL.

    output_type: 'green-screen' | 'alpha-mask' | 'foreground-mask'
    """
    model_ver = "arielreplicate/robust_video_matting:73d2128a371922d5d1abf0712a1d974be0e4e2358cc1218e4e34714767232bac"
    output = replicate.run(
        model_ver,
        input={
            "input_video": input_video_url,
            "output_type": output_type,
        },
    )
    if hasattr(output, "url"):
        return str(output.url)
    if isinstance(output, str):
        return output
    return str(output)


def upscale_image(image_path, scale=4, face_enhance=True):
    """Real-ESRGAN super-resolution — pixel SR, preserves identity (does NOT regenerate the subject).
    scale 2-4; face_enhance runs GFPGAN to restore facial detail. Returns output URL."""
    model_ver = "nightmareai/real-esrgan:f121d640bd286e1fdc67f9799164c1d5be36ff74576ee11c803ae5b665dd46aa"
    with open(image_path, "rb") as f:
        output = replicate.run(model_ver, input={"image": f, "scale": scale, "face_enhance": face_enhance})
    if hasattr(output, "url"):
        return str(output.url)
    if isinstance(output, str):
        return output
    return str(output)


def download(url, dest):
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=1 << 16):
            f.write(chunk)
    print(f"  Saved: {dest} ({Path(dest).stat().st_size // 1024}KB)", flush=True)
    return dest
