"""
OpenAI image-gen client (direct, NOT via KIE).

Use this for any GPT Image work in this project. KIE's GPT Image proxy
(`kie_client.generate_gpt_image`) is deprecated — see CLAUDE.md.

Functions:
  generate_image(prompt, out_path=None, ...)  → text-to-image OR image-to-image
                                                 (image-to-image when image_paths given)

Returns: {"status": "success"|"failed", "paths": [...], "raw": {...}}
"""
import base64
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_API_KEY = os.getenv("OPENAI_API_KEY")
if not _API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in .env")

_client = OpenAI(api_key=_API_KEY)

DEFAULT_MODEL = "gpt-image-2"
VALID_SIZES = {"1024x1024", "1024x1536", "1536x1024", "auto"}


def generate_image(
    prompt,
    out_path=None,
    image_paths=None,
    model=DEFAULT_MODEL,
    size="1024x1536",
    n=1,
    quality="high",
):
    """Generate (or edit) image(s) via OpenAI's image API.

    prompt:       text prompt
    out_path:     where to save (str or Path). For n>1, becomes prefix_001.png etc.
    image_paths:  list of input image paths → triggers image-to-image (edit)
    model:        OpenAI image model name (default gpt-image-1)
    size:         "1024x1024" | "1024x1536" (portrait) | "1536x1024" (landscape) | "auto"
    n:            number of variants
    quality:      "low" | "medium" | "high" | "auto"
    """
    if size not in VALID_SIZES:
        raise ValueError(f"size must be one of {VALID_SIZES}, got {size!r}")

    try:
        if image_paths:
            files = [open(p, "rb") for p in image_paths]
            try:
                resp = _client.images.edit(
                    model=model,
                    prompt=prompt,
                    image=files if len(files) > 1 else files[0],
                    size=size,
                    n=n,
                    quality=quality,
                )
            finally:
                for f in files:
                    f.close()
        else:
            resp = _client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                n=n,
                quality=quality,
            )
    except Exception as e:
        return {"status": "failed", "paths": [], "raw": {"error": str(e)}}

    paths = []
    if out_path:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        for i, item in enumerate(resp.data):
            b64 = item.b64_json
            if not b64:
                continue
            target = out_path if n == 1 else out_path.with_name(
                f"{out_path.stem}_{i+1:03d}{out_path.suffix or '.png'}"
            )
            target.write_bytes(base64.b64decode(b64))
            paths.append(str(target))

    return {"status": "success", "paths": paths, "raw": resp.model_dump()}
