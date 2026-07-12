#!/usr/bin/env python3
"""Interview-anchor verification pass — draws alignment guides on the subject + interviewer anchors
and stacks them, so the angles/facing/background can be checked BEFORE any video is generated.

Guides drawn on each: vertical SCREEN-CENTER (red), rule-of-thirds (grey), and horizontal EYELINE
candidates (yellow) so eyeline height, framing scale, and looking-room are readable by eye. Output
is reviewed against the checklist below (gaze direction, 180 axis, camera height, lighting, walls).

Usage: interview_anchor_verify.py <subject.png> <interviewer.png> [--out montage.jpg]
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CHECKLIST = """CHECK (facing/same-room):
 A gaze: subject screen-RIGHT, interviewer screen-LEFT (opposite; not into-lens except CTA)
 A eyeline height matches across the two (yellow guides line up)
 A looking-room: each face sits on the OPPOSITE side of its gaze (space in front of the face)
 B camera height + framing scale match (head size equal, both eye-level, level horizon)
 B 180 axis: gazes converge, not both pointing the same way
 C same palette/decor, DIFFERENT walls of the SAME room (not identical, not two rooms)
 D consistent color temp/softness/exposure; coherent light direction"""

def guides(path, label):
    im = Image.open(path).convert("RGB").resize((360, 640))
    d = ImageDraw.Draw(im); w, h = im.size
    d.line([(w//2, 0), (w//2, h)], fill=(255, 40, 40), width=2)          # screen center
    for fx in (w//3, 2*w//3): d.line([(fx, 0), (fx, h)], fill=(120, 120, 120), width=1)
    for fy in (int(h*0.28), int(h*0.36), int(h*0.44)):                   # eyeline candidates
        d.line([(0, fy), (w, fy)], fill=(255, 235, 0), width=1)
        d.text((4, fy-12), f"{fy/h:.2f}", fill=(255, 235, 0))
    d.text((8, 8), label, fill=(0, 255, 255))
    return im

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("subject"); ap.add_argument("interviewer")
    ap.add_argument("--out", default="/tmp/anchor_verify.jpg")
    a = ap.parse_args()
    top = guides(a.subject, "SUBJECT (want gaze->RIGHT)")
    bot = guides(a.interviewer, "INTERVIEWER (want gaze->LEFT)")
    canvas = Image.new("RGB", (360, 1288), (0, 0, 0))
    canvas.paste(top, (0, 0)); canvas.paste(bot, (0, 648))
    canvas.save(a.out, quality=92)
    print("montage:", a.out)
    print(CHECKLIST)

if __name__ == "__main__":
    main()
