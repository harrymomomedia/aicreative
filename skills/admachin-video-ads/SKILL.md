---
name: admachin-video-ads
description: Create, analyze, stage, and launch performance video ads using AdSwipe and AdMachin, including hook and script development, creative variation, proof-media selection, regulated tort/legal copy, asset-library persistence, copy approval, and Facebook launch safeguards. Use for paid-social ads, UGC ad concepts, competitor swipe analysis, medical or legal lead-generation creative, AdMachin drafts, and campaign launches. Pair with video-production, ai-video-generation, and video-post-production for the underlying video craft.
---

# AdMachin Video Ads

This is the performance-ad and publishing adapter. Load `video-production` for the overall workflow, `ai-video-generation` for generated assets, and `video-post-production` for finishing and QA.

## AdSwipe Analysis

- Analyze transcript, visuals, pacing, and proof cuts together.
- Record hook, audience qualifier, problem, mechanism, proof, objections, CTA, cut frequency, host register, and B-roll function.
- Viral metrics are sparse; do not overfit to the few ads that expose performance data.
- When cloning a winner, preserve framing and beat logic as scaffolding. Rewrite the discovery mechanism, sentence rhythm, speaker logic, and exact visuals.
- Run a second dissection when the source's B-roll or transition logic is not yet mapped precisely.

## Creative Development

- Write complete 2-3 sentence openers when the user is choosing hooks.
- Make variants meaningfully different in speaker role, premise, opening logic, proof type, visual format, and CTA framing.
- Rotate direct notice, story, debate, checklist, myth-busting, advocate, family, case-worker, local-commentary, and document-led formats.
- Keep spoken copy plain: short sentences, one idea at a time, natural cadence, no legalese or caricatured slang.
- Match gaze to register: off-camera for an overheard confession/podcast; direct-to-lens for an audience-facing notice.
- Use `ad-copy-formats` when a batch needs structurally different primary text and headlines.

## Regulated Legal Copy

- State the qualifying harm explicitly. For prison/JDC campaigns, say `sexual abuse` or `sexually abused`, not only `abuse`.
- Use `may qualify`, `could be eligible`, `potential compensation`, or `significant potential compensation`.
- Never guarantee money, payouts, settlements, damages, or outcomes.
- Keep compensation close to the qualifying harm so the action is not buried.
- Address people who already have the qualifying diagnosis or injury; do not turn a tort campaign
  into future-risk or symptom-anxiety targeting.
- Prefer `private form`, `private page`, `free case review`, or `private questions`; avoid ambiguous `private check`.
- Describe contact as confidential when appropriate; never promise that nobody will call when
  follow-up contact is part of intake.
- Keep the Pulaski/Jones disclaimer verbatim by loading `pulaski-jones-disclaimer`.
- Present final headline and primary text verbatim for approval before creating AdMachin copy rows.

Campaign-specific qualification rules belong in campaign memory or `inventory/`, not this skill.

## Proof And B-Roll

- Map each source proof insert to its narrative function and emotional intensity.
- In medical/tort ads, do not replace patient, recovery, scar, diagnosis, or scan proof with calendars, folders, generic paperwork, or a weak laptop article.
- Treat article/study screens as secondary corroboration when stronger human diagnosis footage exists.
- If `list_clip_trims` returns no matches, query `list_brolls` in the source library before
  concluding that no reusable footage exists or generating a replacement.
- Reject blank or unreadable phone/computer screens.
- For Reels eligibility flows, use true 9:16 mobile states with feed-readable text. Do not reveal taps, selected answers, pressed controls, or private data unless the product demonstration explicitly requires it.
- Show every proposed host and B-roll asset individually before final assembly.

## AdMachin Asset Persistence

- Upload every approved generated B-roll asset to the correct project/subproject immediately after QA.
- Use a descriptive title, tags, and complete model/provider/prompt metadata.
- Read the record back or verify its returned ID before treating the asset as reusable.
- Never leave an approved reusable generated asset only on local disk.

## Draft And Launch Gates

1. Resolve workspace, project, subproject, page, pixel/event, URL, CTA, and source ad set from current AdMachin data.
2. Get explicit approval for final headline and primary text.
3. Upload the final captioned creative only when the campaign expects captioned delivery; verify the returned creative record.
4. Create copy and draft ads with resumable state keyed by a globally unique identifier.
5. Validate the launch plan before spending.
6. Launch only through the gated AdMachin path with explicit confirmation.
7. Generated ad sets start paused unless the user explicitly requests otherwise.
8. After any timeout, poll the server-side launch run and reconcile Facebook objects before retrying. Never blindly duplicate.

## Delivery And Memory

- Show each generated video immediately with a backticked path.
- Keep clean, captioned, and disclaimer files separate.
- Store campaign scripts, selected personas, rejected assets, AdMachin IDs, and launch results in campaign memory or `inventory/<campaign>_learnings.md`.
- Store only cross-campaign production behavior in the general video skills.
