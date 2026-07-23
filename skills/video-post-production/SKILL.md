---
name: video-post-production
description: Edit and finish videos with native-speed trimming, frame-accurate B-roll assembly, audio cleanup and loudness control, caption routing, mobile-safe layout, aspect conversion, transition inspection, and every-frame QA. Call name CutSmith. Use for stitching clips, recutting footage, adding or replacing B-roll, removing filler, mixing voices, burning subtitles, creating clean/captioned variants, or diagnosing flashes, freezes, drift, clipping, and layout problems.
---

# Video Post Production

Treat the edit as a timed visual and audio system. Make every boundary intentional and verify the rendered result, not only the timeline.

## Assembly Workflow

1. **Inventory sources**
   - Probe codec, frame rate, frame count, duration, audio sample rate, dimensions, and rotation.
   - Preserve originals and create normalized intermediates only when codec parameters differ.

2. **Build a frame timeline**
   - Choose the final frame rate first.
   - Express all cuts as integer frame boundaries.
   - Adjacent B-roll shots must share one exact boundary or have a deliberate host run between them.
   - Never leave a one- or two-frame host flash.
   - Keep generated footage at native speed; solve timing with trims, re-ordering, stronger coverage, or regeneration.
   - For landscape interview masters, keep speaker crop changes on the same frame timeline. Load
     `interview-shotcraft` and use `reframe_interview.py` for fixed vertical punch-ins.

3. **Trim speech by words**
   - Use Scribe word timestamps to cut leading/trailing improvisation.
   - Mid-sentence filler may be removed at native speed when the resulting visual jump is covered by approved B-roll.
   - Do not use B-roll to conceal identity drift.

4. **Choose proof and B-roll**
   - Match the insert's narrative function and emotional intensity.
   - Prefer specific human/action/proof footage over generic paperwork or empty screens.
   - Reject blank, unreadable, or visually indecipherable phone/computer footage.
   - For mobile form sequences, use clean 9:16 states with readable text and no exposed answer selections unless showing them is the actual product task.

5. **Mix audio**
   - Keep dialogue intelligible and consistent before adding music.
   - Use static whole-master gain when dynamic loudness normalization pumps.
   - With ffmpeg `alimiter`, set `level=disabled`; default auto makeup can undo the LUFS target.
   - Re-measure integrated LUFS and true peak on the delivered render.

6. **Route captions**
   - Use an existing named caption skill before altering a renderer.
   - Fit against actual rendered bounds, including tracking, stroke, shadow, and highlight boxes.
   - Preserve horizontal safe margins and review the longest cards.
   - Stop captions when a dense interface has no safe caption area; preserve the full source duration.

7. **Render variants**
   - Preserve separate clean, captioned, disclaimer, and aspect-ratio outputs.
   - Do not overwrite a clean master with a treatment.

8. **Run final QA**
   - Run `dissect.py <final> --every-frame --no-ocr`.
   - Run `scripts/framewise_video_qa.py`.
   - Inspect every transition before, at, and after the boundary.
   - Reject black frames, isolated flashes, frozen runs, accidental visual runs under 12 frames, clipped captions, audio clipping, and source-duration changes.

## Caption Routing

| Desired treatment | Skill |
|---|---|
| Redwood pink/red karaoke box | `redwood-subtitle` |
| Bold Hormozi/Submagic-style cards | `hormozi3` |
| Calm controlled phrase captions | `nick-subtitle` |
| Yellow text treatment | `yellow-text-sub` |
| Cinematic/VFX captions | `embedded-captions` |
| New reference style | `caption-engine-builder` |
| Regulated disclaimer | the dedicated campaign disclaimer skill |

## References

- Read [audio-finishing.md](references/audio-finishing.md) before voice replacement or final loudness work.
- Read [captions-and-mobile.md](references/captions-and-mobile.md) before captioning vertical video or interface footage.
- Read [framewise-qa.md](references/framewise-qa.md) before final delivery or when a cut feels wrong.
