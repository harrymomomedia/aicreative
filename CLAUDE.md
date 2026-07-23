# CLAUDE.md - aicreative

This repository produces video, image, and paid-social creative. Keep this always-loaded file
limited to routing, locked defaults, approval gates, and repository safety. Detailed technique
belongs in skills; campaign facts belong in campaign memory or `inventory/`.

## Instruction Order

1. `AGENTS.md`
2. This file
3. Relevant live skills under `/Users/harry/.codex/skills/`
4. Campaign memory or `inventory/`
5. `docs/video-production-learnings-archive.md` only for historical troubleshooting

## Skill Router

| Work | Call name | Stable skill ID |
|---|---|---|
| End-to-end video planning and delivery | `VideoPilot` | `video-production` |
| Generated people, scenes, B-roll, providers, continuity | `GenLock` | `ai-video-generation` |
| Editing, audio, captions, aspect variants, final QA | `CutSmith` | `video-post-production` |
| AdSwipe, performance ads, legal/tort copy, AdMachin | `AdLaunch` | `admachin-video-ads` |
| Primary text and headline structures | `CopyDeck` | `ad-copy-formats` |
| Podcast creative | `PodFlow` | `podcast-video` |
| Two-shot, street-interview, and master reframing | `ShotCraft` | `interview-shotcraft` |
| PIP or stacked layouts | `ProofPIP`, `MotionPIP`, `ProofStack` | matching format skill |
| Caption treatment | `Redwood`, `Hormozi`, `Nick`, `YellowPop`, or `CaptionFX` | matching caption skill |
| Motion graphics | `HyperFrames` | `hyperframes` and its routed specialist |
| Classify and promote production learnings | `SkillForge` | `video-skillforge` |
| Promote, validate, commit, and push learnings | `ForgeSync` | `video-forgesync` |
| Recall or register any call name | `SkillDeck` | `video-skill-deck` |

The installed `general-video` skill is a HyperFrames fallback, not the universal router.
Resolve the full catalog and named recipes through `SkillDeck`; never rename stable skill folders
for recall. In the first working update, state the selected call names and their purpose once. When
a reusable workflow genuinely needs a new skill or recipe, assign a unique call name, register it,
and tell the user what to call it.

## Locked Defaults

- STT: ElevenLabs Scribe, never Whisper.
- GPT image: KIE `generate_gpt_image` at 2K.
- Veo 3.1: useapi Google Flow unlimited,
  `googleflow_client.generate_veo(model="veo-3.1-lite-low-priority")`.
- Never move Veo to a paid provider without explicit approval.
- Keep generated video at native playback speed. Repair timing with trims, coverage, or rerolls.
- The approved image is the sole identity and scene truth for image-to-video.
- Build continuation anchors only from clean, eyes-open frames of accepted clip 1.
- Use named caption skills and run framewise final QA before delivery.

Provider details and exceptions live in `ai-video-generation/references/providers.md`.

## Approval And Delivery Gates

- Show the provider, model, full prompt, and expected cost before generated-media submission.
- Show host/persona stills before animation.
- Show proposed B-roll individually when the user is curating assets.
- Use a visibly different approved person for every ad in a batch unless reuse is approved.
- Show each generated video immediately.
- Upload approved generated B-roll to the project library with full generation metadata.
- Present final ad headline and primary text verbatim before AdMachin staging.
- AdMachin launch actions spend money: validate, require explicit confirmation, and reconcile
  server-side state after timeouts before retrying.

Detailed generation, editing, caption, legal-copy, and QA criteria are owned by the routed skills.

## Memory Discipline

- `AGENTS.md`: routing and repository behavior only.
- `CLAUDE.md`: always-on project defaults only.
- Skills: reusable cross-campaign techniques.
- Active Claude memory: concise campaign state, compliance, IDs, approved assets, and rejects only.
- `inventory/`: versioned campaign research, copy, taxonomies, and detailed learnings.
- Historical or superseded material: archives outside auto-loaded memory.

Search before adding. Replace superseded rules instead of appending. Avoid duplicate prose across
layers and never create a standalone memory file for a reusable correction.

## Git Safety

- Multiple sessions may share the worktree and index.
- Recheck branch and status immediately before staging, pulling, committing, and pushing.
- Never revert changes from another session.
- Secret-scan the exact staged patch before pushing.
- Commit only intended paths unless the user explicitly requests a complete repository sync.
