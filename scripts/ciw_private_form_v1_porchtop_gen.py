"""CIW private-form ad v1 using persona 05c porch anchor.

Provider: useapi google-flow Veo 3.1 Lite low priority (free/no-credit).

Usage:
  .venv/bin/python scripts/ciw_private_form_v1_porchtop_gen.py clip01
  .venv/bin/python scripts/ciw_private_form_v1_porchtop_gen.py
"""
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from googleflow_client import download, generate_veo, upload_asset


SLUG = "ciw_private_form_v1_porchtop_05c"
OUT = Path("outputs") / SLUG
OUT.mkdir(parents=True, exist_ok=True)

HOST_IMG = "outputs/ciw_private_form/porchtop_anchor_variants/05c_porch_steps_wider.png"


CLIPS = [
    (
        "clip01",
        "If staff sexually abused you at C-I-W Chino or another California women's prison, you may qualify for significant potential compensation.",
        "Direct, serious hook. Warm but plain, like she is warning someone important.",
        "Stay still and centered, steady eye contact, very small head movement.",
        "Say C-I-W as the spoken letters C, I, W. Chino = CHEE-no.",
    ),
    (
        "clip02",
        "Did they touch you, threaten you, pressure you, or make you feel like you could not say no? This private page is for you.",
        "Quiet and firm, naming the problem without sounding dramatic.",
        "A tiny nod on the question, no big gestures.",
        "Natural clear American English.",
    ),
    (
        "clip03",
        "It asks a few private questions. Where were you incarcerated? Was it a guard, medical worker, or other staff?",
        "Practical, reassuring, like explaining a simple form.",
        "Calm face, phone-camera intimacy, steady posture.",
        "Natural clear American English.",
    ),
    (
        "clip04",
        "Did it happen years ago? Did fear keep you from reporting it? You do not have to post your story online.",
        "Gentle and protective, easing shame and fear.",
        "Softer eyes, slight lean toward the phone, then settles back.",
        "Natural clear American English.",
    ),
    (
        "clip05",
        "You do not have to call anybody first. Just answer the private questions and see if you may qualify.",
        "Simple, direct, no sales pitch.",
        "Still direct-to-camera, a small reassuring nod near the end.",
        "Natural clear American English.",
    ),
    (
        "clip06",
        "It is free, private, and takes about two minutes. Tap below to start.",
        "Clear call to action, calm urgency.",
        "Small final nod, serious but approachable.",
        "Natural clear American English.",
    ),
]


def last_word(text: str) -> str:
    words = re.findall(r"[A-Za-z']+", text)
    return words[-1] if words else ""


def build_prompt(line: str, tone: str, body: str, pronunciation: str) -> str:
    final_word = last_word(line)
    return f"""A fictional Latina woman in her late 50s sits on the front steps of a modest Southern California apartment building, filming a direct-to-camera phone selfie.
IDENTITY LOCK: use the start image exactly as the character reference. Same face, same grey-streaked braid, same warm olive skin, same brown eyes, same age, same denim overshirt over white tank, same natural wrinkles and lived-in skin texture.
CAMERA: vertical iPhone UGC, chest-up porch-step frame, phone at eye level, no cinematic camera moves, no zooms, no cuts.
GAZE: warm dark-brown eyes stay the SAME color throughout, open, looking into the phone lens. Natural slow blinks only.
BODY: {body} Hands and fingers stay below frame or low in her lap, never near the lens, never pointing at the camera, never covering the face.
VOICE: older Latina woman, plainspoken Southern California, serious trusted auntie/community-helper energy, not a lawyer, not a polished news anchor.
TONE: {tone}
SPEED: about 2.4 words per second, clear and conversational.
AUDIO CRITICAL: close clean phone mic audio, fully audible. No whispering, no mumbling, no background music.
PRONUNCIATION: {pronunciation}
DIALOGUE LOCK: English only. Say ONLY the words in SPOKEN DIALOGUE, in order. No fillers, no extra words, no repetition. Stop after the final word "{final_word}".
NO on-screen text, NO captions, NO subtitles, NO watermarks, NO logos.
SPOKEN DIALOGUE (verbatim, stop after final word): "{line}\""""


def duration_for(line: str) -> int:
    return 8 if len(line.split()) > 11 else 6


def gen(clip_id: str, line: str, tone: str, body: str, pronunciation: str, mgid: str):
    out = OUT / f"{clip_id}.mp4"
    prompt_path = OUT / f"{clip_id}_prompt.txt"
    prompt = build_prompt(line, tone, body, pronunciation)
    prompt_path.write_text(prompt)
    if out.exists() and out.stat().st_size > 50_000:
        return clip_id, "cached", str(out)
    print(f"=== {clip_id} duration={duration_for(line)}s ===", flush=True)
    print(line, flush=True)
    result = generate_veo(
        prompt,
        image_mgid=mgid,
        duration=duration_for(line),
        seed=1200 + (abs(hash(clip_id)) % 7000),
    )
    if result.get("status") != "success" or not result.get("urls"):
        return clip_id, "FAILED", str(result.get("raw"))[:300]
    download(result["urls"][0], str(out))
    return clip_id, "success", str(out)


def main():
    only = set(sys.argv[1:])
    clips_by_id = {clip[0]: clip for clip in CLIPS}

    host_mgid = upload_asset(HOST_IMG)
    print(f"[host] {HOST_IMG} -> {host_mgid}", flush=True)

    if only == {"clip01"} or not (OUT / "clip01.mp4").exists():
        clip = clips_by_id["clip01"]
        print(gen(*clip, host_mgid), flush=True)
        if only == {"clip01"}:
            return

    anchor_dir = OUT / "anchors"
    if not list(anchor_dir.glob("_anchor_*.jpg")):
        anchor_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                ".venv/bin/python",
                "scripts/pick_clean_anchors.py",
                str(OUT / "clip01.mp4"),
                "--out-dir",
                str(anchor_dir),
                "--n",
                "6",
                "--prefix",
                "_anchor",
            ],
            check=False,
        )
    anchor_mgids = [
        upload_asset(str(anchor), "image/jpeg")
        for anchor in sorted(anchor_dir.glob("_anchor_*.jpg"))
    ] or [host_mgid]
    print(f"[anchors] {len(anchor_mgids)} eyes-open frames", flush=True)

    rest = [clip for clip in CLIPS if clip[0] != "clip01" and (not only or clip[0] in only)]
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for index, clip in enumerate(rest):
            futures[
                executor.submit(gen, *clip, anchor_mgids[index % len(anchor_mgids)])
            ] = clip[0]
        for future in as_completed(futures):
            print(future.result(), flush=True)


if __name__ == "__main__":
    main()
