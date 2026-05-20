"""Finalize a Chowchilla w05 ad: Scribe QA → trim silence → loudnorm → stitch.

Per ad (E/D/A/C):
  1. ElevenLabs Scribe transcribe each clip (biased keywords) → clip{N}_transcript.json
  2. QA: compare transcript vs intended line → PASS / SOFT / FAIL (flag improvisation)
  3. trim_silence.py per clip → clip{N}_trimmed.mp4
  4. loudnorm per clip (EBU R128 I=-16) → clip{N}_norm.mp4
  5. concat-demuxer stitch → outputs/chowchilla_w05_<ad>/<ad>_final.mp4

Usage:
  .venv/bin/python scripts/chowchilla_w05_finalize.py --ads E
  .venv/bin/python scripts/chowchilla_w05_finalize.py --ads E,D,A,C
"""
import argparse, json, re, subprocess, sys, pathlib, warnings
import concurrent.futures as cf
warnings.filterwarnings("ignore")

ROOT = pathlib.Path("/Users/harry/aicreative")
sys.path.insert(0, str(ROOT))
from scripts.chowchilla_b01_ads import SCRIPTS, out_dir
from elevenlabs_client import scribe_whisper_compat

BIASED_KEYWORDS = ["Chowchilla:3.0", "CCWF:2.0"]


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def ffmpeg(args, label="ffmpeg"):
    r = subprocess.run(["ffmpeg", "-y", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{label} failed:\n{r.stderr[-1500:]}")


def norm_text(s):
    return re.sub(r"[^\w\s]", "", s.lower()).strip()


def transcribe(clip, tx_path):
    if tx_path.exists():
        return json.loads(tx_path.read_text())
    r = scribe_whisper_compat(str(clip), biased_keywords=BIASED_KEYWORDS, language_code="en")
    tx_path.write_text(json.dumps(r, indent=2, default=str))
    return r


def qa(ad):
    """Return list of {clip, status, intended, actual}."""
    res = []
    for i, intended in enumerate(SCRIPTS[ad], start=1):
        clip = out_dir(ad) / f"clip{i}.mp4"
        if not clip.exists() or clip.stat().st_size < 50_000:
            res.append({"clip": i, "status": "MISSING", "intended": intended, "actual": ""})
            continue
        tx = out_dir(ad) / f"clip{i}_transcript.json"
        actual = transcribe(clip, tx)["text"].strip()
        iw, aw = norm_text(intended).split(), norm_text(actual).split()
        j = 0
        for w in aw:
            if j < len(iw) and w == iw[j]:
                j += 1
        status = "PASS" if norm_text(actual) == norm_text(intended) else ("SOFT" if j == len(iw) else "FAIL")
        res.append({"clip": i, "status": status, "intended": intended, "actual": actual})
    return res


def _tokens(s):
    return re.sub(r"[^\w\s]", " ", s.lower()).split()


def _all_words(transcript):
    words = []
    for seg in transcript.get("segments", []):
        words.extend(seg.get("words", []))
    return words


def intended_bounds(ad, i, transcript):
    """Return (start, end) spanning the first→last INTENDED word in the transcript.
    Subsequence-matches the scripted line against transcribed words, so leading/trailing
    improvisation (Veo's added words/sounds) falls outside the window. None if no match."""
    intended = _tokens(SCRIPTS[ad][i - 1])
    words = _all_words(transcript)
    j, first_start, last_end = 0, None, None
    for w in words:
        tok = re.sub(r"[^\w]", "", w.get("word", "").lower())
        if not tok:
            continue
        if j < len(intended) and tok == intended[j]:
            if first_start is None:
                first_start = w["start"]
            last_end = w["end"]
            j += 1
    if first_start is None or last_end is None or j < len(intended):
        return None
    return first_start, last_end


def trim(ad, i, lead=0.04, tail=0.06, leadpad=0.06):
    """Word-aware trim to first→last intended word. Then prepend `leadpad` seconds of
    frozen first-frame + silence so the voice-changer has lead-in and renders the first
    word at full energy (clips that start speaking immediately, e.g. clip4's 'women' at
    0.079s, otherwise come out weak). Video is held during the silence so lip-sync holds."""
    clip = out_dir(ad) / f"clip{i}.mp4"
    tx = out_dir(ad) / f"clip{i}_transcript.json"
    trimmed = out_dir(ad) / f"clip{i}_trimmed.mp4"
    if trimmed.exists():
        return trimmed
    transcript = json.loads(tx.read_text())
    b = intended_bounds(ad, i, transcript)
    if b is None:
        words = _all_words(transcript)
        if not words:
            raise RuntimeError(f"no words for {ad} clip{i}")
        s, e = max(0.0, words[0]["start"] - lead), words[-1]["end"] + tail
    else:
        s, e = max(0.0, b[0] - lead), b[1] + tail
    lp_ms = int(leadpad * 1000)
    fc = (f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS,"
          f"tpad=start_duration={leadpad}:start_mode=clone[v];"
          f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,adelay={lp_ms}|{lp_ms}[a]")
    ffmpeg(["-i", str(clip), "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "19",
            "-c:a", "aac", "-b:a", "192k", str(trimmed)], label="trim")
    return trimmed


VOICE_ID_CACHE = ROOT / "outputs/chowchilla_black_personas/b01_voice_id.txt"


def get_voice_id():
    """Clone w05's voice once from a few clean E clips; cache the voice_id for all ads."""
    if VOICE_ID_CACHE.exists():
        return VOICE_ID_CACHE.read_text().strip()
    from elevenlabs_client import clone_voice
    srcs = []
    for i in (1, 5, 10):
        t = out_dir("E") / f"clip{i}_trimmed.mp4"
        if not t.exists():
            continue
        a = out_dir("E") / f"_clone_{i}.mp3"
        ffmpeg(["-i", str(t), "-vn", "-ar", "44100", "-ac", "1", str(a)], label="clone-extract")
        srcs.append(a)
    concat = out_dir("E") / "_clone_src.mp3"
    lst = out_dir("E") / "_clone_list.txt"
    lst.write_text("\n".join(f"file '{s.resolve()}'" for s in srcs))
    ffmpeg(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(concat)], label="clone-concat")
    lst.unlink(missing_ok=True)
    vid = clone_voice("b01_chowchilla", [str(concat)])
    VOICE_ID_CACHE.write_text(vid)
    print(f"  [CLONE] w05 voice_id={vid}", flush=True)
    return vid


def voice_change(ad, i, voice_id):
    """STS the trimmed clip's audio to the cloned w05 voice (unifies timbre, strips music).
    Remux onto the trimmed video. Returns clip{i}_vc.mp4."""
    from elevenlabs_client import voice_changer
    trimmed = out_dir(ad) / f"clip{i}_trimmed.mp4"
    vc_clip = out_dir(ad) / f"clip{i}_vc.mp4"
    if vc_clip.exists():
        return vc_clip
    src_audio = out_dir(ad) / f"clip{i}_src.mp3"
    vc_audio = out_dir(ad) / f"clip{i}_vc.mp3"
    ffmpeg(["-i", str(trimmed), "-vn", "-ar", "44100", "-ac", "1", str(src_audio)], label="vc-extract")
    voice_changer(str(src_audio), voice_id, str(vc_audio),
                  model_id="eleven_multilingual_sts_v2", stability=0.5, similarity_boost=0.85,
                  remove_background_noise=True)
    ffmpeg(["-i", str(trimmed), "-i", str(vc_audio), "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(vc_clip)], label="vc-remux")
    return vc_clip


def loudnorm(ad, i, src_suffix="trimmed"):
    src = out_dir(ad) / f"clip{i}_{src_suffix}.mp4"
    out = out_dir(ad) / f"clip{i}_norm.mp4"
    if not out.exists():
        # micro fade-in (soften word onset after the lead-pad) + fade-out (clean cut-off,
        # no abrupt chop at the seam). Positions the out-fade off the clip duration.
        pr = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                  "-of", "default=noprint_wrappers=1:nokey=1", str(src)])
        dur = float(pr.stdout.strip() or 0)
        fo = max(0.0, dur - 0.07)
        af = (f"loudnorm=I=-16:TP=-1.5:LRA=11,"
              f"afade=t=in:st=0:d=0.05,afade=t=out:st={fo:.3f}:d=0.07")
        ffmpeg(["-i", str(src), "-af", af,
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(out)], label="loudnorm")
    return out


def stitch(ad, clips):
    out = out_dir(ad) / f"{ad}_final.mp4"
    lst = out_dir(ad) / "concat.txt"
    lst.write_text("\n".join(f"file '{p.resolve()}'" for p in clips))
    ffmpeg(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)], label="concat")
    lst.unlink(missing_ok=True)
    return out


def finalize(ad, do_vc=True):
    print(f"\n=== ad {ad} ===", flush=True)
    print(f"  [QA] Scribe-transcribing {len(SCRIPTS[ad])} clips", flush=True)
    results = qa(ad)
    nmiss = sum(1 for r in results if r["status"] == "MISSING")
    nfail = sum(1 for r in results if r["status"] == "FAIL")
    for r in results:
        if r["status"] != "PASS":
            print(f"    [{r['status']}] clip {r['clip']}: intended={r['intended']!r}\n"
                  f"             actual={r['actual']!r}", flush=True)
    print(f"  [QA] {sum(1 for r in results if r['status'] in ('PASS','SOFT'))} pass/soft, "
          f"{nfail} fail, {nmiss} missing", flush=True)
    if nmiss:
        print(f"  ABORT {ad}: {nmiss} clips missing — generate them first", flush=True)
        return None, results
    n = len(SCRIPTS[ad])
    print(f"  [TRIM] {n} clips (lead/tail tightened)", flush=True)
    trimmed = [trim(ad, i) for i in range(1, n + 1)]
    if do_vc:
        voice_id = get_voice_id()
        print(f"  [VOICE-CHANGE] {n} clips → {voice_id} (unify timbre, strip music)", flush=True)
        with cf.ThreadPoolExecutor(max_workers=4) as ex:  # ElevenLabs 5-concurrent cap
            list(ex.map(lambda i: voice_change(ad, i, voice_id), range(1, n + 1)))
        src_suffix = "vc"
    else:
        src_suffix = "trimmed"
    print(f"  [LOUDNORM] {n} clips", flush=True)
    normed = [loudnorm(ad, i, src_suffix=src_suffix) for i in range(1, n + 1)]
    print(f"  [STITCH] concat {n} clips", flush=True)
    final = stitch(ad, normed)
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(final)])
    dur = float(r.stdout.strip()) if r.stdout.strip() else 0
    print(f"  → {final} ({dur:.2f}s)", flush=True)
    return final, results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ads", default="E")
    ap.add_argument("--no-voice-change", action="store_true")
    args = ap.parse_args()
    ads = [a.strip().upper() for a in args.ads.split(",") if a.strip()]
    finals = {}
    for ad in ads:
        f, _ = finalize(ad, do_vc=not args.no_voice_change)
        finals[ad] = f
    print("\n=== finals ===", flush=True)
    for ad in ads:
        print(f"  {ad}: {finals.get(ad) or 'INCOMPLETE'}", flush=True)


if __name__ == "__main__":
    main()
