# Prompt And Continuity

## Image-To-Video Prompt

The anchor already defines identity and scene. Prompt:

- action and restrained gesture
- gaze and speaking behavior
- voice/register/pacing
- exact dialogue
- camera behavior
- intentional requested change
- no unwanted text/music when relevant

Do not repeat age, ethnicity, face, hair, eyes, skin, scars, bandages, clothing, room, furniture, lighting, or framing. Re-description invites reinterpretation.

## Dialogue

- Use closed sentences with periods and commas.
- Avoid em dashes, trailing colons, quote-framing, and open lists.
- Keep one natural thought per clip.
- Prompt pronunciation for difficult medical/product/proper names.
- Require only the supplied words, in order, then stop.

## Anchor Rotation

After clip 1 passes, extract several eyes-open, forward-gaze frames from that accepted clip:

```bash
.venv/bin/python scripts/pick_clean_anchors.py clip01.mp4 \
  --out-dir outputs/<job>/anchors \
  --n 6 \
  --strategy random \
  --seed 17
```

The deterministic random subset prevents every later clip from inheriting the same transient
expression while keeping the anchor pool auditable in `anchor_manifest.json`.

- Rotate only clean frames from approved clip 1.
- Do not recursively seed clip 3 from clip 2, clip 4 from clip 3, and so on. That compounds
  generated defects and gradually degrades identity and scene fidelity.
- Keep a minimum temporal gap between picks so the pool is not six near-identical frames.
- Review the exported anchors before generation. Reject closed eyes, averted gaze, mouth
  distortion, transient hand occlusion, changed medical detail, or scene drift.
- The approved still remains the identity source of truth even when clip-1 frames are used for
  motion continuity.

### Controlled Same-Vicinity Progression

When later clips should imply that a walking presenter has moved slightly within the same area:

- Select every source frame independently from accepted clip 1.
- Create each alternate anchor as a strict single-source, background-only image edit. Preserve the
  presenter, pose, wardrobe, foreground, and camera geometry; vary only nearby surroundings,
  pedestrians, or traffic.
- Never feed one generated anchor into the next. Never use multi-reference synthesis for an
  identity-critical anchor; source competition can replace the face, age, race, or body.
- Show the complete anchor set for approval before generating later video clips.

Any identity change is an automatic rejection. Use an untouched clip-1 frame when a background
edit cannot preserve the approved person exactly.

## Identity Gate

Compare anchor versus start/mid/end, plus quarter-points for 8-second clips. Reject material changes in:

- face geometry or age
- skin or eye color
- hair
- medical details
- wardrobe
- room/furniture/lighting
- camera position/framing

Reroll the failing clip. Trimming around drift, covering it with B-roll, or freezing a frame is not a repair.
