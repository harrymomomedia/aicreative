"""Batch 4 — 10 MORE social-proof image ads for the CA women's-prison campaign in the comment /
chat / forum style that's performing (per user, 2026-06-26). HARD CONSTRAINT: NO Facebook logo,
NO Facebook branding, must NOT look like Facebook — generic unbranded comment threads, chat
bubbles, and Reddit-style forum posts (no real Reddit/Apple/WhatsApp/Messenger logos either).
ALL gpt-image-2 (KIE, 2K, 1:1). Black + Latina avatars, "significant potential compensation",
"sexually abused" explicit, no owed/paid/settlement. Disclaimer added in a later bar pass.

  python scripts/ccwf_social10.py            # generate all (skip-if-exists)
  python scripts/ccwf_social10.py --only s04_groupchat,s10_reviews
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, download as kie_download

OUT = Path("outputs/ccwf_women/social10")
TEXTRULE = (" Render every quoted line of text EXACTLY as written, spelled perfectly and clearly "
            "legible. NO other text, words, or letters anywhere in the image.")
UI = (" Realistic clean modern mobile UI screenshot styling, crisp legible system sans-serif text, "
      "rounded message/comment bubbles, simple round profile avatars of ordinary Black or Latina "
      "women with real everyday faces, no glamour.")
DEBRAND = (" IMPORTANT: do NOT include the Facebook logo, the Facebook name, the blue Facebook header, "
           "like/share/comment chrome, the Reddit logo or wordmark, or any Apple, iMessage, WhatsApp, "
           "or Messenger logos or app names. It must be a GENERIC, neutral, UNBRANDED interface that "
           "does NOT look like Facebook — no recognizable platform branding or logos anywhere.")

CONCEPTS = [
    ("s01_reddit_valley",
     "A realistic forum-thread screenshot on a clean white background, Reddit-style discussion but "
     "with NO Reddit logo or wordmark. A subreddit-style label at top: 'r/Ex_Inmates'. A bold post "
     "title: 'Anyone else abused by a guard at Valley State?'. Upvote and downvote arrows with a "
     "count '274' on the left. Below, a top reply in an indented box from user 'still_here_92': "
     "'You're not alone. If a staff member sexually abused you at a California women's prison, you "
     "may qualify for significant potential compensation. No police report needed, and it's "
     "completely confidential.'" + UI + DEBRAND + TEXTRULE),

    ("s02_reddit_90s",
     "A realistic forum-thread screenshot on white, Reddit-style but with NO Reddit logo or "
     "branding. A subreddit-style label: 'r/AskLegal'. A bold post title: 'It happened in the 90s "
     "at CIW Chino. Is it too late?'. Upvote arrows with a count '188'. A top reply from "
     "'paralegal_help': 'It's not too late — there is no deadline. If a staff member sexually "
     "abused you in a California women's prison, you may qualify for significant potential "
     "compensation. It's free and confidential.'" + UI + DEBRAND + TEXTRULE),

    ("s03_forum_thread",
     "A realistic online support-forum thread on a soft grey-white background, a generic discussion "
     "board. A thread title at top: 'Coming forward after all these years'. Below it three short "
     "stacked replies, each with a small round avatar of an ordinary woman and a username: 'I "
     "finally did it last month. It was free and totally private.', 'Same. I thought no one would "
     "believe me.', and a highlighted info reply: 'Survivors of staff sexual abuse in California "
     "women's prisons may qualify for significant potential compensation.'" + UI + DEBRAND + TEXTRULE),

    ("s04_groupchat",
     "A realistic group-chat screenshot with grey incoming and blue outgoing message bubbles, a "
     "generic messaging app. A group title at the top: 'The Girls'. Messages in order from "
     "different people: 'did you guys see this?', 'about Chowchilla?', 'ya — if a guard did "
     "something to you in there, you might qualify. it's free to check', 'omg. I need to look into "
     "this.'. A small caption bar at the very bottom: 'Survivors may qualify for significant "
     "potential compensation.'" + UI + DEBRAND + TEXTRULE),

    ("s05_text_dm",
     "A realistic one-on-one text-message conversation with grey incoming and blue outgoing "
     "bubbles, a generic phone messaging screen. Messages in order: 'hey... I think this is about "
     "what happened to you at Chino', 'what is it', 'women who were sexually abused by staff in "
     "there are getting help now. it's confidential. you may qualify.'. A small caption bar at the "
     "bottom: 'Survivors may qualify for significant potential compensation.'" + UI + DEBRAND + TEXTRULE),

    ("s06_comments_notalone",
     "A realistic online comment thread on a clean white background, a generic community comment "
     "section. A small caption at the top: 'You are not alone.'. Below it three comments, each with "
     "a small round profile photo of an ordinary Black or Latina woman and a first name: 'Happened "
     "to me at Folsom. I never said a word.', 'Me too. Chowchilla, years ago.', 'I didn't know I "
     "could do anything about it.'. A pinned reply at the bottom in slightly bolder text: "
     "'Survivors may qualify for significant potential compensation — free and confidential.'"
     + UI + DEBRAND + TEXTRULE),

    ("s07_comments_privacy",
     "A realistic generic comment thread on white. A bold question at the top: 'Will anyone find "
     "out?'. Two comments with small round avatars of ordinary women: 'I was scared to even check. "
     "No one in my life ever knew.', 'It's completely private — that's why I finally did it.'. A "
     "pinned reply at the bottom in bolder text: 'It's 100% confidential. Survivors may qualify "
     "for significant potential compensation.'" + UI + DEBRAND + TEXTRULE),

    ("s08_advocate_dm",
     "A realistic one-on-one direct-message screen, a generic messaging interface. The conversation "
     "is from a contact named 'Survivor Support': 'Hi — I saw your comment. If a staff member "
     "sexually abused you while you were in a California women's prison, you may qualify for "
     "significant potential compensation. It's free, confidential, and takes about two minutes to "
     "check.'. A small grey reply bubble below: 'thank you... I didn't know.'" + UI + DEBRAND + TEXTRULE),

    ("s09_comments_toolate",
     "A realistic generic comment thread on white. A bold caption at the top: 'I thought it was too "
     "late.'. Two comments with small round avatars of ordinary Black or Latina women: 'It was over "
     "twenty years ago for me. It still counted.', 'There's no deadline — I almost didn't check.'. "
     "A pinned reply at the bottom in bolder text: 'Survivors may qualify for significant potential "
     "compensation — even decades later.'" + UI + DEBRAND + TEXTRULE),

    ("s10_reviews",
     "A realistic stack of short review-style comments on a clean white background, a generic "
     "review list. Each comment has a row of five gold stars, a short line of text, and an initial: "
     "'Finally felt heard. Free and private, just like they said. — A.', 'I was terrified to check. "
     "No one ever found out. — M.', 'I didn't think anything could be done after all these years. "
     "— R.'. A small line at the bottom: 'Survivors of staff sexual abuse in California women's "
     "prisons may qualify for significant potential compensation.'" + UI + DEBRAND + TEXTRULE),
]


def gen(slug, prompt):
    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / f"{slug}.png"
    if dst.exists():
        return f"skip {slug}"
    try:
        res = generate_gpt_image(prompt, aspect_ratio="1:1", resolution="2K")
        urls = res.get("urls") or []
        if not urls:
            return f"FAIL {slug}: {res.get('status')} {str(res.get('raw'))[:160]}"
        kie_download(urls[0], str(dst))
        return f"ok {slug}"
    except Exception as e:
        return f"ERR {slug}: {e}"


if __name__ == "__main__":
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    todo = [(s, p) for s, p in CONCEPTS if (only is None or s in only)]
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(gen, s, p) for s, p in todo]
        for f in as_completed(futs):
            print(f.result(), flush=True)
    print(f"DONE — {len(todo)} concepts → {OUT}", flush=True)
