# AGENTS.md — aicreative

Use `/Users/harry/aicreative/CLAUDE.md` as the detailed operating manual for this project.
Use `/Users/harry/.codex/skills/admachin-video-ads/SKILL.md` as the reusable ad-production playbook.

## Persist Learnings In Three Layers

- Claude / project memory: `/Users/harry/aicreative/CLAUDE.md`
- Codex reusable skill: `/Users/harry/.codex/skills/admachin-video-ads/SKILL.md`, mirrored to `/Users/harry/aicreative/skills/admachin-video-ads/SKILL.md`
- Campaign-specific notes: `inventory/` or `outputs/<campaign>/..._learnings.md`

When the user asks to save session learnings, update the live Codex copy and the repo mirror together.

## Locked Defaults For This Repo

- STT = ElevenLabs Scribe, not Whisper.
- GPT image = `kie_client.generate_gpt_image` at 2K unless the user explicitly asks for another path.
- Veo 3.1 Fast = Poyo default; KIE `veo3_fast` is the outage fallback.
- Use clip-1 anchor rotation with eyes-open, forward-gaze frames and an explicit eye-color lock.
- If the user says a winner angle is working, preserve framing/beat structure only as scaffolding; rewrite sentence structure and discovery mechanism so variants do not sound like synonym swaps.
- For a single ad from one persona seed, prefer raw model audio plus loudness leveling. Use `voice_changer` when unifying the same persona across multiple ads or stripping music / timbre drift.
- Use descriptive slugs for approved concepts and finals, not only letters or version counters.
- Sensitive legal copy: say `sexual abuse` explicitly when needed, use `may qualify` plus `significant potential compensation`, and keep the Pulaski/Jones disclaimer verbatim.
