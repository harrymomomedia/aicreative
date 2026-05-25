"""Stage 2b: clips 2+ for the 4 rebuilt videos (no headphones), from fresh clean anchors.
agepower + barbershop (re-roll 2-5), #3 thousand_h01 + #8 scalemoney_h05 (new 2-4, kid/sexual split).
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.jdc_pod_reroll_nohp import submit

A = "outputs/jdc_pod_agepower_h07/anchors"
B = "outputs/jdc_pod_barbershop_h08/anchors"
T = "outputs/jdc_pod_thousand_h01/anchors"
S = "outputs/jdc_pod_scalemoney_h05/anchors"

# (slug, clip, anchor, age, tone, dialogue, last, hp)
JOBS = [
    # agepower (real_07) clips 2-5 — no headphones
    ("jdc_pod_agepower_h07", "clip2", f"{A}/_anchor_0.jpg", "late 30s", "Heavy, firm.",
     "Whatever happened in there? That's on him, not you. Period.", "Period", "none"),
    ("jdc_pod_agepower_h07", "clip3", f"{A}/_anchor_1.jpg", "late 30s", "Validating, gentle.",
     "You was just a kid. None of that was on you. None of it.", "it", "none"),
    ("jdc_pod_agepower_h07", "clip4", f"{A}/_anchor_2.jpg", "late 30s", "Grounded, informational.",
     "If you was sexually abused in Illinois juvie, you may qualify for significant compensation.", "compensation", "none"),
    ("jdc_pod_agepower_h07", "clip5", f"{A}/_anchor_3.jpg", "late 30s", "Quiet push.",
     "Free, two minutes. Quit blamin' that little kid you was. Go check.", "check", "none"),
    # barbershop (real_08) clips 2-5 — no headphones
    ("jdc_pod_barbershop_h08", "clip2", f"{B}/_anchor_0.jpg", "early 30s", "Quiet, personal.",
     "He sexually abused me in there. I buried it for years.", "years", "none"),
    ("jdc_pod_barbershop_h08", "clip3", f"{B}/_anchor_1.jpg", "early 30s", "Casual.",
     "Went home, checked it. Two minutes. Nobody knew. Filed it.", "it", "none"),
    ("jdc_pod_barbershop_h08", "clip4", f"{B}/_anchor_2.jpg", "early 30s", "Real, a little surprised.",
     "Now they sayin' I may qualify for significant compensation. Nobody was in my business.", "business", "none"),
    ("jdc_pod_barbershop_h08", "clip5", f"{B}/_anchor_3.jpg", "early 30s", "Reassuring.",
     "You don't gotta say it out loud. Nowhere. Just you. Go look.", "look", "none"),
    # #3 thousand_h01 (real_01) clips 2-4 — split-safe
    ("jdc_pod_thousand_h01", "clip2", f"{T}/_anchor_0.jpg", "early 30s", "Firm, the weight of it.",
     "The staff sexually abused us. Every one of us.", "us", "none"),
    ("jdc_pod_thousand_h01", "clip3", f"{T}/_anchor_1.jpg", "early 30s", "Grounded.",
     "Illinois is payin' for what was done to us, and you may qualify for significant compensation.", "compensation", "none"),
    ("jdc_pod_thousand_h01", "clip4", f"{T}/_anchor_2.jpg", "early 30s", "Direct close.",
     "Free to check, two minutes, private. That was you in there? Add your name. Go look.", "look", "none"),
    # #8 scalemoney_h05 (real_05) clips 2-4 — split-safe
    ("jdc_pod_scalemoney_h05", "clip2", f"{S}/_anchor_0.jpg", "mid 30s", "Matter-of-fact.",
     "A staff member sexually abused you in Illinois juvie.", "juvie", "none"),
    ("jdc_pod_scalemoney_h05", "clip3", f"{S}/_anchor_1.jpg", "mid 30s", "Real-talk money.",
     "You may qualify for significant compensation. The kind of money that change things.", "things", "none"),
    ("jdc_pod_scalemoney_h05", "clip4", f"{S}/_anchor_2.jpg", "mid 30s", "Direct close.",
     "I filed mine already. Find out private, free, two minutes. Why you still scrollin'? Go check.", "check", "none"),
]


def main():
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(submit, *j): f"{j[0]}/{j[1]}" for j in JOBS}
        for f in as_completed(futs):
            name = futs[f]
            try:
                n, status, info = f.result()
                print(f"[{n}] {status} {info}", flush=True)
            except Exception as e:
                print(f"[{name}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
