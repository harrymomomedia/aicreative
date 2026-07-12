"""veo_clip_qa.py — ONE solid per-clip QA gate for generated talking-head / interview Veo clips.

Consolidates every check that has bitten this project so a single call decides ship / trim / reroll
and (crucially) says WHY. Import `qa_clip(...)` from a finalize script, or run as a CLI on a file.

Checks (each returns pass/fail + detail):
  1. transcript   — intended line present? (canonicalized, tightest-span subsequence -> recall)
  2. improv       — off-screen / invented words? (mid-span extra words + total-vs-expected ratio)
  3. voice_gender — female persona rendered with a MALE voice? (F0 fraction < 160 Hz)
  4. two_voice    — a 2nd speaker slipped in? (bimodal F0: real low mass AND real high mass)
  5. pronoun      — required proper nouns present & not mangled (e.g. Chowchilla != Chauchilla)
  6. coverage     — is the clip UNDERFILLED? (voiced time / clip time; low => Veo improv risk)
  7. burned_text  — Veo hallucinated on-screen subtitles? (optional OCR, needs tesseract)

Returns a dict: {ok, action, recall, male_frac, extra, coverage, span:(s,e), fails:[...], detail:{}}
  action in {accept, trim, reroll, reroll_shorter}  — what the caller should do.

Design notes baked in from hard-won lessons (see CLAUDE.md):
  - Canonicalize BOTH sides (strip apostrophes/hyphens WITHIN tokens; fold number-words<->digits)
    or contractions ("didn't") and amounts ("eleven"->"11") false-reject a correct take.
  - Tolerate a Scribe-garbled leading/trailing expected word ("Shame"->"deshame").
  - Median F0 hides a male SEGMENT; use the FRACTION below 160 Hz, not the median.
"""
import subprocess, re, tempfile, os, sys, json

# ---------- transcript canonicalization ----------
NUMS = {"11": "eleven", "31": "thirtyone", "2": "two", "6": "six", "eleven": "eleven",
        "thirtyone": "thirtyone", "two": "two", "six": "six", "one": "one", "1": "one"}
def _canon(t): return NUMS.get(t, t)
def _clean(t): return re.sub(r"[^a-z0-9]", "", t.lower())
def toks(s):
    return [c for c in (_canon(_clean(w)) for w in s.split()) if c]

def tight_span(exp, trans):
    """(i, j, matched) window in trans best matching exp as ordered subsequence; trims leading/mid/
    trailing improv; tolerates up to 2 garbled leading expected words. Max matched, then tightest."""
    best = None
    for off in range(0, min(3, len(exp))):
        e0 = exp[off]
        for start in range(len(trans)):
            if trans[start] != e0: continue
            ei, j, last = off, start, start
            while j < len(trans) and ei < len(exp):
                if trans[j] == exp[ei]: ei += 1; last = j
                j += 1
            matched = ei - off
            if matched > 0:
                span_len = last - start
                if best is None or matched > best[3] or (matched == best[3] and span_len < best[2]):
                    best = (start, last, span_len, matched)
    return None if best is None else (best[0], best[1], best[3])

# ---------- audio / pitch ----------
def _load_mono(mp4, sr=16000):
    import librosa
    wav = tempfile.mktemp(suffix=".wav")
    subprocess.run(["ffmpeg", "-y", "-i", mp4, "-ac", "1", "-ar", str(sr), wav], capture_output=True)
    try:
        y, _ = librosa.load(wav, sr=sr)
    finally:
        try: os.remove(wav)
        except OSError: pass
    return y, sr

def pitch_profile(mp4):
    """Return dict with male_frac (<160Hz), high_frac (>190Hz), voiced_secs, bimodal flag."""
    try:
        import numpy as np, librosa
    except Exception:
        return {"male_frac": 0.0, "high_frac": 0.0, "voiced_secs": 0.0, "bimodal": False}
    y, sr = _load_mono(mp4)
    f0, _, _ = librosa.pyin(y, fmin=70, fmax=350, sr=sr)
    hop = 512  # librosa.pyin default frame -> ~0.032s/frame at 16k
    v = f0[~np.isnan(f0)]
    if len(v) == 0:
        return {"male_frac": 0.0, "high_frac": 0.0, "voiced_secs": 0.0, "bimodal": False}
    male = float(np.sum(v < 160) / len(v))
    high = float(np.sum(v > 190) / len(v))
    voiced_secs = float(len(v) * hop / sr)
    bimodal = male >= 0.15 and high >= 0.30   # a real low cluster AND a real high cluster = 2 voices
    return {"male_frac": male, "high_frac": high, "voiced_secs": voiced_secs, "bimodal": bimodal}

def clip_secs(mp4):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nk=1:nw=1", mp4], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except ValueError: return 0.0

# ---------- the gate ----------
def qa_clip(path, line, gender="female", proper_nouns=(), scribe_fn=None,
            recall_min=0.85, male_max=0.22, improv_max=0.30, coverage_min=0.45, ocr=False):
    """Full QA on one clip. scribe_fn(path, biased_keywords=[...]) -> {'words':[...],'text':..} .
    If scribe_fn is None, imports elevenlabs_client.scribe."""
    if scribe_fn is None:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from elevenlabs_client import scribe as scribe_fn
    fails, detail = [], {}
    res = scribe_fn(path, biased_keywords=list(proper_nouns) or ["Chowchilla"])
    ws = [w for w in res.get("words", []) if w.get("type") == "word"]
    def wt(w): return (w.get("text") or w.get("word") or "")
    if not ws:
        return {"ok": False, "action": "reroll", "recall": 0.0, "fails": ["no_speech"], "detail": {},
                "span": None, "male_frac": None, "extra": None, "coverage": 0.0}

    exp = toks(line)
    trans = [_canon(_clean(wt(w))) for w in ws]
    ts = tight_span(exp, trans)
    recall = 0.0 if ts is None else ts[2] / len(exp)
    detail["recall"] = round(recall, 2); detail["trans_words"] = len(trans)
    if recall < recall_min: fails.append(f"transcript({ts[2] if ts else 0}/{len(exp)})")

    # improv: mid-span extra words + how much longer the transcript is than the line
    extra = 0.0
    span = None
    if ts:
        i, j, matched = ts
        mid_extra = (j - i + 1) - matched                       # words inside span not in the line
        total_extra = max(0, len(trans) - matched)              # all non-line words (lead+mid+trail)
        extra = mid_extra / max(1, len(exp))
        detail["mid_improv"] = mid_extra; detail["total_extra"] = total_extra
        if extra > improv_max: fails.append(f"improv(mid={mid_extra})")
        span = (max(0.0, ws[i]["start"] - 0.05), ws[j]["end"] + 0.25)

    # voice checks
    pp = pitch_profile(path)
    detail["male_frac"] = round(pp["male_frac"], 2); detail["bimodal"] = pp["bimodal"]
    if gender == "female" and pp["male_frac"] > male_max: fails.append(f"male_voice({pp['male_frac']*100:.0f}%)")
    if pp["bimodal"]: fails.append("two_voice(bimodal)")

    # coverage / underfill
    dur = clip_secs(path)
    coverage = pp["voiced_secs"] / dur if dur else 0.0
    detail["coverage"] = round(coverage, 2); detail["clip_secs"] = round(dur, 1)
    underfilled = coverage < coverage_min

    # pronunciation of required proper nouns
    if proper_nouns:
        full = " ".join(wt(w).lower() for w in scribe_fn(path).get("words", []))
        for pn in proper_nouns:
            if pn.lower() == "chowchilla":
                if "chauch" in full or "chochil" in full: fails.append("chowchilla_mispron")
                elif "chowchill" not in full: fails.append("chowchilla_unclear")
            elif _clean(pn) not in _clean(full): fails.append(f"pron_missing({pn})")

    # optional burned-in text OCR
    if ocr:
        bt = _burned_text(path)
        detail["burned_text"] = bt
        if bt: fails.append("burned_text")

    ok = not fails
    # decide action
    if ok:
        action = "accept" if (span is None or extra <= 0.10) else "trim"
    elif underfilled and any(f.startswith(("improv", "male_voice", "two_voice")) for f in fails):
        action = "reroll_shorter"          # void -> shorten the clip duration and reroll
    else:
        action = "reroll"
    return {"ok": ok, "action": action, "recall": round(recall, 2), "male_frac": detail["male_frac"],
            "extra": round(extra, 2), "coverage": detail["coverage"], "span": span,
            "fails": fails, "detail": detail}

def _burned_text(path):
    """Return stable burned-in words (Veo hallucinated subtitles). Needs tesseract; '' if unavailable."""
    import shutil
    if not shutil.which("tesseract"): return ""
    seen = {}
    for t in (0.5, 2.0, 4.0):
        jpg = tempfile.mktemp(suffix=".jpg")
        subprocess.run(["ffmpeg", "-y", "-ss", str(t), "-i", path, "-frames:v", "1", jpg], capture_output=True)
        try: img = open(jpg, "rb").read(); os.remove(jpg)
        except OSError: continue
        ocr = subprocess.run(["tesseract", "stdin", "-", "--psm", "11", "-l", "eng", "tsv"],
                             input=img, capture_output=True)
        for ln in ocr.stdout.decode("utf-8", "ignore").splitlines()[1:]:
            p = ln.split("\t")
            if len(p) >= 12 and p[11].strip() and float(p[10] or -1) >= 60:
                w = re.sub(r"[^A-Za-z]", "", p[11]).lower()
                if len(w) >= 3: seen[w] = seen.get(w, 0) + 1
    return " ".join(w for w, c in seen.items() if c >= 2)   # stable across >=2 frames = real burn-in

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("clip"); ap.add_argument("line")
    ap.add_argument("--gender", default="female")
    ap.add_argument("--pron", nargs="*", default=[])
    ap.add_argument("--ocr", action="store_true")
    a = ap.parse_args()
    print(json.dumps(qa_clip(a.clip, a.line, gender=a.gender, proper_nouns=a.pron, ocr=a.ocr), indent=2))
