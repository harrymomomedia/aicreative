#!/usr/bin/env python3
"""Contact sheet of Depo Provera AdMachin creatives (video thumbnails), labeled with a short id,
so we can visually spot the recovery/surgery/scan b-rolls. Writes numbered thumbs + a tiled grid.
"""
import sys, subprocess, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from admachin_client import _get
from PIL import Image, ImageDraw, ImageFont

DEPO = "9cfb5b76-1dd3-4e07-b037-2dda178ac266"
OUT = Path("outputs/depo_interview/admachin_broll"); OUT.mkdir(parents=True, exist_ok=True)

r = _get("/creatives", params={"subproject_id": DEPO, "limit": 60})
items = r if isinstance(r, list) else (r.get("data") or [])
vids = [c for c in items if c.get("type") == "video"]
print(f"{len(items)} creatives, {len(vids)} videos")

manifest = []
tiles = []
for i, c in enumerate(vids):
    url = c.get("thumbnail_url") or c.get("media_url")
    if not url: continue
    p = OUT / f"thumb_{i:02d}.jpg"
    try:
        urllib.request.urlretrieve(url, p)
        im = Image.open(p).convert("RGB"); im.thumbnail((240, 420))
        canvas = Image.new("RGB", (240, 440), (20, 20, 20))
        canvas.paste(im, ((240 - im.width)//2, 0))
        d = ImageDraw.Draw(canvas)
        d.text((6, 422), f"{i:02d} {c['id'][:8]} {c.get('duration','?')}s", fill=(255, 235, 0))
        tiles.append(canvas)
        manifest.append((i, c["id"], c.get("duration"), c.get("media_url")))
    except Exception as e:
        print("skip", i, e)

# tile grid, 6 cols
cols = 6
rows = (len(tiles) + cols - 1) // cols
grid = Image.new("RGB", (cols*240, rows*440), (0, 0, 0))
for idx, t in enumerate(tiles):
    grid.paste(t, ((idx % cols)*240, (idx // cols)*440))
grid_path = OUT / "contact_sheet.jpg"
grid.save(grid_path, quality=85)
print("grid:", grid_path, grid.size)

(OUT / "manifest.txt").write_text("\n".join(f"{i}\t{cid}\t{dur}\t{url}" for i, cid, dur, url in manifest))
for m in manifest: print(m[0], m[1], m[2])
