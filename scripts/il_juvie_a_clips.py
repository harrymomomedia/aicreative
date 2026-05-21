"""Generate IL juvenile-detention survivor ad (Script A) clips via KIE Veo 3.1 Lite @ 1080p.

Persona anchor: outputs/il_juvie_a/reference/character_A_livingroom.png (Black man, early 30s).
i2v: KIE veo3_lite, FIRST_AND_LAST_FRAMES_2_VIDEO (anchor passed twice = persona lock).
Short i2v prompts per CLAUDE.md — character/setting live in the anchor, not the prompt.

Run:
  .venv/bin/python scripts/il_juvie_a_clips.py --clip 1            # one clip (test)
  .venv/bin/python scripts/il_juvie_a_clips.py --clips 1 2 3
  .venv/bin/python scripts/il_juvie_a_clips.py --all --max-workers 4
"""
import argparse
import concurrent.futures
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from kie_client import generate_veo, upload_file, download

OUT = ROOT / "outputs" / "il_juvie_a"
OUT.mkdir(parents=True, exist_ok=True)
ANCHOR_LOCAL = OUT / "reference" / "character_A_livingroom.png"

SHARED = (
    "Selfie talking-head video: the SAME man from the reference image speaking straight into "
    "his phone's front camera, in the same living room, mid-conversation with the viewer.\n"
    "GAZE: eyes stay locked on the lens, minimal blinking, no glancing away.\n"
    "BODY: weary stillness, small natural head motion, NO smile at any point.\n"
    "VOICE: adult Black man, early 30s, low-mid register, slightly gravelly, conversational — NOT an announcer.\n"
    "AUDIO: his voice only — no music, no second or narrator voice, no background chatter.\n"
    "DIALOGUE LOCK: say ONLY the line below, in order; no extra words, no fillers (uh/um/like), "
    "no trailing word; STOP after the final word.\n"
    "NO on-screen text, captions, subtitles, graphics, or watermark."
)

# (beat note, spoken dialogue)
CLIPS = [
    ("Opening confession. Heavy, reflective. Slight downward weight on 'fifteen,' then back to the lens. "
     "Unhurried ~2.2 words/sec, brief pause before 'St. Charles.' Pronounce Illinois as ILL-uh-NOY.",
     "I did time in an Illinois juvenile detention center when I was just fifteen. St. Charles."),
    ("Quiet, resigned. Looking back. Even pace.",
     "For years, I told myself that part of my life was over. That I'd moved on."),
    ("A shift — something interrupts the calm. Slightly more alert.",
     "Then my cousin sends me this article. He's like, isn't this the place they had you?"),
    ("Measured, careful with the legal line. Clear and even.",
     "Anybody who was locked up as a kid in an Illinois juvenile detention center may qualify for significant potential compensation."),
    ("Lower, harder. The hardest line — say it plainly, no flinch.",
     "For the sexual abuse the guards committed against us in there."),
    ("Recognition landing. Voice tightens. 'We were kids' said quietly.",
     "And I just sat there. Because that happened to me. It happened to a lot of us. We were kids."),
    ("Practical, matter-of-fact. Reassuring ease.",
     "There's a form. You put down when you were inside, and what happened. That's it."),
    ("Reassuring, privacy emphasis. Steady.",
     "Nobody calls your phone. Nobody shows up at your house. You just find out if you've got a case."),
    ("Light, almost a shrug. Ease.",
     "I filled mine out. Took me two minutes."),
    ("Back to weight, then permission. 'It's not' said firmly.",
     "We were just kids in there. And it's not too late. I thought it was. It's not."),
    ("Direct call to action. Clear, simple.",
     "Tap the button. See if you qualify."),
]


def build_prompt(idx):
    beat, dialogue = CLIPS[idx - 1]
    return (
        f"{SHARED}\n"
        f"BEAT: {beat}\n"
        f'SPOKEN DIALOGUE (verbatim, stop after final word): "{dialogue}"'
    )


def get_anchor_url():
    """Upload the persona anchor fresh (KIE tempfile URLs expire ~24h)."""
    cache = OUT / "persona_anchor_url.txt"
    url = upload_file(str(ANCHOR_LOCAL), filetype="image/png")
    cache.write_text(url)
    print(f"  anchor uploaded → {url}", flush=True)
    return url


def generate_one(idx, anchor_url):
    out_path = OUT / f"clip{idx}.mp4"
    if out_path.exists():
        return (idx, "exists", str(out_path))
    t0 = time.time()
    res = generate_veo(
        prompt=build_prompt(idx),
        image_urls=[anchor_url, anchor_url],  # anchor twice = FIRST_AND_LAST persona lock
        aspect_ratio="9:16",
        resolution="1080p",
        model="veo3_lite",
        mode="FIRST_AND_LAST_FRAMES_2_VIDEO",
    )
    if res["status"] != "success" or not res.get("urls"):
        return (idx, "failed", res.get("failMsg") or res.get("raw"))
    download(res["urls"][0], str(out_path))
    return (idx, "success", f"{out_path} ({round(time.time()-t0,1)}s)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", type=int, default=None)
    ap.add_argument("--clips", nargs="+", type=int, default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--max-workers", type=int, default=4)
    args = ap.parse_args()

    if args.all:
        idxs = list(range(1, len(CLIPS) + 1))
    elif args.clips:
        idxs = args.clips
    elif args.clip:
        idxs = [args.clip]
    else:
        raise SystemExit("specify --clip N, --clips N..., or --all")

    anchor_url = get_anchor_url()
    print(f"generating clip(s): {idxs}", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as ex:
        futs = {ex.submit(generate_one, i, anchor_url): i for i in idxs}
        for f in concurrent.futures.as_completed(futs):
            i = futs[f]
            try:
                print(f"  → {f.result()}", flush=True)
            except Exception as e:
                print(f"  ✗ clip {i} ERROR: {str(e)[:200]}", flush=True)


if __name__ == "__main__":
    main()
