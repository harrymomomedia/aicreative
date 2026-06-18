"""Yellow-marker highlights for article cards — ANIMATED-SWEEP edition (user 2026-06-10).
Outputs per card:
  cards_real/<card>.png        — CLEAN base (restored from backup, no baked strokes)
  cards_real/hl_<card>.png     — transparent overlay holding ONLY the marker strokes
The assemble script wipes the overlay left->right (page-space) before zoompan, so the
highlight draws on while the camera zooms. TITLE-ONLY strokes per user rule.
Tesseract TSV word boxes (stdin invocation; conf is FLOAT)."""
import io
import os
import re
import shutil
import subprocess

from PIL import Image, ImageDraw

CARDS_DIR = "outputs/cawp_f1_news/cards_real"
BACKUP = f"{CARDS_DIR}/backup_nohl"
os.makedirs(BACKUP, exist_ok=True)

HIGHLIGHT = (255, 230, 58, 128)

# phrases: explicit word sequences | full_lines: stroke every big-type line in the zone
TARGETS = {
    "card1_sentence.png": {"phrases": ["224 years", "sexually assaulting inmates"],
                           "y_min": 0, "y_max": 520, "min_h": 22},
    "card2_doj.png": {"full_lines": True, "y_min": 300, "y_max": 860, "min_h": 34},
    "card3_filings.png": {"phrases": ["sexual abuse by prison staff"],
                          "y_min": 0, "y_max": 430, "min_h": 22},
}


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def ocr_words(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    r = subprocess.run(["tesseract", "stdin", "-", "--psm", "3", "-l", "eng", "tsv"],
                       input=buf.getvalue(), capture_output=True)
    out = []
    for line in r.stdout.decode().splitlines()[1:]:
        p = line.split("\t")
        if len(p) < 12 or not p[11].strip():
            continue
        try:
            conf = float(p[10])
        except ValueError:
            continue
        if conf < 40:
            continue
        out.append({"line_key": (p[2], p[3], p[4]), "x": int(p[6]), "y": int(p[7]),
                    "w": int(p[8]), "h": int(p[9]), "text": p[11]})
    return out


def find_phrase(words, phrase):
    toks = [norm(t) for t in phrase.split()]
    hits = []
    for i in range(len(words) - len(toks) + 1):
        if all(norm(words[i + j]["text"]) == toks[j] for j in range(len(toks))):
            hits.append(words[i:i + len(toks)])
    return hits


def stroke_groups(d, groups, drawn):
    for grp in groups:
        x0 = min(w["x"] for w in grp) - 8
        x1 = max(w["x"] + w["w"] for w in grp) + 10
        y0 = min(w["y"] for w in grp) - 6
        y1 = max(w["y"] + w["h"] for w in grp) + 8
        d.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=HIGHLIGHT)
        drawn += 1
    return drawn


for fname, cfg in TARGETS.items():
    path = os.path.join(CARDS_DIR, fname)
    bak = os.path.join(BACKUP, fname)
    if not os.path.exists(bak):
        shutil.copy(path, bak)
    shutil.copy(bak, path)  # base = clean original, strokes go to the overlay only

    img = Image.open(path).convert("RGB")
    in_zone = [w for w in ocr_words(img)
               if cfg["y_min"] <= w["y"] <= cfg["y_max"] and w["h"] >= cfg["min_h"]]
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    n = 0
    if cfg.get("full_lines"):
        lines = {}
        for w in in_zone:
            lines.setdefault(w["line_key"], []).append(w)
        n = stroke_groups(d, lines.values(), n)
    else:
        for phrase in cfg["phrases"]:
            for seq in find_phrase(in_zone, phrase):
                by_line = {}
                for w in seq:
                    by_line.setdefault(w["line_key"], []).append(w)
                n = stroke_groups(d, by_line.values(), n)
    overlay.save(os.path.join(CARDS_DIR, f"hl_{fname}"))
    print(f"{fname}: {n} strokes -> hl_{fname} (base restored clean)")
