---
name: podcast-video
description: Produce natural podcast-style talking-head videos and ads, including host selection, off-camera or direct-address register, script chunking, mic and set continuity, conversational reactions, generated or existing footage, proof-media cuts, jump-cut pacing, captions, and final QA. Call name PodFlow. Use when the user asks for a podcast clip, interview-style monologue, studio conversation, regular-podcast feel, video podcast ad, or a newscaster concept rewritten as a podcaster.
---

# Podcast Video

Use `video-production` for the full job, `ai-video-generation` when creating the host or clips, and `video-post-production` for the edit.
Load `interview-shotcraft` when two visible speakers, shared two-shots, or landscape-to-vertical
speaker reframing are part of the format.

## Choose The Register

- **Overheard conversation/confession:** off-camera gaze toward an implied host, conversational cadence, natural pauses.
- **Audience-facing podcast notice:** direct-to-lens gaze, firmer delivery, still conversational.
- Do not put a hype announcer script on an intimate off-camera visual.
- A microphone may be visible when it is part of the approved anchor; do not invent headphones, microphones, or studio props in later prompts.

## Build The Host

- Favor ordinary documentary realism over polished influencer portraiture unless the concept asks for polish.
- Approve the still before animation.
- Lock the mic, chair, background, wardrobe, lighting, and framing through the image rather than repeated prompt description.
- For a series, define whether one host persists or each ad intentionally gets a different host.

## Write For Speech

- Use short complete thoughts and natural transitions.
- Avoid headline-like article prose, quote-framing, em dashes, open lists, and mic-drop copy.
- Target a consistent speaking rate across chunks.
- Split only at natural thought boundaries.
- Keep regulated diagnosis, eligibility, compensation, disclaimer, and CTA phrases intact.

## Handle Reactions

- `Mm-hmm` and `yeah` can sound natural between complete thoughts.
- Filter retained reactions out of captions.
- If a reaction interrupts regulated wording or changes the claim, reroll or remove it at native speed using Scribe word timings under approved B-roll.

## Edit The Conversation

- Use jump cuts when they match the reference; avoid cutting on every clause mechanically.
- Space proof-media inserts so the host has readable runs between them.
- Match B-roll intensity to the spoken beat.
- Cover a native-speed filler removal with approved B-roll when needed, but never use coverage to hide identity drift.
- Preserve natural room tone and raw host audio when it is coherent.

## QA

- Verify transcript, voice identity, mic/set continuity, gaze, mouth, reactions, and pacing.
- Inspect the host at start/mid/end of every generated clip.
- Check every B-roll transition for accidental host flashes.
- Route captions through the selected named caption skill and keep dense interface sequences unobstructed.

## References

- Read [structure-and-pacing.md](references/structure-and-pacing.md) when adapting a reference or dividing a 30-60 second script.
- Read [host-and-audio.md](references/host-and-audio.md) when generating a presenter or correcting cross-clip voice drift.
