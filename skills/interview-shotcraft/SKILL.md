---
name: interview-shotcraft
description: Design and produce podcast, field-interview, street-interview, reporter-and-subject, and two-person conversation videos using memorable alternative shot recipes. Call name ShotCraft. Use for true two-shot generation, one-speaker-at-a-time interview clips, a shared horizontal master cropped into matching vertical singles, active-speaker punch-ins from landscape footage, interviewer/reaction cutaways, eyeline continuity, microphone continuity, or choosing the safest interview architecture before generation.
---

# Interview Shotcraft

Choose the shot architecture before generating dialogue. Load `ai-video-generation` for generated
media, `video-post-production` for assembly and QA, and `podcast-video` for podcast performance.

## Recipe Selector

| Recipe | Literal pattern | Best when | Main risk |
|---|---|---|---|
| **PodSolo** | One podcast guest or host | Intimate monologue or audience-facing podcast read | Can feel like an ad read |
| **DuoLock** | True two-person generated shot | Shared interaction and visible reactions matter | Cross-talk, mouth leakage, identity drift |
| **WideSplit** | One approved landscape composition cropped into matched solo anchors | Both people must share one believable world but should animate separately | Static or soft crops from a weak master |
| **StreetPunch** | One landscape video master cut into vertical active-speaker punch-ins | Existing horizontal interview already contains the full performance | Insufficient source resolution or bad crop timing |
| **SoloRelay** | Independently generated single-person angles in one scene grammar | Long dialogue, strict voice control, or repeated two-shot failures | Eyelines and backgrounds can stop matching |

Read [recipes.md](references/recipes.md) before choosing between `DuoLock`, `WideSplit`, and
`SoloRelay`. Read [vertical-reframing.md](references/vertical-reframing.md) for `StreetPunch`.

## Production Workflow

1. **Map the conversation**
   - Mark who speaks, who reacts, question/answer boundaries, and moments that require both people.
   - Decide whether the final needs real shared interaction or only the appearance of one location.

2. **Choose by failure tolerance**
   - Start with `DuoLock` only when a short shared shot materially improves the concept.
   - Prefer `WideSplit` or `SoloRelay` for long legal/medical dialogue, strict transcripts, or
     models that cannot keep a silent listener silent.
   - Use `StreetPunch` when the landscape master is already accepted and has enough resolution.

3. **Approve the visual system**
   - Show the two-shot master or every solo anchor before animation.
   - Lock left/right positions, gaze direction, lens height, background landmarks, wardrobe, mic
     ownership, and source resolution.
   - Treat approved images as visual truth; generation prompts describe performance and intentional
     camera behavior only.

4. **Generate or reframe**
   - Keep one audible speaker per generated clip unless the chosen model has passed a two-speaker
     pilot.
   - Preserve native playback speed.
   - For `StreetPunch`, use `scripts/reframe_interview.py` with contiguous frame boundaries and
     fixed per-shot crops.

5. **Assemble**
   - Cut on complete thoughts, reaction beats, or intentional overlaps.
   - Use a brief wide reset when spatial orientation would otherwise become confusing.
   - Keep crop changes as cuts unless a motivated camera move is requested.
   - Route finishing through `video-post-production`.

6. **Verify**
   - Check speaker-mouth attribution, silent-listener mouth leakage, identity, voice, eyelines,
     mic direction, handedness, background continuity, crop sharpness, and every cut boundary.
   - Reject one-frame flashes, accidental jump zooms, clipped faces, and crops that leave the active
     speaker looking out of frame.

7. **Promote learnings**
   - Run `video-skillforge` after a validated new interview route, failure mode, or user correction.
   - Add a recipe variant when conditions differ; do not overwrite all interview work with the
     newest successful method.

## Hard Rules

- Do not ask a generated silent listener to perform complex gestures while another person speaks.
- Do not hide multi-character identity drift with crop changes.
- Do not derive a portrait crop that cannot support the delivery resolution without unacceptable
  upscaling.
- Do not let campaign names, dialogue, or legal rules enter this format skill.
