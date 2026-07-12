#!/usr/bin/env python3
"""Face-aware chin-safe crop for stacked interview panes.

Given a clip, detect the largest face and return an ffmpeg crop filter for a `pane_w x pane_h` pane
that: keeps the WHOLE face with the CHIN inside + margin, puts the eyeline in the upper third, and
makes the face a consistent share of the pane (so both stacked panes match). Import `pane_crop`.
"""
import subprocess, sys
from pathlib import Path
import cv2, numpy as np

_CASC = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def _biggest_face(clip, samples=("2","4","6")):
    """Median face box across a few sample times (robust to a bad frame)."""
    boxes = []
    for t in samples:
        subprocess.run(["ffmpeg","-y","-ss",t,"-i",str(clip),"-frames:v","1","/tmp/_fc.png"],
                       capture_output=True)
        img = cv2.imread("/tmp/_fc.png")
        if img is None: continue
        h, w = img.shape[:2]
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = _CASC.detectMultiScale(g, 1.1, 5, minSize=(int(h*0.10), int(h*0.10)))
        if len(faces): boxes.append(max(faces, key=lambda f: f[2]*f[3]))
    if not boxes: return None
    fx, fy, fw, fh = np.median(np.array(boxes), axis=0).astype(int)
    return fx, fy, fw, fh, w, h

# face should fill this share of the pane HEIGHT (Haar box ~ brow->chin); tune for CU tightness
FACE_FILL = 0.52

def pane_crop(clip, pane_w=720, pane_h=640, face_fill=FACE_FILL):
    r = _biggest_face(clip)
    if not r:
        return f"crop={pane_w}:{pane_h//1}:0:{0},scale={pane_w}:{pane_h},setsar=1,fps=30"  # fallback: no crop-ish
    fx, fy, fw, fh, W, H = r
    ar = pane_w / pane_h
    ch = int(fh / face_fill)                    # crop height so face ~FACE_FILL of pane
    cw = int(ch * ar)
    if cw > W:                                  # can't be wider than source
        cw = W; ch = int(cw / ar)
    if ch > H: ch = H; cw = int(ch * ar)
    face_cx = fx + fw/2
    face_cy = fy + fh/2
    # eyeline (~fy + 0.4*fh) should sit ~0.36 down the pane
    eyeline = fy + 0.40*fh
    cy = int(eyeline - 0.36*ch)
    cx = int(face_cx - cw/2)
    # guarantee chin (fy+fh) has >=6% margin above crop bottom
    chin = fy + fh
    if chin + 0.06*ch > cy + ch: cy = int(chin + 0.06*ch - ch)
    cx = max(0, min(cx, W - cw)); cy = max(0, min(cy, H - ch))
    return f"crop={cw}:{ch}:{cx}:{cy},scale={pane_w}:{pane_h},setsar=1,fps=30"

if __name__ == "__main__":
    for clip in sys.argv[1:]:
        print(clip, "->", pane_crop(clip))
