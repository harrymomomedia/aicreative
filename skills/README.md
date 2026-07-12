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
| `interview` | GENERAL cross-cutting patterns for ANY two-person interview video — speaker matching (distinct speakers + same-speaker consistency, F0/embedding thresholds, per-speaker STS), one-speaker-per-clip routing, face/identity anchoring, gaze geometry, dialogue locks, QA gates, and assembly primitives (word-anchored turn align, stereo-concat rule, static-gain loudness). The base both format skills build on. |
| `street-interview` | STREET / vox-pop UGC ads — reporter with a mic stops people on the sidewalk; personas → two-shot i2i anchor → Grok/Veo back-and-forth → wide-16:9 punch-in to 9:16 → distinct-voice swap → trim/assemble (Chowchilla/CCWF build). |
| `stacked-documentary-interview` | STACKED documentary/podcast interview + b-roll — subject TOP / documentarian BOTTOM; the 10 same-room anchor rules (reverse-angle chest-up, iPhone look, 3/4 gaze, facing-each-other flip) → Grok clean talkers + silent listeners → stacked/cut assembly (stereo-concat rule, static-gain loudness, delogo, hybrid fallback) → b-roll-over-VO → AdMachin B-Roll library (Depo build). |
| `session-memory-pass` | End-of-session learning extraction: save user preferences, mistakes, rules, skills, and campaign notes without staging unrelated work. |
