---
name: video-production
description: Orchestrate any video project from brief through delivery, including reference analysis, scripting, storyboarding, asset selection, AI generation, editing, captions, audio, quality assurance, and handoff. Use for ads, UGC, talking heads, explainers, social videos, product videos, documentary edits, B-roll assemblies, motion graphics, recuts, and any request to create, improve, inspect, or finish a video. Load the specialist skills named here when their part of the workflow becomes relevant.
---

# Video Production

Use this as the primary router for video work. Keep the whole production coherent while specialist skills handle generation, post-production, captions, formats, and domain rules.

## Core Workflow

1. **Define the job**
   - Identify audience, platform, aspect ratio, duration, desired action, tone, and deliverables.
   - Distinguish source-footage editing, AI generation, motion graphics, and hybrid work.
   - For a reference clone, preserve the reference's function and pacing, not its exact creative expression.

2. **Inspect before designing**
   - Probe every source with `ffprobe`.
   - Run `dissect.py` for references or finished-video diagnosis.
   - Read transcript, scene map, representative frames, and audio measurements together.
   - Write a beat map: hook, development, proof, objections, CTA, and visual changes.

3. **Choose the production route**
   - Use the routing table below and load only the skills needed for this job.
   - Prefer existing project scripts, libraries, and approved assets over rebuilding.
   - State the model/provider, expected cost, and full generation prompt before submitting paid or generated media.

4. **Approve important creative inputs**
   - Show proposed hosts/personas before animating them.
   - Show proposed B-roll individually before final assembly when the user is curating the visual argument.
   - Use visibly different people across a multi-video batch unless reuse is explicitly approved.
   - Do not bury a weak asset inside an edit; replace it before assembly.

5. **Produce incrementally**
   - Pilot the highest-risk clip or format first.
   - Show each generated video immediately, then perform deeper QA.
   - Preserve every accepted asset and reroll only the failing unit.
   - Keep resumable task IDs and skip-if-exists behavior for provider jobs.
   - Capture each output's acceptance, rejection, defect, fix, and evidence for `video-skillforge`.

6. **Finish deliberately**
   - Edit at native playback speed.
   - Build a frame-quantized timeline.
   - Mix audio once on the assembled master.
   - Route captions through an existing named caption skill.
   - Preserve separate clean, captioned, and disclaimer versions.

7. **Verify and hand off**
   - Run transcript, identity, audio, transition, caption, and every-frame checks appropriate to the job.
   - Present the final path, duration, resolution, and QA result.
   - Run `video-skillforge`: promote reusable lessons and keep campaign facts in campaign memory.

## Skill Routing

| Need | Load |
|---|---|
| AI people, image-to-video, generated B-roll, provider choice, identity/voice continuity | `ai-video-generation` |
| Trimming, assembly, B-roll timing, audio, captions, delivery QA | `video-post-production` |
| Paid-social creative, AdSwipe, legal/tort copy, AdMachin staging or launch | `admachin-video-ads` |
| Caption styling | `redwood-subtitle`, `hormozi3`, `nick-subtitle`, `yellow-text-sub`, or `embedded-captions` |
| New caption-style cloning | `caption-engine-builder` |
| PIP or stacked proof formats | `pip-composite`, `hf-pip-composite`, or `stacked-format` |
| Existing talking-head footage recut | `talking-head-recut` |
| Podcast or interview-style creative | `podcast-video` |
| Two-person interviews, landscape-master punch-ins, matching solo angles | `interview-shotcraft` |
| Motion graphics or custom compositions | `hyperframes`, then its routed specialist |
| Product, website, PR, music, slideshow, or faceless formats | the matching specialist skill |
| Aspect conversion for feed | `feed-4x5` |
| Regulated Pulaski/Jones disclaimer | `pulaski-jones-disclaimer` |
| Promote validated production learnings into the repo | `video-skillforge` |

The installed `general-video` skill is a HyperFrames fallback, not the universal production router. Use this skill first, then route to `general-video` only for a freeform HyperFrames composition.

## Non-Negotiable Quality Rules

- Never slow, speed up, time-stretch, duplicate, freeze, or hold frames to repair a generated or edited video. Use native-speed trims or regenerate.
- Never approve image-to-video continuity from the first frame alone.
- Never use blank or unreadable screen footage.
- Never let captions exceed the mobile viewport or obscure essential interface content.
- Never allow accidental one- or two-frame flashes between visual inserts.
- Never treat a passing transcript as sufficient visual QA.
- Never auto-switch to a paid generation provider when the project has a locked unlimited route.

## References

- Read [routing-and-briefs.md](references/routing-and-briefs.md) when the request is broad or mixes several production modes.
- Read [quality-bar.md](references/quality-bar.md) before final delivery or when diagnosing why a video feels artificial.
