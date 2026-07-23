---
name: ai-video-generation
description: Generate AI video clips, talking heads, personas, and B-roll with cost-aware provider routing, approved anchors, prompt discipline, identity and scene continuity, dialogue accuracy, voice consistency, and incremental QA. Call name GenLock. Use whenever a video project needs text-to-video, image-to-video, character animation, generated medical or documentary footage, provider/model selection, rerolls, or generated-asset review.
---

# AI Video Generation

Generate the smallest reliable units, prove continuity, and preserve every accepted result.

## Generation Workflow

1. **Specify the unit**
   - Define one clip's narrative function, dialogue, duration, aspect ratio, audio needs, and continuity dependencies.
   - Keep dialogue near a natural speaking rate; underfilled clips invite improvisation.

2. **Approve the anchor**
   - Show the host/persona still before animation.
   - For multi-ad batches, approve a visibly different person for every ad unless reuse is intentional.
   - Choose animation-safe framing: face and mouth visible, restrained hands, stable background, no accidental text.

3. **Choose the provider**
   - Read [providers.md](references/providers.md).
   - Calculate expected credits or cost before a batch.
   - Never change a locked provider/model without approval.

4. **Write a reference-led prompt**
   - Treat the supplied first frame as the sole visual truth.
   - Describe action, performance, voice, dialogue, camera behavior, and intentional changes only.
   - Do not restate appearance, medical details, wardrobe, room, lighting, or framing.
   - Use closed spoken sentences. Avoid em dashes, trailing colons, quote-framing, and grammatically open lists.
   - Show the full prompt and model/provider before generation.

5. **Pilot clip 1**
   - Check pronunciation, transcript, identity, setting, camera, mouth, eyes, voice, pacing, burned text, watermarks, and the last second.
   - Build later anchors from a deterministic-random set of eyes-open, forward-gaze frames from
     the accepted clip 1 when a continuous presenter is required.
   - Never recursively anchor each new clip from the previous generated clip.

6. **Generate incrementally**
   - Show each output immediately.
   - Save task IDs and prompts.
   - Reuse accepted clips; reroll only the failing clip.
   - Run sequentially when credits or provider throttles make failed batch submission costly.

7. **Run continuity QA**
   - Compare the approved anchor against start, midpoint, and end; add quarter-points for clips of 8 seconds or longer.
   - Any material face, age, skin, eye, hair, medical-detail, wardrobe, room, lighting, camera, or framing drift is an automatic reroll.
   - Never hide identity drift with B-roll, trims, captions, or convenient cuts.

8. **Run speech and voice QA**
   - Use ElevenLabs Scribe, not Whisper.
   - Canonicalize intended and heard tokens before exact-word decisions.
   - Check retained spans for inserted fillers, stutters, dropped words, repeated lines, and trailing improv.
   - Use both `scripts/audio_match.py` and `scripts/voice_consistency.py`.
   - Prefer raw model audio for one ad from one persona. Use `voice_changer` only for measured timbre drift, cross-video persona consistency, or unwanted music/room bleed.

## Hard Defaults

- Veo 3.1: useapi Google Flow unlimited, `googleflow_client.generate_veo(model="veo-3.1-lite-low-priority")`.
- GPT image: `kie_client.generate_gpt_image` at 2K.
- STT: ElevenLabs Scribe.
- Keep native playback speed throughout.
- A provider safety failure still may spend credits; preserve accepted outputs and avoid broad reruns.
- Generated reusable B-roll must retain complete model/provider/prompt metadata and be uploaded to the project's asset library when one exists.

## References

- Read [providers.md](references/providers.md) before choosing or changing a generation route.
- Read [prompt-and-continuity.md](references/prompt-and-continuity.md) for talking heads, anchor rotation, dialogue locks, and reroll criteria.
- Read [cost-and-transcript-qa.md](references/cost-and-transcript-qa.md) for resumable generation, word-span cleanup, and efficiency decisions.
