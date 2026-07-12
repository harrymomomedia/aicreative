# Skills (backup mirror)

These are copies of the user's aicreative caption/campaign skills that should
also live in the assistant's auto-loaded skill folders. For Codex desktop
sessions, the live copy is under `~/.codex/skills/`. Mirrored here for version
control / backup. Personal or non-aicreative skills should stay live-only in
`~/.codex/skills/` unless they become repo-relevant.

| Skill | Purpose |
|---|---|
| `hormozi3` | Submagic "Hormozi 3" captions (`scripts/caption_hormozi3.py`). |
| `nick-subtitle` | Submagic "Nick" captions via the internal `scripts/caption_nick.py` renderer. |
| `pulaski-jones-disclaimer` | Verbatim Pulaski/Jones legal disclaimer text + overlay (auto "most boring window" placement). |
| `yellow-text-sub` | Per-word yellow-text captions (`scripts/caption_styled.py`). |
| `feed-4x5` | 4:5 feed crop with letterbox auto-detection (`scripts/crop_4x5.py`). |
| `admachin-video-ads` | AdSwipe/tort UGC ad analysis, scripts, Veo workflow, sensitive legal captions, and QA rules. |
| `street-interview` | Street-interview / vox-pop UGC ads — reporter with a mic stops people on the sidewalk; personas → two-shot i2i anchor → Grok/Veo back-and-forth → wide-16:9 punch-in to 9:16 → trim/assemble (Chowchilla/CCWF build). |
| `interview-scene` | Anchor-image pipeline for the seated two-person documentary/podcast interview (same-room reverse-angle chest-up heads, iPhone look, 3/4 gaze, facing-each-other flip). |
| `stacked-podcast-broll` | Full stacked documentary/podcast interview + b-roll pipeline (subject top / interviewer bottom, Grok clean talkers + silent listeners, stereo-concat rule, b-roll-over-VO, AdMachin B-Roll library). |
| `session-memory-pass` | End-of-session learning extraction: save user preferences, mistakes, rules, skills, and campaign notes without staging unrelated work. |
