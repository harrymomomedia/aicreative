"""Build the final, ready-to-render emoji inventory from the VISUALLY-VERIFIED emoji list.

Input: inventory/submagic_emoji_inventory.json with each emoji's {emoji, t} (human-verified glyph +
appearance time — see inventory/EMOJI_MODEL.md for why these are eyeballed, not auto-detected).

This script (1) DISSECTS every 24fps frame to capture each emoji's REST (cx,cy), exact APPEARANCE
time, and per-frame TRAJECTORY (robust to previous-emoji lingering + late appearance), then
(2) APPLIES the placement rules so the inventory is ready to render with caption_hormozi3.py:
big horizontal sliders (>200px travel) keep their off-center keyword rest; everything else
(statics + subtle sliders) rests CENTERED; failed captures default to centered static. Vertical
placement (~16px below OUR text) is done in the renderer, so cy is not pinned here.

  python scripts/rederive_emoji.py
"""
import subprocess, json
import numpy as np
import cv2

W, H, FPS = 720, 1280, 24.0
EO = "outputs/illinois_jdc_storytime_e_b14"
SM = f"{EO}/story_e_b14_final_submagic_hormozi3.mp4"
M = f"{EO}/story_e_b14_final.mp4"


def fr(v, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", v, "-frames:v", "1",
                          "-pix_fmt", "bgr24", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw[:W * H * 3], np.uint8).reshape(H, W, 3).astype(np.int16) if len(raw) >= W * H * 3 else None


def blobs(cap, mas):
    d = np.abs(cap - mas).sum(axis=2).astype(np.uint8)
    band = d[820:1120]
    m = cv2.morphologyEx((band > 55).astype(np.uint8) * 255, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    rw = (m > 0).sum(axis=1); m[rw > 150, :] = 0
    er = rw > 150
    for dy in (-3, -2, -1, 1, 2, 3):
        m[np.roll(er, dy), :] = 0
    n, lbl, st, cen = cv2.connectedComponentsWithStats(m, 8)
    out = []
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if 22 <= w <= 120 and 22 <= h <= 120 and 0.5 < w / h < 2.2 and a / (w * h) > 0.42 and a > 500:
            out.append((int(cen[i][0]), int(cen[i][1]) + 820, a))
    return out


def per_frame(t0, t1):
    out = []
    t = t0
    while t < t1:
        cap, mas = fr(SM, t), fr(M, t)
        out.append((round(t, 3), blobs(cap, mas) if cap is not None else []))
        t += 1 / FPS
    return out


def derive(t_inv):
    frames = per_frame(t_inv - 0.45, t_inv + 1.15)
    # REST = dominant blob clustered in the late window (current emoji settled, previous gone)
    late = []
    for t, bs in frames:
        if t >= t_inv + 0.4 and bs:
            late.append(max(bs, key=lambda b: b[2]))
    if len(late) < 3:
        return None
    # cluster late blobs by position; take the largest cluster's median (rejects next-emoji at window end)
    late.sort(key=lambda b: b[0])
    cxs = [b[0] for b in late]
    med = int(np.median(cxs))
    near = [b for b in late if abs(b[0] - med) <= 45]
    rx = int(np.median([b[0] for b in near])); ry = int(np.median([b[1] for b in near]))
    # build the entrance: scan forward; keep the blob nearest rest that's within (≤280 cx, ≤55 cy)
    path = []
    for t, bs in frames:
        cand = [b for b in bs if abs(b[1] - ry) <= 55 and abs(b[0] - rx) <= 290]
        if cand:
            b = min(cand, key=lambda b: abs(b[0] - (path[-1][1] if path else rx)) +
                    abs(b[1] - (path[-1][2] if path else ry)))
            path.append((t, b[0], b[1]))
    if len(path) < 2:
        return None
    # trim to the contiguous run ending at settle (drop pre-appearance gaps / strays)
    run = [path[-1]]
    for t, x, y in reversed(path[:-1]):
        if run[0][0] - t <= 3.5 / FPS and abs(x - run[0][1]) <= 70 and abs(y - run[0][2]) <= 45:
            run.insert(0, (t, x, y))
        else:
            break
    appear = run[0][0]
    traj = [[round(t - appear, 3), x - rx, y - ry] for t, x, y in run]
    # drop the long held tail
    clean = []
    for k in traj:
        clean.append(k)
        if abs(k[1]) <= 4 and abs(k[2]) <= 4 and len(clean) > 1:
            break
    return {"rest": [rx, ry], "appear": round(appear, 3), "traj": clean}


if __name__ == "__main__":
    inv = json.load(open("inventory/submagic_emoji_inventory.json"))
    for e in inv["emojis"]:
        r = derive(e["t"])
        if not r:
            print(f"{e['emoji']} t={e['t']:.2f}  FAILED"); continue
        rx, ry = r["rest"]; tr = r["traj"]; s = tr[0]
        e["cx"] = rx                              # raw capture; placement rules (below) finalize cx/motion
        e["_appear"] = r["appear"]
        e.setdefault("motion", {})["traj"] = tr   # full captured trajectory (offsets from rest)
        mag = (s[1] ** 2 + s[2] ** 2) ** 0.5
        kind = "horiz" if abs(s[1]) > abs(s[2]) * 2 else ("vert" if abs(s[2]) > abs(s[1]) * 2 else "diag")
        print(f"{e['emoji']} t={e['t']:.2f} rest=({rx},{ry}) appear={r['appear']:.2f} "
              f"(inv {e['t']:.2f}, Δ{r['appear']-e['t']:+.2f}) start=({s[1]:+d},{s[2]:+d}) "
              f"{'SLIDE '+kind if mag > 8 else 'pop'} frames={len(tr)}")
    # ---- placement rules (bake the final, ready-to-render positions into the inventory) ----
    # Submagic places an emoji under its keyword, so off-center is intentional ONLY when the emoji
    # visibly travels there. A subtle slide parked far off-center reads as a broken "off-center
    # static". So: BIG horizontal sliders (>200px travel) keep their off-center keyword rest; every
    # other emoji (statics + subtle sliders) rests CENTERED — subtle ones still slide IN, to center.
    # FAILED captures default to centered static. Vertical is handled in the renderer (~16px below
    # OUR text), so cy isn't pinned here.
    BASE = {"type": "pop", "s0": 0.45, "dur": 0.13, "peak": 1.10, "ramp": 0.55}
    CENTER_CX = 720 // 2 - 1                       # 359
    BIG_SLIDE_PX = 200                            # travel above this = obviously-moving big slider
    big_n = 0
    for e in inv["emojis"]:
        m = e.get("motion", {})
        tr = m.get("traj")
        cx = e.get("cx")
        ap = e.get("_appear")
        evt = e["t"]
        # require >=3 frames so a spurious 1-2 frame capture (caught a stray text fragment) is NOT
        # mistaken for a big slide
        big = bool(tr) and len(tr) >= 3 and abs(tr[0][1]) > BIG_SLIDE_PX
        nm = dict(BASE)
        if big:                                   # off-center keyword rest, replay the big slide
            e["cx"] = cx
            nm["traj"] = tr
            nm["slide"] = None
            big_n += 1
        else:                                     # centered; keep a subtle slide-in if present, else pop
            e["cx"] = CENTER_CX
            if tr and 8 < (tr[0][1] ** 2 + tr[0][2] ** 2) ** 0.5 < 160 and len(tr) >= 3:
                nm["traj"] = tr
                nm["slide"] = None
            else:
                nm["traj"] = None
                nm["slide"] = [0, 0]
        e["motion"] = nm
        # appearance = captured frame when reliable, else fall back to the verified inventory time
        e["_appear"] = ap if (ap is not None and abs(ap - evt) <= 0.6) else evt

    json.dump(inv, open("inventory/submagic_emoji_inventory.json", "w"), indent=2, ensure_ascii=False)
    n = len(inv["emojis"])
    print(f"\nplacement applied: {big_n} big-slider(s) off-center, {n - big_n} centered  ({n} emojis total)")
    print("wrote final cx / _appear / motion (traj) — ready to render with caption_hormozi3.py")
