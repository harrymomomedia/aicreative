"""KIE veo3_fast fallback for Chowchilla w05 ads when Poyo is in a wide outage.

Same Veo model, different infra ($0.30/clip vs Poyo $0.10). Keeps the missing clips on
the SAME 'fast' tier as the clips that already landed on Poyo (mixing in veo3_lite would
mismatch the ad's look/voice). Reuses the exact prompts + anchor-rotation mapping from
chowchilla_w05_ads.py so KIE clips are interchangeable with Poyo clips for concat.

Anchor mapping (matches phase-rest rotation): clip1 → w05.png base anchor;
clip N>1 → _anchor_{(N-2) % 6}.jpg extracted from clip1.

Usage:
  .venv/bin/python scripts/chowchilla_w05_kie_fallback.py --ad E --clips 1,4,5,6,9,10
"""
import argparse, concurrent.futures, pathlib, sys, time

ROOT = pathlib.Path("/Users/harry/aicreative")
sys.path.insert(0, str(ROOT))
import kie_client
from scripts.chowchilla_w05_ads import SCRIPTS, TONES, build_prompt, out_dir, ANCHOR_SRC

_upload_cache = {}


def kie_url_for(ad, clip_n):
    """Upload the right anchor for clip_n to KIE; cache by local path."""
    if clip_n == 1:
        local = ANCHOR_SRC
    else:
        local = out_dir(ad) / f"_anchor_{(clip_n - 2) % 6}.jpg"
    key = str(local)
    if key not in _upload_cache:
        _upload_cache[key] = kie_client.upload_file(str(local))
        print(f"  uploaded {local.name} → KIE", flush=True)
    return _upload_cache[key]


def gen_clip(ad, clip_n):
    dest = out_dir(ad) / f"clip{clip_n}.mp4"
    if dest.exists() and dest.stat().st_size > 50_000:
        print(f"[{ad}{clip_n}] skip (exists)", flush=True)
        return ad, clip_n, str(dest)
    line = SCRIPTS[ad][clip_n - 1]
    prompt = build_prompt(line, TONES[ad])
    anchor = kie_url_for(ad, clip_n)
    t0 = time.time()
    print(f"[{ad}{clip_n}] KIE submit", flush=True)
    try:
        res = kie_client.generate_veo(
            prompt, aspect_ratio="9:16", image_urls=[anchor],
            mode="IMAGE_2_VIDEO", model="veo3_fast", resolution="720p",
        )
    except Exception as e:
        print(f"[{ad}{clip_n}] EXC ({time.time()-t0:.0f}s): {e}", flush=True)
        return ad, clip_n, None
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[{ad}{clip_n}] FAIL ({time.time()-t0:.0f}s): {res.get('failMsg') or res.get('raw')}", flush=True)
        return ad, clip_n, None
    kie_client.download(res["urls"][0], str(dest))
    print(f"[{ad}{clip_n}] DONE ({time.time()-t0:.0f}s) → {dest}", flush=True)
    return ad, clip_n, str(dest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ad", required=True)
    ap.add_argument("--clips", required=True, help="comma-sep clip numbers, e.g. 1,4,5,6,9,10")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    ad = args.ad.upper()
    clips = [int(c) for c in args.clips.split(",") if c.strip()]
    # Pre-upload anchors sequentially (cache) to avoid duplicate uploads in threads.
    for c in clips:
        kie_url_for(ad, c)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(gen_clip, ad, c) for c in clips]
        for f in concurrent.futures.as_completed(futs):
            f.result()
    print("\n=== summary ===", flush=True)
    have = sorted((p.name for p in out_dir(ad).glob("clip*.mp4") if p.stat().st_size > 50_000),
                  key=lambda n: int(''.join(filter(str.isdigit, n))))
    print(f"  {ad}: {len(have)}/{len(SCRIPTS[ad])} — {have}", flush=True)


if __name__ == "__main__":
    main()
